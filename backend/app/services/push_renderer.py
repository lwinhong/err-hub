import re

from app.services.push_data import get_error_report_data, get_custom_sql_data


def render_template_content(template):
    """渲染推送模板内容"""
    if template.template_type == 'error_report':
        variables = get_error_report_data(template)
    elif template.template_type == 'custom_sql':
        variables = get_custom_sql_data(template)
    else:
        return {'subject': '', 'content': '', 'error': f'Unknown template type: {template.template_type}'}

    subject = _replace_variables(template.subject or '', variables)
    content = _replace_variables(template.body_template, variables)

    return {
        'subject': subject,
        'content': content,
        'variables': {k: v for k, v in variables.items() if not isinstance(v, str) or len(v) < 500},
    }


def _replace_variables(text, variables):
    """替换模板中的 {{variable}} 变量"""
    def replacer(match):
        key = match.group(1).strip()
        value = variables.get(key, match.group(0))
        return str(value) if value is not None else ''

    return re.sub(r'\{\{(\w+)\}\}', replacer, text)
