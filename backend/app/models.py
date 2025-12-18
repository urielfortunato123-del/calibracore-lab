"""
CalibraCore Lab - Database Models
"""
from datetime import datetime, date
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(str, PyEnum):
    """User roles for access control"""
    LABORATORIO = "laboratorio"
    ADMIN = "admin"


class EquipmentStatus(str, PyEnum):
    """Equipment calibration status"""
    EM_DIA = "em_dia"
    PROXIMO_60 = "proximo_60"
    PROXIMO_30 = "proximo_30"
    VENCIDO = "vencido"


class Usuario(Base):
    """User model for authentication and authorization"""
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    papel = Column(Enum(UserRole), default=UserRole.LABORATORIO, nullable=False)
    laboratorio = Column(String(100), nullable=True)  # Laboratório do usuário
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    equipamentos = relationship("Equipamento", back_populates="responsavel_usuario")


class Equipamento(Base):
    """Equipment model for calibration tracking"""
    __tablename__ = "equipamentos"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo_interno = Column(String(50), unique=True, index=True, nullable=False)
    descricao = Column(String(200), nullable=False)
    categoria = Column(String(100), nullable=True, index=True)  # Ex: Peneiras, Balanças, Termômetros
    marca = Column(String(100), nullable=True)  # Ex: Solotest, Marte, Delta
    numero_certificado = Column(String(100), nullable=True)  # Ex: 82512-25
    numero_serie = Column(String(100), nullable=True)
    laboratorio = Column(String(100), nullable=False)
    responsavel_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    data_ultima_calibracao = Column(Date, nullable=True)
    data_vencimento = Column(Date, nullable=False)
    observacoes = Column(Text, nullable=True)
    caminho_certificado = Column(String(500), nullable=True)  # Path to PDF file
    
    # Notification fields
    email_contato = Column(String(100), nullable=True)
    telefone_contato = Column(String(20), nullable=True)  # WhatsApp
    notificar_automaticamente = Column(Boolean, default=True)

    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    responsavel_usuario = relationship("Usuario", back_populates="equipamentos")
    alertas = relationship("AlertaEnviado", back_populates="equipamento")
    
    @property
    def status(self) -> EquipmentStatus:
        """Calculate current status based on expiration date"""
        if not self.data_vencimento:
            return EquipmentStatus.EM_DIA
        
        hoje = date.today()
        dias_para_vencer = (self.data_vencimento - hoje).days
        
        if dias_para_vencer < 0:
            return EquipmentStatus.VENCIDO
        elif dias_para_vencer <= 30:
            return EquipmentStatus.PROXIMO_30
        elif dias_para_vencer <= 60:
            return EquipmentStatus.PROXIMO_60
        else:
            return EquipmentStatus.EM_DIA
    
    @property
    def dias_para_vencer(self) -> int:
        """Days until calibration expires"""
        if not self.data_vencimento:
            return 999
        return (self.data_vencimento - date.today()).days


class AlertaEnviado(Base):
    """Alert history tracking"""
    __tablename__ = "alertas_enviados"
    
    id = Column(Integer, primary_key=True, index=True)
    equipamento_id = Column(Integer, ForeignKey("equipamentos.id"), nullable=False)
    tipo_alerta = Column(String(50), nullable=False)  # inicial_60, lembrete_15, urgente_7, vencido
    data_envio = Column(DateTime, default=datetime.utcnow)
    destinatarios = Column(Text, nullable=True)  # JSON list of emails
    sucesso = Column(Boolean, default=True)
    mensagem_erro = Column(Text, nullable=True)
    
    # Relationships
    equipamento = relationship("Equipamento", back_populates="alertas")
class AuditLog(Base):
    """Audit log for tracking create, update, delete actions on models"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    action = Column(String(20), nullable=False)  # CREATE, UPDATE, DELETE
    table_name = Column(String(50), nullable=False)
    record_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    changes = Column(Text, nullable=True)  # JSON string of changed fields

    user = relationship("Usuario")
