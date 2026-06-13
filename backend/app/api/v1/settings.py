from flask import Blueprint, request, jsonify
from flask import current_app

from app.models.setting import SystemSetting
from app.utils.decorators import admin_required

bp = Blueprint('settings_v1', __name__, url_prefix='/api/v1/settings')

# 可配置项白名单：key -> (类型转换, 最小值, 最大值, 描述)
SETTING_SCHEMA = {
    'data_retention_days': {
        'type': int,
        'min': 1,
        'max': 3650,
        'description': '异常数据保留天数，超出后自动清理',
    },
    'default_page_size': {
        'type': int,
        'min': 10,
        'max': 100,
        'description': '列表默认每页显示条数',
    },
}


def _get_all_settings():
    """返回所有可配置项的当前值与默认值"""
    result = {}
    for key, schema in SETTING_SCHEMA.items():
        db_val = SystemSetting.get_value(key)
        default_val = current_app.config.get(key.upper())
        result[key] = {
            'value': int(db_val) if db_val is not None else default_val,
            'default': default_val,
            'description': schema['description'],
            'min': schema.get('min'),
            'max': schema.get('max'),
        }
    return result


@bp.route('', methods=['GET'])
@admin_required
def get_settings(**kwargs):
    return jsonify(_get_all_settings())


@bp.route('', methods=['PUT'])
@admin_required
def update_settings(**kwargs):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    errors = []
    updated = []

    for key, raw_value in data.items():
        schema = SETTING_SCHEMA.get(key)
        if not schema:
            errors.append(f'Unknown setting: {key}')
            continue

        try:
            value = schema['type'](raw_value)
        except (ValueError, TypeError):
            errors.append(f'Invalid type for {key}')
            continue

        if 'min' in schema and value < schema['min']:
            errors.append(f'{key} must be >= {schema["min"]}')
            continue
        if 'max' in schema and value > schema['max']:
            errors.append(f'{key} must be <= {schema["max"]}')
            continue

        SystemSetting.set_value(key, value, schema.get('description'))
        updated.append(key)

    if errors:
        return jsonify({'error': '; '.join(errors)}), 400

    return jsonify({
        'message': 'Settings updated',
        'updated': updated,
        'settings': _get_all_settings(),
    })
