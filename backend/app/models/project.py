import uuid
import secrets
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    project_key = db.Column(db.String(32), unique=True, nullable=False)
    api_token = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_disabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    errors = db.relationship('Error', backref='project', lazy='dynamic')

    @staticmethod
    def generate_key():
        return secrets.token_hex(16)

    @staticmethod
    def generate_token():
        return secrets.token_hex(32)
