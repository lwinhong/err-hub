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
    unresolved_count = Error.query.filter_by(status='unresolved').count()

    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    today_new_count = Error.query.filter(
        Error.first_seen_at >= today_start
    ).count()

    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    trend = (
        db.session.query(
            db.func.date_trunc('day', Error.last_seen_at).label('day'),
            db.func.count(Error.id).label('count'),
        )
        .filter(Error.last_seen_at >= seven_days_ago)
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

    recent_errors = (
        Error.query
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
            'project_name': project.name if project else 'Unknown',
            'last_seen_at': e.last_seen_at.isoformat(),
        })

    return jsonify({
        'project_count': project_count,
        'unresolved_count': unresolved_count,
        'today_new_count': today_new_count,
        'trend': trend_data,
        'recent_errors': recent_list,
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
