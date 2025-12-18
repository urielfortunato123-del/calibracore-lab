"""
CalibraCore Lab - Pydantic Schemas
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


# ============= Enums =============

class UserRole(str, Enum):
    LABORATORIO = "laboratorio"
    ADMIN = "admin"


class EquipmentStatus(str, Enum):
    EM_DIA = "em_dia"
    PROXIMO_60 = "proximo_60"
    PROXIMO_30 = "proximo_30"
    VENCIDO = "vencido"


# ============= Auth Schemas =============

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


# ============= User Schemas =============

class UsuarioBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    papel: UserRole = UserRole.LABORATORIO
    laboratorio: Optional[str] = None


class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6)


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    papel: Optional[UserRole] = None
    laboratorio: Optional[str] = None
    ativo: Optional[bool] = None
    senha: Optional[str] = Field(None, min_length=6)


class UsuarioResponse(UsuarioBase):
    id: int
    ativo: bool
    criado_em: datetime
    
    class Config:
        from_attributes = True


class UsuarioMe(BaseModel):
    id: int
    nome: str
    email: str
    papel: UserRole
    laboratorio: Optional[str]
    
    class Config:
        from_attributes = True


# ============= Equipment Schemas =============

class EquipamentoBase(BaseModel):
    codigo_interno: str = Field(..., min_length=1, max_length=50)
    descricao: str = Field(..., min_length=2, max_length=200)
    categoria: Optional[str] = None  # Ex: Peneiras, Balanças, Termômetros
    marca: Optional[str] = None  # Ex: Solotest, Marte, Delta
    numero_certificado: Optional[str] = None  # Ex: 82512-25
    numero_serie: Optional[str] = None
    laboratorio: str = Field(..., min_length=1, max_length=100)
    data_ultima_calibracao: Optional[date] = None
    data_vencimento: date
    observacoes: Optional[str] = None
    email_contato: Optional[str] = None
    telefone_contato: Optional[str] = None
    notificar_automaticamente: bool = True


class EquipamentoCreate(EquipamentoBase):
    responsavel_id: Optional[int] = None


class EquipamentoUpdate(BaseModel):
    codigo_interno: Optional[str] = Field(None, max_length=50)
    descricao: Optional[str] = Field(None, max_length=200)
    categoria: Optional[str] = None
    marca: Optional[str] = None
    numero_certificado: Optional[str] = None
    numero_serie: Optional[str] = None
    laboratorio: Optional[str] = Field(None, max_length=100)
    responsavel_id: Optional[int] = None
    data_ultima_calibracao: Optional[date] = None
    data_vencimento: Optional[date] = None
    observacoes: Optional[str] = None
    email_contato: Optional[str] = None
    telefone_contato: Optional[str] = None
    notificar_automaticamente: Optional[bool] = None
    ativo: Optional[bool] = None


class EquipamentoResponse(EquipamentoBase):
    id: int
    responsavel_id: Optional[int]
    categoria: Optional[str] = None
    marca: Optional[str] = None
    numero_certificado: Optional[str] = None
    caminho_certificado: Optional[str] = None
    status: EquipmentStatus
    dias_para_vencer: int
    ativo: bool
    criado_em: datetime
    responsavel_nome: Optional[str] = None
    email_contato: Optional[str] = None
    telefone_contato: Optional[str] = None
    notificar_automaticamente: bool
    
    class Config:
        from_attributes = True


class EquipamentoListResponse(BaseModel):
    items: List[EquipamentoResponse]
    total: int
    page: int
    pages: int


# ============= Dashboard Schemas =============

class DashboardResumo(BaseModel):
    total: int
    em_dia: int
    vence_60_dias: int
    vence_30_dias: int
    vencidos: int


# ============= Alert Schemas =============

class AlertaResponse(BaseModel):
    id: int
    equipamento_id: int
    equipamento_codigo: Optional[str] = None
    equipamento_descricao: Optional[str] = None
    tipo_alerta: str
    data_envio: datetime
    destinatarios: Optional[str]
    sucesso: bool
    
    class Config:
        from_attributes = True


class ProcessarAlertasResponse(BaseModel):
    processados: int
    alertas_enviados: int
    erros: int
    detalhes: List[dict]


# ============= Audit Schemas =============

class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    table_name: str
    record_id: int
    timestamp: datetime
    changes: Optional[str] = None
    user_nome: Optional[str] = None

    class Config:
        from_attributes = True

