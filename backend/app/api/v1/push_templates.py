from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.push_template import PushTemplate
from app.utils.decorators import admin_required

bp = Blueprint('push_templates_v1', __name__, url_prefix='/api/v1/push-templates')


@bp.route('', methods=['GET'])
@admin_required
def list_templates(**kwargs):
    templates = PushTemplate.query.order_by(PushTemplate.created_at.desc()).all()
    return jsonify([t.to_dict() for t in templates])


@bp.route('', methods=['POST'])
@admin_required
def create_template(**kwargs):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    name = data.get('name', '').strip()
    template_type = data.get('template_type', '').strip()
    body_template = data.get('body_template', '').strip()

    if not name or not template_type or not body_template:
        return jsonify({'error': 'name, template_type and body_template are required'}), 400

    if template_type not in ('error_report', 'custom_sql'):
        return jsonify({'error': 'template_type must be error_report or custom_sql'}), 400

    if template_type == 'custom_sql' and not data.get('sql_query', '').strip():
        return jsonify({'error': 'sql_query is required for custom_sql template type'}), 400

    template = PushTemplate(
        name=name,
        template_type=template_type,
        project_id=data.get('project_id'),
        top_n=data.get('top_n', 10),
        time_range_hours=data.get('time_range_hours', 24),
        sql_query=data.get('sql_query'),
        column_mapping=data.get('column_mapping'),
        subject=data.get('subject'),
        body_template=body_template,
    )
    db.session.add(template)
    db.session.commit()

    return jsonify(template.to_dict()), 201


@bp.route('/<uuid:template_id>', methods=['GET'])
@admin_required
def get_template(template_id, **kwargs):
    template = PushTemplate.query.get_or_404(template_id)
    return jsonify(template.to_dict())


@bp.route('/<uuid:template_id>', methods=['PUT'])
@admin_required
def update_template(template_id, **kwargs):
    template = PushTemplate.query.get_or_404(template_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'name' in data:
        template.name = data['name'].strip()
    if 'template_type' in data:
        template_type = data['template_type'].strip()
        if template_type not in ('error_report', 'custom_sql'):
            return jsonify({'error': 'template_type must be error_report or custom_sql'}), 400
        template.template_type = template_type
    if 'project_id' in data:
        template.project_id = data['project_id']
    if 'top_n' in data:
        template.top_n = data['top_n']
    if 'time_range_hours' in data:
        template.time_range_hours = data['time_range_hours']
    if 'sql_query' in data:
        template.sql_query = data['sql_query']
    if 'column_mapping' in data:
        template.column_mapping = data['column_mapping']
    if 'subject' in data:
        template.subject = data['subject']
    if 'body_template' in data:
        template.body_template = data['body_template'].strip()

    db.session.commit()
    return jsonify(template.to_dict())


@bp.route('/<uuid:template_id>', methods=['DELETE'])
@admin_required
def delete_template(template_id, **kwargs):
    template = PushTemplate.query.get_or_404(template_id)
    if template.schedules.count() > 0:
        return jsonify({'error': 'Cannot delete template with active schedules'}), 400
    db.session.delete(template)
    db.session.commit()
    return jsonify({'message': 'Template deleted'})


@bp.route('/<uuid:template_id>/preview', methods=['POST'])
@admin_required
def preview_template(template_id, **kwargs):
    template = PushTemplate.query.get_or_404(template_id)
    from app.services.push_renderer import render_template_content
    result = render_template_content(template)
    return jsonify(result)
