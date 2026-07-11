from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.push_schedule import PushSchedule
from app.models.push_provider import PushProvider
from app.models.push_template import PushTemplate
from app.utils.decorators import admin_required

bp = Blueprint('push_schedules_v1', __name__, url_prefix='/api/v1/push-schedules')


@bp.route('', methods=['GET'])
@admin_required
def list_schedules(**kwargs):
    schedules = PushSchedule.query.order_by(PushSchedule.created_at.desc()).all()
    return jsonify([s.to_dict() for s in schedules])


@bp.route('', methods=['POST'])
@admin_required
def create_schedule(**kwargs):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    name = data.get('name', '').strip()
    provider_id = data.get('provider_id')
    template_id = data.get('template_id')
    cron_expression = data.get('cron_expression', '').strip()

    if not name or not provider_id or not template_id or not cron_expression:
        return jsonify({'error': 'name, provider_id, template_id and cron_expression are required'}), 400

    provider = PushProvider.query.get(provider_id)
    if not provider:
        return jsonify({'error': 'Provider not found'}), 404

    template = PushTemplate.query.get(template_id)
    if not template:
        return jsonify({'error': 'Template not found'}), 404

    from croniter import croniter
    try:
        croniter(cron_expression)
    except (ValueError, KeyError):
        return jsonify({'error': 'Invalid cron expression'}), 400

    schedule = PushSchedule(
        name=name,
        provider_id=provider_id,
        template_id=template_id,
        cron_expression=cron_expression,
        timezone=data.get('timezone', 'UTC'),
        is_active=data.get('is_active', True),
    )
    db.session.add(schedule)
    db.session.commit()

    return jsonify(schedule.to_dict()), 201


@bp.route('/<uuid:schedule_id>', methods=['GET'])
@admin_required
def get_schedule(schedule_id, **kwargs):
    schedule = PushSchedule.query.get_or_404(schedule_id)
    return jsonify(schedule.to_dict())


@bp.route('/<uuid:schedule_id>', methods=['PUT'])
@admin_required
def update_schedule(schedule_id, **kwargs):
    schedule = PushSchedule.query.get_or_404(schedule_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'name' in data:
        schedule.name = data['name'].strip()
    if 'provider_id' in data:
        provider = PushProvider.query.get(data['provider_id'])
        if not provider:
            return jsonify({'error': 'Provider not found'}), 404
        schedule.provider_id = data['provider_id']
    if 'template_id' in data:
        template = PushTemplate.query.get(data['template_id'])
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        schedule.template_id = data['template_id']
    if 'cron_expression' in data:
        from croniter import croniter
        try:
            croniter(data['cron_expression'])
        except (ValueError, KeyError):
            return jsonify({'error': 'Invalid cron expression'}), 400
        schedule.cron_expression = data['cron_expression']
    if 'timezone' in data:
        schedule.timezone = data['timezone']
    if 'is_active' in data:
        schedule.is_active = data['is_active']

    db.session.commit()
    return jsonify(schedule.to_dict())


@bp.route('/<uuid:schedule_id>', methods=['DELETE'])
@admin_required
def delete_schedule(schedule_id, **kwargs):
    schedule = PushSchedule.query.get_or_404(schedule_id)
    db.session.delete(schedule)
    db.session.commit()
    return jsonify({'message': 'Schedule deleted'})


@bp.route('/<uuid:schedule_id>/trigger', methods=['POST'])
@admin_required
def trigger_schedule(schedule_id, **kwargs):
    schedule = PushSchedule.query.get_or_404(schedule_id)
    from app.services.push_service import execute_push
    result = execute_push(schedule)
    return jsonify(result)


@bp.route('/logs', methods=['GET'])
@admin_required
def list_logs(**kwargs):
    schedule_id = request.args.get('schedule_id')
    limit = request.args.get('limit', 50, type=int)

    from app.models.push_log import PushLog
    query = PushLog.query
    if schedule_id:
        query = query.filter_by(schedule_id=schedule_id)
    logs = query.order_by(PushLog.pushed_at.desc()).limit(limit).all()
    return jsonify([l.to_dict() for l in logs])
