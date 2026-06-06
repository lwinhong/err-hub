from functools import wraps

import jwt
from flask import request, jsonify, current_app

from app.extensions import db
from app.models.user import User
from app.models.project import Project


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-API-Token')
        if not token:
            return jsonify({'error': 'API token is required'}), 401
        project = Project.query.filter_by(api_token=token).first()
        if not project:
            return jsonify({'error': 'Invalid API token'}), 401
        kwargs['project'] = project
        return f(*args, **kwargs)
    return decorated


def _decode_jwt():
    """解析 JWT 并返回 (user, error_response) 元组。
    成功时返回 (user, None)，失败时返回 (None, error_response)。
    """
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None, (jsonify({'error': 'Authorization header is required'}), 401)
    token = auth_header[7:]
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
    except jwt.ExpiredSignatureError:
        return None, (jsonify({'error': 'Token has expired'}), 401)
    except jwt.InvalidTokenError:
        return None, (jsonify({'error': 'Invalid token'}), 401)
    user = User.query.get(payload.get('user_id'))
    if not user or not user.is_active:
        return None, (jsonify({'error': 'User not found or inactive'}), 401)
    return user, None


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user, err = _decode_jwt()
        if err:
            return err
        kwargs['user_id'] = str(user.id)
        kwargs['current_user'] = user
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user, err = _decode_jwt()
        if err:
            return err
        if not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        kwargs['user_id'] = str(user.id)
        kwargs['current_user'] = user
        return f(*args, **kwargs)
    return decorated
