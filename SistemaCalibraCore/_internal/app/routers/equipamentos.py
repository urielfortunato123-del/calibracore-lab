"""
CalibraCore Lab - Equipment Router
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import date

from app.database import get_db
from app.auth import get_current_user
from app.models import Equipamento, Usuario, EquipmentStatus
from app.schemas import (
    EquipamentoCreate,
    EquipamentoUpdate,
    EquipamentoResponse,
    EquipamentoListResponse
)

router = APIRouter(prefix="/api/equipamentos", tags=["Equipamentos"])


def equipamento_to_response(eq: Equipamento) -> dict:
    """Convert equipment model to response dict"""
    return {
        "id": eq.id,
        "codigo_interno": eq.codigo_interno,
        "descricao": eq.descricao,
        "categoria": eq.categoria,
        "marca": eq.marca,
        "numero_certificado": eq.numero_certificado,
        "numero_serie": eq.numero_serie,
        "laboratorio": eq.laboratorio,
        "responsavel_id": eq.responsavel_id,
        "data_ultima_calibracao": eq.data_ultima_calibracao,
        "data_vencimento": eq.data_vencimento,
        "observacoes": eq.observacoes,
        "status": eq.status.value,
        "dias_para_vencer": eq.dias_para_vencer,
        "ativo": eq.ativo,
        "criado_em": eq.criado_em,
        "responsavel_nome": eq.responsavel_usuario.nome if eq.responsavel_usuario else None
    }


@router.get("", response_model=EquipamentoListResponse)
async def listar_equipamentos(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    laboratorio: Optional[str] = None,
    categoria: Optional[str] = None,
    status: Optional[str] = None,
    busca: Optional[str] = None,
    ativo: bool = True,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    List equipment with filters and pagination
    """
    query = db.query(Equipamento).filter(Equipamento.ativo == ativo)
    
    # Filter by laboratory
    if laboratorio:
        query = query.filter(Equipamento.laboratorio == laboratorio)
    
    # Filter by categoria
    if categoria:
        query = query.filter(Equipamento.categoria == categoria)
    
    # Filter by search term
    if busca:
        search_term = f"%{busca}%"
        query = query.filter(
            or_(
                Equipamento.codigo_interno.ilike(search_term),
                Equipamento.descricao.ilike(search_term),
                Equipamento.numero_serie.ilike(search_term)
            )
        )
    
    # Get all results for status filtering (since status is calculated)
    all_results = query.all()
    
    # Filter by status if specified
    if status:
        status_enum = EquipmentStatus(status)
        all_results = [eq for eq in all_results if eq.status == status_enum]
    
    # Sort by expiration date (soonest first)
    all_results.sort(key=lambda x: x.data_vencimento or date.max)
    
    # Pagination
    total = len(all_results)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = all_results[start:end]
    
    pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    return {
        "items": [equipamento_to_response(eq) for eq in paginated],
        "total": total,
        "page": page,
        "pages": pages
    }


@router.get("/laboratorios")
async def listar_laboratorios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Get list of unique laboratories
    """
    labs = db.query(Equipamento.laboratorio).distinct().all()
    return [lab[0] for lab in labs if lab[0]]


@router.get("/categorias")
async def listar_categorias(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Get list of unique categories
    """
    cats = db.query(Equipamento.categoria).distinct().all()
    return [cat[0] for cat in cats if cat[0]]


@router.get("/{equipamento_id}", response_model=EquipamentoResponse)
async def obter_equipamento(
    equipamento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Get equipment by ID
    """
    equipamento = db.query(Equipamento).filter(Equipamento.id == equipamento_id).first()
    if not equipamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipamento não encontrado"
        )
    return equipamento_to_response(equipamento)


@router.post("", response_model=EquipamentoResponse, status_code=status.HTTP_201_CREATED)
async def criar_equipamento(
    equipamento: EquipamentoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Create new equipment
    """
    # Check for duplicate code
    existing = db.query(Equipamento).filter(
        Equipamento.codigo_interno == equipamento.codigo_interno
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um equipamento com este código interno"
        )
    
    db_equipamento = Equipamento(
        codigo_interno=equipamento.codigo_interno,
        descricao=equipamento.descricao,
        categoria=equipamento.categoria,
        marca=equipamento.marca,
        numero_certificado=equipamento.numero_certificado,
        numero_serie=equipamento.numero_serie,
        laboratorio=equipamento.laboratorio,
        responsavel_id=equipamento.responsavel_id or current_user.id,
        data_ultima_calibracao=equipamento.data_ultima_calibracao,
        data_vencimento=equipamento.data_vencimento,
        observacoes=equipamento.observacoes
    )
    
    db.add(db_equipamento)
    db.commit()
    db.refresh(db_equipamento)
    
    return equipamento_to_response(db_equipamento)


@router.put("/{equipamento_id}", response_model=EquipamentoResponse)
async def atualizar_equipamento(
    equipamento_id: int,
    equipamento: EquipamentoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Update equipment
    """
    db_equipamento = db.query(Equipamento).filter(Equipamento.id == equipamento_id).first()
    if not db_equipamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipamento não encontrado"
        )
    
    # Check for duplicate code if changing
    if equipamento.codigo_interno and equipamento.codigo_interno != db_equipamento.codigo_interno:
        existing = db.query(Equipamento).filter(
            Equipamento.codigo_interno == equipamento.codigo_interno
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um equipamento com este código interno"
            )
    
    # Update fields
    update_data = equipamento.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_equipamento, field, value)
    
    db.commit()
    db.refresh(db_equipamento)
    
    return equipamento_to_response(db_equipamento)


@router.delete("/{equipamento_id}")
async def deletar_equipamento(
    equipamento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Soft delete equipment (set as inactive)
    """
    db_equipamento = db.query(Equipamento).filter(Equipamento.id == equipamento_id).first()
    if not db_equipamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipamento não encontrado"
        )
    
    db_equipamento.ativo = False
    db.commit()
    
    return {"message": "Equipamento desativado com sucesso"}


@router.post("/{equipamento_id}/registrar-calibracao", response_model=EquipamentoResponse)
async def registrar_calibracao(
    equipamento_id: int,
    data_calibracao: date,
    data_novo_vencimento: date,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Register a new calibration for equipment
    """
    db_equipamento = db.query(Equipamento).filter(Equipamento.id == equipamento_id).first()
    if not db_equipamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipamento não encontrado"
        )
    
    db_equipamento.data_ultima_calibracao = data_calibracao
    db_equipamento.data_vencimento = data_novo_vencimento
    
    db.commit()
    db.refresh(db_equipamento)
    
    return equipamento_to_response(db_equipamento)
