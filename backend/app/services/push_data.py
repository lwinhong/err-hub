import re
from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.models.error import Error
from app.models.project import Project


def get_error_report_data(template):
    """获取异常报告数据"""
    now = datetime.now(timezone.utc)
    time_range_hours = template.time_range_hours or 24
    since = now - timedelta(hours=time_range_hours)

    query = Error.query

    if template.project_id:
        query = query.filter_by(project_id=template.project_id)
        project = Project.query.get(template.project_id)
        project_name = project.name if project else 'Unknown'
    else:
        project_name = 'All Projects'

    total_count = query.count()
    new_count = query.filter(Error.first_seen_at >= since).count()
    resolved_count = query.filter_by(status='resolved').count()

    top_n = template.top_n or 10
    top_errors = query.order_by(Error.count.desc()).limit(top_n).all()

    error_list_rows = []
    for i, err in enumerate(top_errors, 1):
        error_list_rows.append(
            f"<tr>"
            f"<td style='padding:6px 12px;border-bottom:1px solid #eee;'>{i}</td>"
            f"<td style='padding:6px 12px;border-bottom:1px solid #eee;'>{err.exception_type}</td>"
            f"<td style='padding:6px 12px;border-bottom:1px solid #eee;'>{err.message[:80]}</td>"
            f"<td style='padding:6px 12px;border-bottom:1px solid #eee;text-align:right;'>{err.count}</td>"
            f"<td style='padding:6px 12px;border-bottom:1px solid #eee;'>{err.severity}</td>"
            f"</tr>"
        )

    error_list_html = (
        "<table style='border-collapse:collapse;width:100%;font-size:13px;'>"
        "<thead><tr style='background:#f5f5f5;'>"
        "<th style='padding:6px 12px;text-align:left;'>#</th>"
        "<th style='padding:6px 12px;text-align:left;'>类型</th>"
        "<th style='padding:6px 12px;text-align:left;'>消息</th>"
        "<th style='padding:6px 12px;text-align:right;'>次数</th>"
        "<th style='padding:6px 12px;text-align:left;'>级别</th>"
        "</tr></thead>"
        f"<tbody>{''.join(error_list_rows)}</tbody></table>"
    )

    return {
        'project_name': project_name,
        'error_count': total_count,
        'new_errors': new_count,
        'resolved_errors': resolved_count,
        'error_list': error_list_html,
        'time_range': f"{since.strftime('%Y-%m-%d %H:%M')} ~ {now.strftime('%Y-%m-%d %H:%M')}",
        'dashboard_url': '',
        'top_n': top_n,
    }


def get_custom_sql_data(template):
    """获取自定义 SQL 查询数据"""
    from sqlalchemy import text

    result = db.session.execute(text(template.sql_query))
    rows = result.mappings().all()

    if not rows:
        return {'columns': [], 'rows': [], 'row_count': 0}

    columns = list(rows[0].keys())
    data_rows = []
    for row in rows:
        data_rows.append({col: str(row[col]) if row[col] is not None else '' for col in columns})

    formatted_rows = []
    for row in data_rows:
        cells = ''.join(
            f"<td style='padding:6px 12px;border-bottom:1px solid #eee;'>{row[col]}</td>"
            for col in columns
        )
        formatted_rows.append(f"<tr>{cells}</tr>")

    mapping = template.column_mapping or {}
    header_cells = ''.join(
        f"<th style='padding:6px 12px;text-align:left;'>{mapping.get(col, col)}</th>"
        for col in columns
    )

    table_html = (
        "<table style='border-collapse:collapse;width:100%;font-size:13px;'>"
        f"<thead><tr style='background:#f5f5f5;'>{header_cells}</tr></thead>"
        f"<tbody>{''.join(formatted_rows)}</tbody></table>"
    )

    variables = {'table': table_html, 'row_count': len(data_rows)}
    for col in columns:
        variables[col] = data_rows[0].get(col, '') if data_rows else ''

    return variables
