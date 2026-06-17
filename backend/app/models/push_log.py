import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.extensions import db


class PushLog(db.Model):
    __tablename__ = 'push_logs'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schedule_id = db.Column(UUID(as_uuid=True), db.ForeignKey('push_schedules.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # success | failed
    response_code = db.Column(db.Integer, nullable=True)
    response_body = db.Column(db.Text, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    pushed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': str(self.id),
            'schedule_id': str(self.schedule_id),
            'status': self.status,
            'response_code': self.response_code,
            'response_body': self.response_body,
            'error_message': self.error_message,
            'pushed_at': self.pushed_at.isoformat() if self.pushed_at else None,
        }
