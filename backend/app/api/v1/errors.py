from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, current_app

from app.extensions import db
from app.models.error import Error
from app.models.project import Project
from app.utils.fingerprint import generate_fingerprint
from app.utils.decorators import jwt_required, admin_required

bp = Blueprint('errors_v1', __name__, url_prefix='/api/v1')


@bp.route('/errors', methods=['POST'])
def create_error():
    # 请求体大小检查
    content_length = request.content_length or 0
    max_size = current_app.config.get('MAX_ERROR_PAYLOAD_SIZE', 65536)
    if content_length > max_size:
        return jsonify({'error': 'Payload too large'}), 413

    token = request.headers.get('X-API-Token')
    if not token:
        return jsonify({'error': 'API token is required'}), 401
    project = Project.query.filter_by(api_token=token).first()
    if not project:
        return jsonify({'error': 'Invalid API token'}), 401

    # Token 封禁检查
    if project.is_disabled:
        return jsonify({'error': 'This project API token has been disabled'}), 403

    redis = current_app.redis

    # Project 维度限速
    rate_limit_key = f'rate_limit:{project.id}'
    current = redis.incr(rate_limit_key)
    if current == 1:
        redis.expire(rate_limit_key, 60)
    project_limit = current_app.config.get('RATE_LIMIT_PER_PROJECT', 60)
    if current > project_limit:
        return jsonify({'error': 'Rate limit exceeded (project)'}), 429

    # IP 维度限速
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr) or 'unknown'
    client_ip = client_ip.split(',')[0].strip()
    ip_rate_key = f'rate_limit:ip:{client_ip}'
    ip_current = redis.incr(ip_rate_key)
    if ip_current == 1:
        redis.expire(ip_rate_key, 60)
    ip_limit = current_app.config.get('RATE_LIMIT_PER_IP', 120)
    if ip_current > ip_limit:
        return jsonify({'error': 'Rate limit exceeded (ip)', 'retry_after': 60}), 429

    # 日限额
    today = datetime.now(timezone.utc).strftime('%Y%m%d')
    daily_key = f'rate_limit:daily:{project.id}:{today}'
    daily_current = redis.incr(daily_key)
    if daily_current == 1:
        redis.expire(daily_key, 86400)
    daily_limit = current_app.config.get('DAILY_ERROR_LIMIT', 10000)
    if daily_current > daily_limit:
        return jsonify({'error': 'Daily error limit exceeded', 'retry_after': 86400}), 429

    data = request.get_json()
    if not data or not data.get('exception_type') or not data.get('message'):
        return jsonify({'error': 'exception_type and message are required'}), 400

    context = data.get('context') or {}
    user = context.get('user', '')

    fingerprint = generate_fingerprint(
        data['exception_type'],
        data.get('stack_trace', ''),
        data.get('message', ''),
        data.get('source', 'backend'),
        ip=client_ip,
        user=user,
    )

    existing = Error.query.filter_by(
        project_id=project.id,
        fingerprint=fingerprint
    ).first()

    if existing:
        existing.count += 1
        existing.last_seen_at = datetime.now(timezone.utc)
        if existing.status == 'resolved':
            existing.status = 'unresolved'
        db.session.commit()
        return jsonify({
            'id': str(existing.id),
            'fingerprint': existing.fingerprint,
            'count': existing.count,
            'status': existing.status,
        }), 201

    error = Error(
        project_id=project.id,
        fingerprint=fingerprint,
        exception_type=data['exception_type'],
        message=data['message'],
        stack_trace=data.get('stack_trace'),
        severity=data.get('severity', 'error'),
        environment=data.get('environment', 'unknown'),
        source=data.get('source', 'backend'),
        ip_address=client_ip,
        context=data.get('context'),
    )
    db.session.add(error)
    db.session.commit()
    return jsonify({
        'id': str(error.id),
        'fingerprint': error.fingerprint,
        'count': error.count,
        'status': error.status,
    }), 201


@bp.route('/projects/<project_id>/errors', methods=['GET'])
@jwt_required
def list_errors(project_id, **kwargs):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)

    query = Error.query.filter_by(project_id=project_id)

    severity = [v.strip() for v in request.args.get('severity', '').split(',') if v.strip()]
    if severity:
        query = query.filter(Error.severity.in_(severity))

    environment = [v.strip() for v in request.args.get('environment', '').split(',') if v.strip()]
    if environment:
        query = query.filter(Error.environment.in_(environment))

    source = [v.strip() for v in request.args.get('source', '').split(',') if v.strip()]
    if source:
        query = query.filter(Error.source.in_(source))

    status = [v.strip() for v in request.args.get('status', '').split(',') if v.strip()]
    if status:
        query = query.filter(Error.status.in_(status))

    search = request.args.get('search')
    if search:
        query = query.filter(
            db.or_(
                Error.exception_type.ilike(f'%{search}%'),
                Error.message.ilike(f'%{search}%'),
            )
        )

    sort = request.args.get('sort', 'last_seen_at')
    if sort == 'count':
        query = query.order_by(Error.count.desc())
    elif sort == 'first_seen_at':
        query = query.order_by(Error.first_seen_at.desc())
    else:
        query = query.order_by(Error.last_seen_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    def _extract_user(ctx):
        if not ctx:
            return ''
        try:
            data = ctx if isinstance(ctx, dict) else {}
            user = data.get('user', '')
            user_name = data.get('userName', '')
            if user and user_name and user != user_name:
                return f'{user}（{user_name}）'
            return user or user_name
        except Exception:
            return ''

    return jsonify({
        'items': [
            {
                'id': str(e.id),
                'exception_type': e.exception_type,
                'message': e.message,
                'severity': e.severity,
                'environment': e.environment,
                'source': e.source,
                'ip_address': e.ip_address,
                'count': e.count,
                'status': e.status,
                'first_seen_at': e.first_seen_at.isoformat(),
                'last_seen_at': e.last_seen_at.isoformat(),
                'user': _extract_user(e.context),
            }
            for e in pagination.items
        ],
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages,
    })


@bp.route('/errors/<error_id>', methods=['GET'])
@jwt_required
def get_error(error_id, **kwargs):
    error = Error.query.get(error_id)
    if not error:
        return jsonify({'error': 'Error not found'}), 404
    return jsonify({
        'id': str(error.id),
        'project_id': str(error.project_id),
        'fingerprint': error.fingerprint,
        'exception_type': error.exception_type,
        'message': error.message,
        'stack_trace': error.stack_trace,
        'severity': error.severity,
        'environment': error.environment,
        'source': error.source,
        'ip_address': error.ip_address,
        'context': error.context,
        'count': error.count,
        'status': error.status,
        'first_seen_at': error.first_seen_at.isoformat(),
        'last_seen_at': error.last_seen_at.isoformat(),
    })


@bp.route('/errors/<error_id>', methods=['PUT'])
@admin_required
def update_error(error_id, **kwargs):
    error = Error.query.get(error_id)
    if not error:
        return jsonify({'error': 'Error not found'}), 404
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'error': 'Status field is required'}), 400
    if data['status'] not in ('unresolved', 'resolved', 'ignored'):
        return jsonify({'error': 'Invalid status value'}), 400
    error.status = data['status']
    db.session.commit()
    return jsonify({
        'id': str(error.id),
        'status': error.status,
    })


@bp.route('/errors/<error_id>', methods=['DELETE'])
@admin_required
def delete_error(error_id, **kwargs):
    error = Error.query.get(error_id)
    if not error:
        return jsonify({'error': 'Error not found'}), 404
    db.session.delete(error)
    db.session.commit()
    return '', 204


@bp.route('/errors/batch', methods=['DELETE'])
@admin_required
def batch_delete_errors(**kwargs):
    data = request.get_json()
    if not data or 'ids' not in data or not isinstance(data['ids'], list):
        return jsonify({'error': 'ids array is required'}), 400
    ids = data['ids']
    if not ids:
        return jsonify({'deleted': 0}), 200
    errors = Error.query.filter(Error.id.in_(ids)).all()
    count = len(errors)
    for error in errors:
        db.session.delete(error)
    db.session.commit()
    return jsonify({'deleted': count}), 200


@bp.route('/projects/<project_id>/errors/stats', methods=['GET'])
@jwt_required
def error_stats(project_id, **kwargs):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    severity_stats = (
        db.session.query(Error.severity, db.func.count(Error.id))
        .filter(Error.project_id == project_id)
        .group_by(Error.severity)
        .all()
    )

    status_stats = (
        db.session.query(Error.status, db.func.count(Error.id))
        .filter(Error.project_id == project_id)
        .group_by(Error.status)
        .all()
    )

    total = Error.query.filter_by(project_id=project_id).count()

    return jsonify({
        'total': total,
        'by_severity': {s: c for s, c in severity_stats},
        'by_status': {s: c for s, c in status_stats},
    })
