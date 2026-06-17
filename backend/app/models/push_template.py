import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.extensions import db


class PushTemplate(db.Model):
    __tablename__ = 'push_templates'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    template_type = db.Column(db.String(20), nullable=False)  # error_report | custom_sql

    # error_report 类型
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=True)
    top_n = db.Column(db.Integer, default=10)
    time_range_hours = db.Column(db.Integer, default=24)

    # custom_sql 类型
    sql_query = db.Column(db.Text, nullable=True)
    column_mapping = db.Column(JSONB, nullable=True)

    # 通用字段
    subject = db.Column(db.String(200), nullable=True)
    body_template = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    project = db.relationship('Project', backref='push_templates')
    schedules = db.relationship('PushSchedule', backref='template', lazy='dynamic')

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'template_type': self.template_type,
            'project_id': str(self.project_id) if self.project_id else None,
            'top_n': self.top_n,
            'time_range_hours': self.time_range_hours,
            'sql_query': self.sql_query,
            'column_mapping': self.column_mapping,
            'subject': self.subject,
            'body_template': self.body_template,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
