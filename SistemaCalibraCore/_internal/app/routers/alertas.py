"""
CalibraCore Lab - Alerts Router
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user, require_admin
from app.models import AlertaEnviado, Equipamento, Usuario
from app.schemas import AlertaResponse, ProcessarAlertasResponse
from app.services.alerta_service import process_alerts

router = APIRouter(prefix="/api/alertas", tags=["Alertas"])


@router.post("/processar", response_model=ProcessarAlertasResponse)
async def processar_alertas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Process all equipment and send calibration alerts
    This endpoint should be called daily (via cron/scheduler)
    """
    result = await process_alerts(db)
    return result


@router.get("/historico", response_model=List[AlertaResponse])
async def listar_historico_alertas(
    equipamento_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Get alert history
    """
    query = db.query(AlertaEnviado).order_by(AlertaEnviado.data_envio.desc())
    
    if equipamento_id:
        query = query.filter(AlertaEnviado.equipamento_id == equipamento_id)
    
    alertas = query.limit(limit).all()
    
    result = []
    for alerta in alertas:
        eq = db.query(Equipamento).filter(Equipamento.id == alerta.equipamento_id).first()
        result.append({
            "id": alerta.id,
            "equipamento_id": alerta.equipamento_id,
            "equipamento_codigo": eq.codigo_interno if eq else None,
            "equipamento_descricao": eq.descricao if eq else None,
            "tipo_alerta": alerta.tipo_alerta,
            "data_envio": alerta.data_envio,
            "destinatarios": alerta.destinatarios,
            "sucesso": alerta.sucesso
        })
    
    return result
