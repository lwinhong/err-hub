from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models.user import User
from app.models.project import Project
from app.utils.decorators import jwt_required, admin_required

bp = Blueprint('projects_v1', __name__, url_prefix='/api/v1/projects')


@bp.route('/', methods=['GET'])
@jwt_required
def list_projects(**kwargs):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)
    pagination = Project.query.order_by(Project.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'items': [
            {
                'id': str(p.id),
                'name': p.name,
                'project_key': p.project_key,
                'api_token': p.api_token,
                'description': p.description,
                'created_at': p.created_at.isoformat(),
            }
            for p in pagination.items
        ],
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages,
    })


@bp.route('/', methods=['POST'])
@jwt_required
def create_project(**kwargs):
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Project name is required'}), 400
    project = Project(
        name=data['name'],
        project_key=Project.generate_key(),
        api_token=Project.generate_token(),
        description=data.get('description'),
    )
    db.session.add(project)
    db.session.commit()
    return jsonify({
        'id': str(project.id),
        'name': project.name,
        'project_key': project.project_key,
        'api_token': project.api_token,
        'description': project.description,
        'created_at': project.created_at.isoformat(),
    }), 201


@bp.route('/<project_id>', methods=['GET'])
@jwt_required
def get_project(project_id, **kwargs):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    return jsonify({
        'id': str(project.id),
        'name': project.name,
        'project_key': project.project_key,
        'api_token': project.api_token,
        'description': project.description,
        'created_at': project.created_at.isoformat(),
    })


@bp.route('/<project_id>', methods=['PUT'])
@jwt_required
def update_project(project_id, **kwargs):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']
    db.session.commit()
    return jsonify({
        'id': str(project.id),
        'name': project.name,
        'project_key': project.project_key,
        'api_token': project.api_token,
        'description': project.description,
        'created_at': project.created_at.isoformat(),
    })


@bp.route('/<project_id>', methods=['DELETE'])
@admin_required
def delete_project(project_id, **kwargs):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': 'Project deleted successfully'})


@bp.route('/<project_id>/regenerate-token', methods=['POST'])
@jwt_required
def regenerate_token(project_id, **kwargs):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    project.api_token = Project.generate_token()
    db.session.commit()
    return jsonify({
        'id': str(project.id),
        'api_token': project.api_token,
    })
