from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.models.error import Error


def cleanup_old_errors(retention_days):
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    count = Error.query.filter(Error.last_seen_at < cutoff).delete()
    db.session.commit()
    return count
