import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.extensions import db


class PushProvider(db.Model):
    __tablename__ = 'push_providers'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    provider_type = db.Column(db.String(20), nullable=False)  # webhook | pushplus

    # webhook 配置
    webhook_url = db.Column(db.Text, nullable=True)
    headers = db.Column(JSONB, default=dict)
    secret = db.Column(db.String(255), nullable=True)

    # pushplus 配置
    pushplus_token = db.Column(db.String(255), nullable=True)
    pushplus_channel = db.Column(db.String(20), default='wechat')
    pushplus_option = db.Column(db.String(100), nullable=True)
    pushplus_template = db.Column(db.String(20), default='html')

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    schedules = db.relationship('PushSchedule', backref='provider', lazy='dynamic')

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'provider_type': self.provider_type,
            'webhook_url': self.webhook_url,
            'headers': self.headers or {},
            'secret': self.secret,
            'pushplus_token': self.pushplus_token,
            'pushplus_channel': self.pushplus_channel,
            'pushplus_option': self.pushplus_option,
            'pushplus_template': self.pushplus_template,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
