from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.push_provider import PushProvider
from app.utils.decorators import admin_required

bp = Blueprint('push_providers_v1', __name__, url_prefix='/api/v1/push-providers')


@bp.route('', methods=['GET'])
@admin_required
def list_providers(**kwargs):
    providers = PushProvider.query.order_by(PushProvider.created_at.desc()).all()
    return jsonify([p.to_dict() for p in providers])


@bp.route('', methods=['POST'])
@admin_required
def create_provider(**kwargs):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    name = data.get('name', '').strip()
    provider_type = data.get('provider_type', '').strip()

    if not name or not provider_type:
        return jsonify({'error': 'name and provider_type are required'}), 400

    if provider_type not in ('webhook', 'pushplus'):
        return jsonify({'error': 'provider_type must be webhook or pushplus'}), 400

    if provider_type == 'webhook':
        webhook_url = data.get('webhook_url', '').strip()
        if not webhook_url:
            return jsonify({'error': 'webhook_url is required for webhook provider'}), 400

    if provider_type == 'pushplus':
        pushplus_token = data.get('pushplus_token', '').strip()
        if not pushplus_token:
            return jsonify({'error': 'pushplus_token is required for pushplus provider'}), 400

    provider = PushProvider(
        name=name,
        provider_type=provider_type,
        webhook_url=data.get('webhook_url'),
        headers=data.get('headers', {}),
        secret=data.get('secret'),
        pushplus_token=data.get('pushplus_token'),
        pushplus_channel=data.get('pushplus_channel', 'wechat'),
        pushplus_option=data.get('pushplus_option'),
        pushplus_template=data.get('pushplus_template', 'html'),
        is_active=data.get('is_active', True),
    )
    db.session.add(provider)
    db.session.commit()

    return jsonify(provider.to_dict()), 201


@bp.route('/<uuid:provider_id>', methods=['GET'])
@admin_required
def get_provider(provider_id, **kwargs):
    provider = PushProvider.query.get_or_404(provider_id)
    return jsonify(provider.to_dict())


@bp.route('/<uuid:provider_id>', methods=['PUT'])
@admin_required
def update_provider(provider_id, **kwargs):
    provider = PushProvider.query.get_or_404(provider_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'name' in data:
        provider.name = data['name'].strip()
    if 'provider_type' in data:
        provider_type = data['provider_type'].strip()
        if provider_type not in ('webhook', 'pushplus'):
            return jsonify({'error': 'provider_type must be webhook or pushplus'}), 400
        provider.provider_type = provider_type
    if 'webhook_url' in data:
        provider.webhook_url = data['webhook_url']
    if 'headers' in data:
        provider.headers = data['headers']
    if 'secret' in data:
        provider.secret = data['secret']
    if 'pushplus_token' in data:
        provider.pushplus_token = data['pushplus_token']
    if 'pushplus_channel' in data:
        provider.pushplus_channel = data['pushplus_channel']
    if 'pushplus_option' in data:
        provider.pushplus_option = data['pushplus_option']
    if 'pushplus_template' in data:
        provider.pushplus_template = data['pushplus_template']
    if 'is_active' in data:
        provider.is_active = data['is_active']

    db.session.commit()
    return jsonify(provider.to_dict())


@bp.route('/<uuid:provider_id>', methods=['DELETE'])
@admin_required
def delete_provider(provider_id, **kwargs):
    provider = PushProvider.query.get_or_404(provider_id)
    if provider.schedules.count() > 0:
        return jsonify({'error': 'Cannot delete provider with active schedules'}), 400
    db.session.delete(provider)
    db.session.commit()
    return jsonify({'message': 'Provider deleted'})


@bp.route('/<uuid:provider_id>/test', methods=['POST'])
@admin_required
def test_provider(provider_id, **kwargs):
    provider = PushProvider.query.get_or_404(provider_id)
    from app.services.push_service import send_push
    result = send_push(
        provider=provider,
        subject='ErrHub 测试推送',
        content='<h3>✅ 推送测试成功</h3><p>这是一个来自 ErrHub 的测试消息。</p>',
    )
    return jsonify(result)
