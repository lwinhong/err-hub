import json
import logging
import time
from datetime import datetime, timedelta, timezone

from flask import Blueprint, request, jsonify, Response, stream_with_context, current_app

from app.extensions import db
from app.models.project import Project
from app.models.error import Error
from app.utils.decorators import jwt_required

bp = Blueprint('dashboard_v1', __name__, url_prefix='/api/v1/dashboard')

logger = logging.getLogger(__name__)

SSE_CHANNEL = 'dashboard:update'
SSE_KEEPALIVE_INTERVAL = 15
SSE_CONNECT_TIMEOUT = 5


def query_overview(project_id=None, days=7, hide_resolved=True, recent_project_ids=None):
    project_count = Project.query.count()
    total_errors = Error.query.count()
    unresolved_count = Error.query.filter_by(status='unresolved').count()
    resolved_count = Error.query.filter_by(status='resolved').count()

    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    today_new_count = Error.query.filter(
        Error.first_seen_at >= today_start
    ).count()

    critical_count = Error.query.filter_by(
        status='unresolved', severity='critical'
    ).count()

    days = min(days, 90)
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    trend_query = (
        db.session.query(
            db.func.date_trunc('day', Error.last_seen_at).label('day'),
            db.func.count(Error.id).label('count'),
        )
        .filter(Error.last_seen_at >= start_date)
    )
    if project_id:
        trend_query = trend_query.filter(Error.project_id == project_id)
    trend = trend_query.group_by(
        db.func.date_trunc('day', Error.last_seen_at)
    ).order_by(db.text('day')).all()

    trend_data = [{'date': day.isoformat() if day else None, 'count': count} for day, count in trend]

    recent_query = Error.query
    if hide_resolved:
        recent_query = recent_query.filter(Error.status != 'resolved')
    if recent_project_ids:
        recent_query = recent_query.filter(Error.project_id.in_(recent_project_ids))
    elif project_id:
        recent_query = recent_query.filter(Error.project_id == project_id)

    recent_errors = recent_query.order_by(Error.last_seen_at.desc()).limit(10).all()

    recent_list = []
    for e in recent_errors:
        project = Project.query.get(e.project_id)
        recent_list.append({
            'id': str(e.id),
            'exception_type': e.exception_type,
            'message': e.message,
            'count': e.count,
            'severity': e.severity,
            'status': e.status,
            'source': e.source,
            'environment': e.environment,
            'ip_address': e.ip_address,
            'project_name': project.name if project else 'Unknown',
            'project_id': str(e.project_id),
            'last_seen_at': e.last_seen_at.isoformat(),
        })

    return {
        'project_count': project_count,
        'total_errors': total_errors,
        'unresolved_count': unresolved_count,
        'resolved_count': resolved_count,
        'today_new_count': today_new_count,
        'critical_count': critical_count,
        'trend': trend_data,
        'recent_errors': recent_list,
    }


def query_distributions(project_id=None):
    base_filter = Error.query
    if project_id:
        base_filter = base_filter.filter(Error.project_id == project_id)

    severity_stats = (
        base_filter.with_entities(Error.severity, db.func.count(Error.id))
        .group_by(Error.severity).all()
    )
    source_stats = (
        base_filter.with_entities(Error.source, db.func.count(Error.id))
        .group_by(Error.source).all()
    )
    environment_stats = (
        base_filter.with_entities(Error.environment, db.func.count(Error.id))
        .group_by(Error.environment).all()
    )
    status_stats = (
        base_filter.with_entities(Error.status, db.func.count(Error.id))
        .group_by(Error.status).all()
    )
    top_errors = (
        base_filter.with_entities(
            Error.exception_type, Error.message,
            db.func.sum(Error.count).label('total_count'),
        )
        .group_by(Error.exception_type, Error.message)
        .order_by(db.text('total_count DESC')).limit(5).all()
    )
    project_stats = (
        db.session.query(
            Project.name,
            db.func.sum(Error.count).label('total_count'),
            db.func.count(Error.id).label('error_types'),
        )
        .join(Error, Error.project_id == Project.id)
        .group_by(Project.id, Project.name)
        .order_by(db.text('total_count DESC')).limit(10).all()
    )

    return {
        'by_severity': {s: c for s, c in severity_stats},
        'by_source': {s: c for s, c in source_stats},
        'by_environment': {e: c for e, c in environment_stats},
        'by_status': {s: c for s, c in status_stats},
        'top_errors': [
            {'exception_type': t.exception_type, 'message': t.message[:80], 'count': int(t.total_count or 0)}
            for t in top_errors
        ],
        'project_ranking': [
            {'name': p.name, 'total_count': int(p.total_count or 0), 'error_types': p.error_types}
            for p in project_stats
        ],
    }


@bp.route('/overview', methods=['GET'])
@jwt_required
def overview(**kwargs):
    project_id = request.args.get('project_id')
    days = request.args.get('days', 7, type=int)
    hide_resolved = request.args.get('hide_resolved', 'true').lower() == 'true'
    recent_project_ids = [
        pid.strip() for pid in request.args.get('recent_project_id', '').split(',') if pid.strip()
    ]
    data = query_overview(project_id, days, hide_resolved, recent_project_ids or None)
    return jsonify(data)


@bp.route('/distributions', methods=['GET'])
@jwt_required
def distributions(**kwargs):
    project_id = request.args.get('project_id')
    return jsonify(query_distributions(project_id))


@bp.route('/projects/<project_id>/trend', methods=['GET'])
@jwt_required
def project_trend(project_id, **kwargs):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    days = request.args.get('days', 7, type=int)
    days = min(days, 90)
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    trend = (
        db.session.query(
            db.func.date_trunc('day', Error.last_seen_at).label('day'),
            db.func.count(Error.id).label('count'),
        )
        .filter(Error.project_id == project_id, Error.last_seen_at >= start_date)
        .group_by(db.func.date_trunc('day', Error.last_seen_at))
        .order_by(db.text('day')).all()
    )

    return jsonify({'trend': [{'date': day.isoformat() if day else None, 'count': count} for day, count in trend]})


@bp.route('/stream', methods=['GET'])
def dashboard_stream():
    token = request.args.get('token', '')
    if not token:
        return jsonify({'error': 'token query parameter is required'}), 401

    try:
        import jwt as _jwt
        payload = _jwt.decode(
            token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256']
        )
    except Exception:
        return jsonify({'error': 'Invalid token'}), 401

    from app.models.user import User
    user = User.query.get(payload.get('user_id'))
    if not user or not user.is_active:
        return jsonify({'error': 'User not found or inactive'}), 401

    project_id = request.args.get('project_id') or None
    days = request.args.get('days', 7, type=int)
    hide_resolved = request.args.get('hide_resolved', 'true').lower() == 'true'
    recent_project_ids = [
        pid.strip() for pid in request.args.get('recent_project_id', '').split(',') if pid.strip()
    ] or None

    def generate():
        pubsub = None
        try:
            redis_client = current_app.redis
            pubsub = redis_client.pubsub()
            pubsub.subscribe(SSE_CHANNEL)

            deadline = time.time() + SSE_CONNECT_TIMEOUT
            while time.time() < deadline:
                msg = pubsub.get_message(timeout=0.5)
                if msg and msg['type'] == 'subscribe':
                    break

            overview_data = query_overview(project_id, days, hide_resolved, recent_project_ids)
            dist_data = query_distributions(project_id)
            yield f'data: {json.dumps({"type": "snapshot", "overview": overview_data, "distributions": dist_data})}\n\n'

            last_keepalive = time.time()
            while True:
                msg = pubsub.get_message(timeout=1.0)
                if msg is None:
                    pass
                elif msg['type'] == 'message':
                    overview_data = query_overview(project_id, days, hide_resolved, recent_project_ids)
                    dist_data = query_distributions(project_id)
                    yield f'data: {json.dumps({"type": "update", "overview": overview_data, "distributions": dist_data})}\n\n'
                    last_keepalive = time.time()

                if time.time() - last_keepalive >= SSE_KEEPALIVE_INTERVAL:
                    yield f'data: {json.dumps({"type": "ping"})}\n\n'
                    last_keepalive = time.time()

        except GeneratorExit:
            pass
        except Exception as e:
            logger.warning('SSE stream error: %s', e)
        finally:
            try:
                if pubsub:
                    pubsub.unsubscribe(SSE_CHANNEL)
                    pubsub.close()
            except Exception:
                pass

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
        },
    )
