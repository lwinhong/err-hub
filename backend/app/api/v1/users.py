from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models.user import User
from app.utils.decorators import admin_required

bp = Blueprint('users_v1', __name__, url_prefix='/api/v1/users')


def _user_to_dict(user):
    return {
        'id': str(user.id),
        'username': user.username,
        'is_admin': user.is_admin,
        'is_active': user.is_active,
        'locked_until': user.locked_until.isoformat() if user.locked_until else None,
        'is_locked': user.is_locked,
        'created_at': user.created_at.isoformat(),
    }


@bp.route('', methods=['GET'])
@admin_required
def list_users(**kwargs):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)
    pagination = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'items': [_user_to_dict(u) for u in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages,
    })


@bp.route('', methods=['POST'])
@admin_required
def create_user(**kwargs):
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400

    existing = User.query.filter_by(username=data['username']).first()
    if existing:
        return jsonify({'error': 'Username already exists'}), 409

    user = User(
        username=data['username'],
        is_admin=data.get('is_admin', False),
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify(_user_to_dict(user)), 201


@bp.route('/<user_id>', methods=['PUT'])
@admin_required
def update_user(user_id, **kwargs):
    current_user = kwargs['current_user']
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'is_admin' in data:
        # 不允许取消自身 admin 权限
        if str(user.id) == str(current_user.id) and not data['is_admin']:
            return jsonify({'error': 'Cannot revoke your own admin privilege'}), 400
        user.is_admin = data['is_admin']

    if 'is_active' in data:
        # 不允许停用自己
        if str(user.id) == str(current_user.id) and not data['is_active']:
            return jsonify({'error': 'Cannot disable your own account'}), 400
        user.is_active = data['is_active']

    db.session.commit()
    return jsonify(_user_to_dict(user))


@bp.route('/<user_id>/reset-password', methods=['PUT'])
@admin_required
def reset_password(user_id, **kwargs):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data or not data.get('password'):
        return jsonify({'error': 'New password is required'}), 400

    user.set_password(data['password'])
    db.session.commit()
    return jsonify({'message': 'Password has been reset'})


@bp.route('/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id, **kwargs):
    current_user = kwargs['current_user']
    if str(user_id) == str(current_user.id):
        return jsonify({'error': 'Cannot delete yourself'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})


@bp.route('/<user_id>/unlock', methods=['POST'])
@admin_required
def unlock_user(user_id, **kwargs):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.unlock()
    db.session.commit()
    return jsonify({'message': 'User unlocked successfully'})
