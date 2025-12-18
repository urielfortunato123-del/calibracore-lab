"""
CalibraCore Lab - Equipment Router
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from app.services.audit import log_action
from app.services.notification import alert_expiration
from app.auth import require_admin
from fastapi.responses import StreamingResponse, FileResponse
import os
import shutil
from uuid import uuid4
from app.services.export import generate_excel_report, generate_pdf_report
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
        "responsavel_nome": eq.responsavel_usuario.nome if eq.responsavel_usuario else None,
        "caminho_certificado": eq.caminho_certificado,
        "email_contato": eq.email_contato,
        "telefone_contato": eq.telefone_contato,
        "notificar_automaticamente": eq.notificar_automaticamente
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
    current_user: Usuario = Depends(require_admin)
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
        observacoes=equipamento.observacoes,
        email_contato=equipamento.email_contato,
        telefone_contato=equipamento.telefone_contato,
        notificar_automaticamente=equipamento.notificar_automaticamente
    )
    
    db.add(db_equipamento)
    db.commit()
    db.refresh(db_equipamento)
    # Audit log for creation
    log_action(db, current_user.id, "CREATE", "equipamentos", db_equipamento.id, {
        "codigo_interno": db_equipamento.codigo_interno,
        "descricao": db_equipamento.descricao,
    })
    # Determine recipients
    emails = ["admin@example.com"]
    whatsapps = ["whatsapp:+1234567890"]
    
    if db_equipamento.email_contato:
        emails.append(db_equipamento.email_contato)
    if db_equipamento.telefone_contato:
        # Ensure 'whatsapp:' prefix if using Twilio
        num = db_equipamento.telefone_contato
        if not num.startswith("whatsapp:"):
            num = f"whatsapp:{num}"
        whatsapps.append(num)

    # Send alerts after creation
    if db_equipamento.notificar_automaticamente:
        await alert_expiration(db_equipamento, emails, whatsapps)

    return equipamento_to_response(db_equipamento)


@router.put("/{equipamento_id}", response_model=EquipamentoResponse)
async def atualizar_equipamento(
    equipamento_id: int,
    equipamento: EquipamentoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
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
    # Audit log for update (capture changed fields)
    log_action(db, current_user.id, "UPDATE", "equipamentos", db_equipamento.id, update_data)
    # Determine recipients
    emails = ["admin@example.com"]
    whatsapps = ["whatsapp:+1234567890"]
    
    if db_equipamento.email_contato:
        emails.append(db_equipamento.email_contato)
    if db_equipamento.telefone_contato:
        num = db_equipamento.telefone_contato
        if not num.startswith("whatsapp:"):
            num = f"whatsapp:{num}"
        whatsapps.append(num)

    # Send alerts after update
    if db_equipamento.notificar_automaticamente:
        await alert_expiration(db_equipamento, emails, whatsapps)

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
    # Audit log for delete (soft)
    log_action(db, current_user.id, "DELETE", "equipamentos", db_equipamento.id, None)
    # Send alert for deletion if needed (optional)
    await alert_expiration(db_equipamento, ["admin@example.com"], ["whatsapp:+1234567890"])

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


@router.get("/export/excel")
async def exportar_excel(
    laboratorio: Optional[str] = None,
    categoria: Optional[str] = None,
    status: Optional[str] = None,
    busca: Optional[str] = None,
    ativo: bool = True,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Export equipment list to Excel
    """
    query = db.query(Equipamento).filter(Equipamento.ativo == ativo)
    
    if laboratorio:
        query = query.filter(Equipamento.laboratorio == laboratorio)
    
    if categoria:
        query = query.filter(Equipamento.categoria == categoria)
    
    if busca:
        search_term = f"%{busca}%"
        query = query.filter(
            or_(
                Equipamento.codigo_interno.ilike(search_term),
                Equipamento.descricao.ilike(search_term),
                Equipamento.numero_serie.ilike(search_term)
            )
        )
    
    all_results = query.all()
    
    if status:
        status_enum = EquipmentStatus(status)
        all_results = [eq for eq in all_results if eq.status == status_enum]
    
    all_results.sort(key=lambda x: x.data_vencimento or date.max)
    
    report_stream = generate_excel_report(all_results)
    
    return StreamingResponse(
        report_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=equipamentos.xlsx"}
    )


@router.get("/export/pdf")
async def exportar_pdf(
    laboratorio: Optional[str] = None,
    categoria: Optional[str] = None,
    status: Optional[str] = None,
    busca: Optional[str] = None,
    ativo: bool = True,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Export equipment list to PDF
    """
    query = db.query(Equipamento).filter(Equipamento.ativo == ativo)
    
    if laboratorio:
        query = query.filter(Equipamento.laboratorio == laboratorio)
    
    if categoria:
        query = query.filter(Equipamento.categoria == categoria)
    
    if busca:
        search_term = f"%{busca}%"
        query = query.filter(
            or_(
                Equipamento.codigo_interno.ilike(search_term),
                Equipamento.descricao.ilike(search_term),
                Equipamento.numero_serie.ilike(search_term)
            )
        )
    
    all_results = query.all()
    
    if status:
        status_enum = EquipmentStatus(status)
        all_results = [eq for eq in all_results if eq.status == status_enum]
    
    all_results.sort(key=lambda x: x.data_vencimento or date.max)
    
    report_stream = generate_pdf_report(all_results)
    
    return StreamingResponse(
        report_stream,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=equipamentos.pdf"}
    )


@router.post("/{equipamento_id}/comprovante", response_model=EquipamentoResponse)
async def upload_comprovante(
    equipamento_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Upload calibration certificate PDF
    """
    import logging
    logger = logging.getLogger(__name__)

    db_equipamento = db.query(Equipamento).filter(Equipamento.id == equipamento_id).first()
    if not db_equipamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipamento não encontrado"
        )
    
    # Validate file type (case insensitive)
    content_type = file.content_type.lower() if file.content_type else ""
    if content_type != "application/pdf":
        logger.warning(f"Tentativa de upload de arquivo inválido: {content_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Apenas arquivos PDF são permitidos. Recebido: {content_type}"
        )
    
    try:
        # Create valid filename
        filename = f"{equipamento_id}_{uuid4().hex}.pdf"
        
        # Use relative upload directory for server compatibility (Project Root / uploads)
        base_upload_dir = os.path.join(os.getcwd(), "uploads")
        
        # Ensure directory exists
        os.makedirs(base_upload_dir, exist_ok=True)
        
        file_path = os.path.join(base_upload_dir, filename)
        
        logger.info(f"Salvando certificado em: {file_path}")
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Remove old file if exists
        if db_equipamento.caminho_certificado and os.path.exists(db_equipamento.caminho_certificado):
            try:
                os.remove(db_equipamento.caminho_certificado)
                logger.info(f"Certificado antigo removido: {db_equipamento.caminho_certificado}")
            except Exception as e:
                logger.error(f"Erro ao remover certificado antigo: {e}")
                
        # Update DB
        db_equipamento.caminho_certificado = file_path
        
        db.commit()
        db.refresh(db_equipamento)
        
        return equipamento_to_response(db_equipamento)
        
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar arquivo: {str(e)}"
        )


@router.get("/{equipamento_id}/comprovante")
async def download_comprovante(
    equipamento_id: int,
    db: Session = Depends(get_db)
):
    """
    Download calibration certificate PDF
    """
    db_equipamento = db.query(Equipamento).filter(Equipamento.id == equipamento_id).first()
    if not db_equipamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipamento não encontrado"
        )
        
    if not db_equipamento.caminho_certificado or not os.path.exists(db_equipamento.caminho_certificado):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificado não encontrado ainda"
        )
        
    return FileResponse(
        db_equipamento.caminho_certificado,
        media_type="application/pdf",
        filename=f"certificado_{db_equipamento.codigo_interno}.pdf",
        content_disposition_type="inline"
    )


@router.post("/{equipamento_id}/alerta/manual", status_code=status.HTTP_200_OK)
async def enviar_alerta_manual(
    equipamento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Manually trigger an alert for this equipment
    """
    db_equipamento = db.query(Equipamento).filter(Equipamento.id == equipamento_id).first()
    if not db_equipamento:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")
    
    # Determine recipients
    emails = ["admin@example.com"]
    whatsapps = ["whatsapp:+1234567890"]
    
    if db_equipamento.email_contato:
        emails.append(db_equipamento.email_contato)
    if db_equipamento.telefone_contato:
        num = db_equipamento.telefone_contato
        if not num.startswith("whatsapp:"):
            num = f"whatsapp:{num}"
        whatsapps.append(num)
        
    # Force alert regardless of date
    # We call a simplified version or reuse alert_expiration but forcing a body
    # Since alert_expiration logic depends on days, let's reuse it but maybe pass a flag?
    # Or just construct message here. For simplicity, let's call alert_expiration.
    # If the equipment is NOT expiring soon, alert_expiration currently returns None (does nothing).
    # We should probably force a message.
    
    # Let's verify days first.
    days = db_equipamento.dias_para_vencer
    
    if days > 60:
         # Force a "Manual Reminder"
        from app.services.notification import send_email, send_whatsapp
        subject = f"🔔 [Manual] Lembrete de Equipamento: {db_equipamento.codigo_interno}"
        body = f"Olá, este é um lembrete manual sobre o equipamento {db_equipamento.codigo_interno} ({db_equipamento.descricao}). Vencimento: {db_equipamento.data_vencimento}."
        
        await send_email(emails, subject, body)
        for num in whatsapps:
            await send_whatsapp(num, body)
            
        return {"message": "Alerta manual enviado com sucesso (Vencimento distante)"}
    else:
        # Use standard logic if it is already in warning period
        await alert_expiration(db_equipamento, emails, whatsapps)
        return {"message": "Alerta manual enviado com sucesso (Baseado no vencimento)"}

