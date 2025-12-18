from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import require_admin
from app.models import AuditLog, Usuario
from app.schemas import AuditLogResponse

router = APIRouter(prefix="/api/audit", tags=["Audit"])

@router.get("", response_model=List[AuditLogResponse])
async def get_audit_logs(
    limit: int = Query(50, le=100),
    offset: int = 0,
    table: Optional[str] = None,
    action: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Get audit logs (Admin only)
    """
    query = db.query(AuditLog)
    
    if table:
        query = query.filter(AuditLog.table_name == table)
    if action:
        query = query.filter(AuditLog.action == action)
        
    # Sort by timestamp desc
    query = query.order_by(AuditLog.timestamp.desc())
    
    logs = query.offset(offset).limit(limit).all()
    
    # Enrich with user name
    result = []
    for log in logs:
        # We could join in SQL, but for simplicity/speed let's assume partial load or lazy load
        # Actually user relationship exists in model
        log_resp = AuditLogResponse.model_validate(log)
        if log.user:
            log_resp.user_nome = log.user.nome
        result.append(log_resp)
        
    return result
