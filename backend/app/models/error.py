import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.extensions import db


class Error(db.Model):
    __tablename__ = 'errors'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=False)
    fingerprint = db.Column(db.String(32), nullable=False)
    exception_type = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    stack_trace = db.Column(db.Text, nullable=True)
    severity = db.Column(db.String(20), default='error')
    environment = db.Column(db.String(50), default='unknown')
    source = db.Column(db.String(20), default='backend')
    context = db.Column(JSONB, nullable=True)
    count = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='unresolved')
    first_seen_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('project_id', 'fingerprint', name='uq_project_fingerprint'),
    )
