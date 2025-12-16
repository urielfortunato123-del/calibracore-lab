"""
CalibraCore Lab - Alert Service
Logic for processing calibration expiration alerts
"""
from datetime import date, datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import logging
import json

from app.models import Equipamento, AlertaEnviado
from app.config import settings
from app.services.email_service import send_email, get_alert_email_html

logger = logging.getLogger(__name__)


def should_send_alert(dias_para_vencer: int, tipo_alerta: str) -> bool:
    """
    Determine if an alert should be sent based on the number of days until expiration
    
    Rules:
    - 60 days: Initial alert
    - 59-30 days: Every 15 days
    - 30-0 days: Weekly
    - Vencido (< 0): Weekly
    """
    if dias_para_vencer == 60:
        return tipo_alerta == "inicial_60"
    
    elif 30 < dias_para_vencer < 60:
        # Every 15 days: at days 45, 30
        if (60 - dias_para_vencer) % 15 == 0:
            return tipo_alerta == "lembrete_15"
        return False
    
    elif 0 <= dias_para_vencer <= 30:
        # Weekly: at days 28, 21, 14, 7, 0
        if dias_para_vencer % 7 == 0:
            return tipo_alerta == "urgente_7"
        return False
    
    elif dias_para_vencer < 0:
        # Expired: weekly reminders
        if abs(dias_para_vencer) % 7 == 0:
            return tipo_alerta == "vencido"
        return False
    
    return False


def get_alert_type(dias_para_vencer: int) -> Optional[str]:
    """
    Get the alert type based on days until expiration
    """
    if dias_para_vencer == 60:
        return "inicial_60"
    elif 30 < dias_para_vencer < 60:
        if (60 - dias_para_vencer) % 15 == 0:
            return "lembrete_15"
    elif 0 <= dias_para_vencer <= 30:
        if dias_para_vencer % 7 == 0:
            return "urgente_7"
    elif dias_para_vencer < 0:
        if abs(dias_para_vencer) % 7 == 0:
            return "vencido"
    return None


def was_alert_sent_today(db: Session, equipamento_id: int, tipo_alerta: str) -> bool:
    """
    Check if an alert of this type was already sent today for this equipment
    """
    hoje = date.today()
    alerta = db.query(AlertaEnviado).filter(
        AlertaEnviado.equipamento_id == equipamento_id,
        AlertaEnviado.tipo_alerta == tipo_alerta,
        AlertaEnviado.data_envio >= datetime.combine(hoje, datetime.min.time()),
        AlertaEnviado.data_envio < datetime.combine(hoje, datetime.max.time())
    ).first()
    return alerta is not None


async def process_alerts(db: Session) -> Dict:
    """
    Process all equipment and send alerts as needed
    Returns a summary of actions taken
    """
    # Get all active equipment
    equipamentos = db.query(Equipamento).filter(Equipamento.ativo == True).all()
    
    # Get alert recipients
    recipients = []
    if settings.ALERT_RECIPIENTS:
        recipients = [email.strip() for email in settings.ALERT_RECIPIENTS.split(",")]
    
    results = {
        "processados": len(equipamentos),
        "alertas_enviados": 0,
        "erros": 0,
        "detalhes": []
    }
    
    for eq in equipamentos:
        dias = eq.dias_para_vencer
        tipo_alerta = get_alert_type(dias)
        
        if tipo_alerta is None:
            continue
        
        # Check if alert was already sent today
        if was_alert_sent_today(db, eq.id, tipo_alerta):
            logger.debug(f"Alerta já enviado hoje para {eq.codigo_interno}")
            continue
        
        # Prepare recipient list (equipment responsible + configured recipients)
        email_list = list(recipients)
        if eq.responsavel_usuario and eq.responsavel_usuario.email:
            if eq.responsavel_usuario.email not in email_list:
                email_list.append(eq.responsavel_usuario.email)
        
        if not email_list:
            logger.warning(f"Nenhum destinatário configurado para {eq.codigo_interno}")
            results["detalhes"].append({
                "equipamento": eq.codigo_interno,
                "status": "sem_destinatarios",
                "tipo_alerta": tipo_alerta
            })
            continue
        
        # Generate and send email
        data_vencimento_str = eq.data_vencimento.strftime("%d/%m/%Y")
        html_content = get_alert_email_html(
            equipamento_codigo=eq.codigo_interno,
            equipamento_descricao=eq.descricao,
            laboratorio=eq.laboratorio,
            data_vencimento=data_vencimento_str,
            dias_restantes=dias,
            tipo_alerta=tipo_alerta
        )
        
        # Determine subject based on alert type
        if tipo_alerta == "inicial_60":
            subject = f"[CalibraCore] Aviso: Calibração vence em 60 dias - {eq.codigo_interno}"
        elif tipo_alerta == "lembrete_15":
            subject = f"[CalibraCore] Lembrete: Calibração vence em {dias} dias - {eq.codigo_interno}"
        elif tipo_alerta == "urgente_7":
            subject = f"[CalibraCore] URGENTE: Calibração vence em {dias} dias - {eq.codigo_interno}"
        else:  # vencido
            subject = f"[CalibraCore] ⚠️ VENCIDO: Calibração expirada - {eq.codigo_interno}"
        
        # Send email
        success = await send_email(
            to_emails=email_list,
            subject=subject,
            html_content=html_content
        )
        
        # Record alert
        alerta = AlertaEnviado(
            equipamento_id=eq.id,
            tipo_alerta=tipo_alerta,
            destinatarios=json.dumps(email_list),
            sucesso=success,
            mensagem_erro=None if success else "Falha no envio do e-mail"
        )
        db.add(alerta)
        
        if success:
            results["alertas_enviados"] += 1
            results["detalhes"].append({
                "equipamento": eq.codigo_interno,
                "status": "enviado",
                "tipo_alerta": tipo_alerta,
                "destinatarios": email_list
            })
            logger.info(f"Alerta {tipo_alerta} enviado para {eq.codigo_interno}")
        else:
            results["erros"] += 1
            results["detalhes"].append({
                "equipamento": eq.codigo_interno,
                "status": "erro",
                "tipo_alerta": tipo_alerta
            })
            logger.error(f"Falha ao enviar alerta para {eq.codigo_interno}")
    
    db.commit()
    return results
