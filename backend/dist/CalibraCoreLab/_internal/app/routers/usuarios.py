"""
CalibraCore Lab - Users Router
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user, require_admin, get_password_hash
from app.models import Usuario, UserRole
from app.schemas import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse
)

router = APIRouter(prefix="/api/usuarios", tags=["Usuários"])


@router.get("", response_model=List[UsuarioResponse])
async def listar_usuarios(
    ativo: Optional[bool] = None,
    papel: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    List all users (Admin only)
    """
    query = db.query(Usuario)
    
    if ativo is not None:
        query = query.filter(Usuario.ativo == ativo)
    
    if papel:
        query = query.filter(Usuario.papel == UserRole(papel))
    
    return query.order_by(Usuario.nome).all()


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def obter_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Get user by ID (Admin only)
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return usuario


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def criar_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Create new user (Admin only)
    """
    # Check for duplicate email
    existing = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um usuário com este e-mail"
        )
    
    db_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=get_password_hash(usuario.senha),
        papel=usuario.papel,
        laboratorio=usuario.laboratorio
    )
    
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def atualizar_usuario(
    usuario_id: int,
    usuario: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Update user (Admin only)
    """
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Check for duplicate email if changing
    if usuario.email and usuario.email != db_usuario.email:
        existing = db.query(Usuario).filter(Usuario.email == usuario.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um usuário com este e-mail"
            )
    
    # Update fields
    update_data = usuario.model_dump(exclude_unset=True)
    
    # Hash password if provided
    if "senha" in update_data:
        update_data["senha_hash"] = get_password_hash(update_data.pop("senha"))
    
    for field, value in update_data.items():
        setattr(db_usuario, field, value)
    
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario


@router.delete("/{usuario_id}")
async def deletar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Soft delete user (Admin only)
    """
    if usuario_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode desativar seu próprio usuário"
        )
    
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    db_usuario.ativo = False
    db.commit()
    
    return {"message": "Usuário desativado com sucesso"}
