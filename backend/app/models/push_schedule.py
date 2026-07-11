import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db


class PushSchedule(db.Model):
    __tablename__ = 'push_schedules'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    provider_id = db.Column(UUID(as_uuid=True), db.ForeignKey('push_providers.id'), nullable=False)
    template_id = db.Column(UUID(as_uuid=True), db.ForeignKey('push_templates.id'), nullable=False)
    cron_expression = db.Column(db.String(50), nullable=False)
    timezone = db.Column(db.String(50), nullable=False, default='UTC')
    is_active = db.Column(db.Boolean, default=True)
    last_pushed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    logs = db.relationship('PushLog', backref='schedule', lazy='dynamic')

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'provider_id': str(self.provider_id),
            'template_id': str(self.template_id),
            'cron_expression': self.cron_expression,
            'timezone': self.timezone,
            'is_active': self.is_active,
            'last_pushed_at': self.last_pushed_at.isoformat() if self.last_pushed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'provider': self.provider.to_dict() if self.provider else None,
            'template': self.template.to_dict() if self.template else None,
        }
