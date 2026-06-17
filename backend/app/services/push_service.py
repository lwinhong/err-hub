import hashlib
import hmac
import json
from datetime import datetime, timezone

import requests

from app.extensions import db
from app.models.push_log import PushLog
from app.services.push_renderer import render_template_content


def execute_push(schedule):
    """执行推送任务"""
    provider = schedule.provider
    template = schedule.template

    rendered = render_template_content(template)

    result = send_push(
        provider=provider,
        subject=rendered['subject'],
        content=rendered['content'],
    )

    log = PushLog(
        schedule_id=schedule.id,
        status='success' if result.get('success') else 'failed',
        response_code=result.get('response_code'),
        response_body=result.get('response_body', '')[:2000],
        error_message=result.get('error'),
    )
    db.session.add(log)

    schedule.last_pushed_at = datetime.now(timezone.utc)
    db.session.commit()

    return result


def send_push(provider, subject, content):
    """根据供应商类型发送推送"""
    if provider.provider_type == 'webhook':
        return _send_webhook(provider, subject, content)
    elif provider.provider_type == 'pushplus':
        return _send_pushplus(provider, subject, content)
    else:
        return {'success': False, 'error': f'Unknown provider type: {provider.provider_type}'}


def _send_webhook(provider, subject, content):
    """发送 Webhook 推送"""
    payload = {
        'event': 'error_report',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'data': {
            'subject': subject,
            'content': content,
        },
    }

    headers = provider.headers or {}
    headers['Content-Type'] = 'application/json'

    if provider.secret:
        body_str = json.dumps(payload, ensure_ascii=False)
        signature = hmac.new(
            provider.secret.encode(),
            body_str.encode(),
            hashlib.sha256
        ).hexdigest()
        headers['X-Signature'] = f'sha256={signature}'

    try:
        resp = requests.post(
            provider.webhook_url,
            json=payload,
            headers=headers,
            timeout=30,
        )
        return {
            'success': resp.status_code < 400,
            'response_code': resp.status_code,
            'response_body': resp.text[:2000],
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def _send_pushplus(provider, subject, content):
    """发送 PushPlus 推送"""
    payload = {
        'token': provider.pushplus_token,
        'title': subject,
        'content': content,
        'template': provider.pushplus_template or 'html',
        'channel': provider.pushplus_channel or 'wechat',
    }

    if provider.pushplus_option:
        payload['option'] = provider.pushplus_option

    try:
        resp = requests.post(
            'https://www.pushplus.plus/send/',
            json=payload,
            timeout=30,
        )
        data = resp.json()
        return {
            'success': data.get('code') == 200,
            'response_code': resp.status_code,
            'response_body': resp.text[:2000],
            'pushplus_code': data.get('code'),
            'pushplus_msg': data.get('msg'),
            'pushplus_data': data.get('data'),
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
