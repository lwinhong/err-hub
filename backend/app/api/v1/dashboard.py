from datetime import datetime, timedelta, timezone

from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models.project import Project
from app.models.error import Error
from app.utils.decorators import jwt_required

bp = Blueprint('dashboard_v1', __name__, url_prefix='/api/v1/dashboard')


@bp.route('/overview', methods=['GET'])
@jwt_required
def overview(**kwargs):
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

    # critical 级别未解决数
    critical_count = Error.query.filter_by(
        status='unresolved', severity='critical'
    ).count()

    # 趋势数据（支持 project_id 过滤）
    project_id = request.args.get('project_id')
    days = request.args.get('days', 7, type=int)
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

    trend_data = []
    for day, count in trend:
        trend_data.append({
            'date': day.isoformat() if day else None,
            'count': count,
        })

    # 最近异常（支持 hide_resolved 和 recent_project_id 过滤）
    hide_resolved = request.args.get('hide_resolved', 'true').lower() == 'true'
    recent_project_ids = [
        pid.strip() for pid in request.args.get('recent_project_id', '').split(',') if pid.strip()
    ]

    recent_query = Error.query
    if hide_resolved:
        recent_query = recent_query.filter(Error.status != 'resolved')
    if recent_project_ids:
        recent_query = recent_query.filter(Error.project_id.in_(recent_project_ids))

    recent_errors = (
        recent_query
        .order_by(Error.last_seen_at.desc())
        .limit(10)
        .all()
    )

    recent_list = []
    for e in recent_errors:
        project = Project.query.get(e.project_id)
        recent_list.append({
            'id': str(e.id),
            'exception_type': e.exception_type,
            'message': e.message,
            'severity': e.severity,
            'status': e.status,
            'source': e.source,
            'environment': e.environment,
            'ip_address': e.ip_address,
            'project_name': project.name if project else 'Unknown',
            'project_id': str(e.project_id),
            'last_seen_at': e.last_seen_at.isoformat(),
        })

    return jsonify({
        'project_count': project_count,
        'total_errors': total_errors,
        'unresolved_count': unresolved_count,
        'resolved_count': resolved_count,
        'today_new_count': today_new_count,
        'critical_count': critical_count,
        'trend': trend_data,
        'recent_errors': recent_list,
    })


@bp.route('/distributions', methods=['GET'])
@jwt_required
def distributions(**kwargs):
    """返回各类分布数据，供 Dashboard 图表使用"""
    project_id = request.args.get('project_id')

    base_filter = Error.query
    if project_id:
        base_filter = base_filter.filter(Error.project_id == project_id)

    # 严重级别分布
    severity_stats = (
        base_filter.with_entities(
            Error.severity, db.func.count(Error.id)
        )
        .group_by(Error.severity)
        .all()
    )

    # 来源分布（前端/后端）
    source_stats = (
        base_filter.with_entities(
            Error.source, db.func.count(Error.id)
        )
        .group_by(Error.source)
        .all()
    )

    # 环境分布
    environment_stats = (
        base_filter.with_entities(
            Error.environment, db.func.count(Error.id)
        )
        .group_by(Error.environment)
        .all()
    )

    # 状态分布
    status_stats = (
        base_filter.with_entities(
            Error.status, db.func.count(Error.id)
        )
        .group_by(Error.status)
        .all()
    )

    # Top 5 异常类型（按出现总次数 count 字段降序）
    top_errors = (
        base_filter.with_entities(
            Error.exception_type,
            Error.message,
            db.func.sum(Error.count).label('total_count'),
        )
        .group_by(Error.exception_type, Error.message)
        .order_by(db.text('total_count DESC'))
        .limit(5)
        .all()
    )

    # 各项目异常数排名（Top 10）
    project_stats = (
        db.session.query(
            Project.name,
            db.func.sum(Error.count).label('total_count'),
            db.func.count(Error.id).label('error_types'),
        )
        .join(Error, Error.project_id == Project.id)
        .group_by(Project.id, Project.name)
        .order_by(db.text('total_count DESC'))
        .limit(10)
        .all()
    )

    return jsonify({
        'by_severity': {s: c for s, c in severity_stats},
        'by_source': {s: c for s, c in source_stats},
        'by_environment': {e: c for e, c in environment_stats},
        'by_status': {s: c for s, c in status_stats},
        'top_errors': [
            {
                'exception_type': t.exception_type,
                'message': t.message[:80],
                'count': int(t.total_count or 0),
            }
            for t in top_errors
        ],
        'project_ranking': [
            {
                'name': p.name,
                'total_count': int(p.total_count or 0),
                'error_types': p.error_types,
            }
            for p in project_stats
        ],
    })


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
        .order_by(db.text('day'))
        .all()
    )

    trend_data = []
    for day, count in trend:
        trend_data.append({
            'date': day.isoformat() if day else None,
            'count': count,
        })

    return jsonify({'trend': trend_data})
