from datetime import datetime
from sqlalchemy.orm import Session
from app.models import AuditLog
import json

def log_action(db: Session, user_id: int, action: str, table_name: str, record_id: int, changes: dict | None = None):
    """Create an audit log entry.
    action: 'CREATE', 'UPDATE', 'DELETE'
    changes: dict of field changes (for UPDATE), will be stored as JSON string.
    """
    audit = AuditLog(
        user_id=user_id,
        action=action,
        table_name=table_name,
        record_id=record_id,
        timestamp=datetime.utcnow(),
        changes=json.dumps(changes) if changes else None,
    )
    db.add(audit)
    db.commit()
    # Do not refresh; log is independent.
