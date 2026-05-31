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


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header is required'}), 401
        token = auth_header[7:]
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        user = User.query.get(payload.get('user_id'))
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401
        kwargs['user_id'] = payload.get('user_id')
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header is required'}), 401
        token = auth_header[7:]
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        user = User.query.get(payload.get('user_id'))
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401
        if not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        kwargs['user_id'] = payload.get('user_id')
        return f(*args, **kwargs)
    return decorated
