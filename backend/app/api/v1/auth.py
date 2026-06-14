from datetime import datetime, timezone

import jwt
from flask import Blueprint, request, jsonify, current_app

from app.extensions import db
from app.models.user import User
from app.models.setting import SystemSetting
from app.utils.decorators import jwt_required

bp = Blueprint('auth_v1', __name__, url_prefix='/api/v1/auth')


def _get_setting_int(key, default):
    val = SystemSetting.get_value(key)
    if val is not None:
        try:
            return int(val)
        except (ValueError, TypeError):
            pass
    return default


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400
    if not data.get('captcha_id'):
        return jsonify({'error': 'Captcha verification is required'}), 400

    captcha_id = data['captcha_id']
    store_key = f'captcha_verified:{captcha_id}'
    if not current_app.redis.get(store_key):
        return jsonify({'error': 'Captcha verification failed or expired'}), 400
    current_app.redis.delete(store_key)

    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        if user and user.is_active:
            login_max_fails = _get_setting_int('login_max_fails', 5)
            login_lock_duration = _get_setting_int('login_lock_duration', 600)
            fail_key = f'login_fails:{user.id}'
            fail_count = current_app.redis.incr(fail_key)
            current_app.redis.expire(fail_key, login_lock_duration)

            if fail_count >= login_max_fails:
                user.lock(login_lock_duration)
                db.session.commit()
        return jsonify({'error': 'Invalid username or password'}), 401
    if not user.is_active:
        return jsonify({'error': 'User account is disabled'}), 403
    if user.is_locked:
        remaining = int((user.locked_until - datetime.now(timezone.utc)).total_seconds())
        return jsonify({
            'error': f'Account is locked, try again in {remaining} seconds',
            'remaining_seconds': remaining,
        }), 403

    current_app.redis.delete(f'login_fails:{user.id}')

    now = datetime.now(timezone.utc)
    access_payload = {
        'user_id': str(user.id),
        'type': 'access',
        'exp': now + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
        'iat': now,
    }
    refresh_payload = {
        'user_id': str(user.id),
        'type': 'refresh',
        'exp': now + current_app.config['JWT_REFRESH_TOKEN_EXPIRES'],
        'iat': now,
    }
    access_token = jwt.encode(access_payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    refresh_token = jwt.encode(refresh_payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
    })


@bp.route('/refresh', methods=['POST'])
def refresh():
    data = request.get_json()
    if not data or not data.get('refresh_token'):
        return jsonify({'error': 'Refresh token is required'}), 400
    try:
        payload = jwt.decode(
            data['refresh_token'],
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Refresh token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid refresh token'}), 401
    if payload.get('type') != 'refresh':
        return jsonify({'error': 'Invalid token type'}), 401
    user = User.query.get(payload.get('user_id'))
    if not user or not user.is_active:
        return jsonify({'error': 'User not found or inactive'}), 401
    now = datetime.now(timezone.utc)
    access_payload = {
        'user_id': str(user.id),
        'type': 'access',
        'exp': now + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
        'iat': now,
    }
    access_token = jwt.encode(access_payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return jsonify({'access_token': access_token})


@bp.route('/me', methods=['GET'])
@jwt_required
def me(**kwargs):
    user = User.query.get(kwargs['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'id': str(user.id),
        'username': user.username,
        'is_admin': user.is_admin,
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat(),
    })


@bp.route('/me/password', methods=['PUT'])
@jwt_required
def change_password(**kwargs):
    user = User.query.get(kwargs['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    data = request.get_json()
    if not data or not data.get('old_password') or not data.get('new_password'):
        return jsonify({'error': 'Old password and new password are required'}), 400
    if not user.check_password(data['old_password']):
        return jsonify({'error': 'Old password is incorrect'}), 400
    user.set_password(data['new_password'])
    db.session.commit()
    return jsonify({'message': 'Password updated successfully'})
