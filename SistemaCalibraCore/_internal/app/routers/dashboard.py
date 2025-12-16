"""
CalibraCore Lab - Dashboard Router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.auth import get_current_user
from app.models import Equipamento, Usuario, EquipmentStatus
from app.schemas import DashboardResumo

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/resumo", response_model=DashboardResumo)
async def obter_resumo(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Get dashboard summary with equipment counts by status
    """
    # Get all active equipment
    equipamentos = db.query(Equipamento).filter(Equipamento.ativo == True).all()
    
    # Count by status
    total = len(equipamentos)
    em_dia = 0
    vence_60_dias = 0
    vence_30_dias = 0
    vencidos = 0
    
    for eq in equipamentos:
        status = eq.status
        if status == EquipmentStatus.EM_DIA:
            em_dia += 1
        elif status == EquipmentStatus.PROXIMO_60:
            vence_60_dias += 1
        elif status == EquipmentStatus.PROXIMO_30:
            vence_30_dias += 1
        elif status == EquipmentStatus.VENCIDO:
            vencidos += 1
    
    return {
        "total": total,
        "em_dia": em_dia,
        "vence_60_dias": vence_60_dias,
        "vence_30_dias": vence_30_dias,
        "vencidos": vencidos
    }


@router.get("/laboratorios-stats")
async def obter_stats_por_laboratorio(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Get equipment counts by laboratory
    """
    equipamentos = db.query(Equipamento).filter(Equipamento.ativo == True).all()
    
    lab_stats = {}
    for eq in equipamentos:
        lab = eq.laboratorio
        if lab not in lab_stats:
            lab_stats[lab] = {
                "total": 0,
                "em_dia": 0,
                "vence_60_dias": 0,
                "vence_30_dias": 0,
                "vencidos": 0
            }
        
        lab_stats[lab]["total"] += 1
        status = eq.status
        
        if status == EquipmentStatus.EM_DIA:
            lab_stats[lab]["em_dia"] += 1
        elif status == EquipmentStatus.PROXIMO_60:
            lab_stats[lab]["vence_60_dias"] += 1
        elif status == EquipmentStatus.PROXIMO_30:
            lab_stats[lab]["vence_30_dias"] += 1
        elif status == EquipmentStatus.VENCIDO:
            lab_stats[lab]["vencidos"] += 1
    
    return lab_stats
