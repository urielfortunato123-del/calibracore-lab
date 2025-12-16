"""
CalibraCore Lab - Email Service
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


async def send_email(
    to_emails: List[str],
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """
    Send email via SMTP
    Returns True if successful, False otherwise
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP não configurado. E-mail não enviado.")
        return False
    
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        message["To"] = ", ".join(to_emails)
        
        # Add text and HTML parts
        if text_content:
            message.attach(MIMEText(text_content, "plain"))
        message.attach(MIMEText(html_content, "html"))
        
        # Send email
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=settings.SMTP_TLS
        )
        
        logger.info(f"E-mail enviado para: {', '.join(to_emails)}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail: {str(e)}")
        return False


def get_alert_email_html(
    equipamento_codigo: str,
    equipamento_descricao: str,
    laboratorio: str,
    data_vencimento: str,
    dias_restantes: int,
    tipo_alerta: str
) -> str:
    """
    Generate HTML email for calibration alert
    """
    # Determine color and urgency
    if dias_restantes < 0:
        cor = "#dc3545"  # Red
        urgencia = "🔴 VENCIDO"
        mensagem = f"O equipamento está com a calibração VENCIDA há {abs(dias_restantes)} dias!"
    elif dias_restantes <= 30:
        cor = "#fd7e14"  # Orange
        urgencia = "🟠 URGENTE"
        mensagem = f"Restam apenas {dias_restantes} dias para o vencimento!"
    elif dias_restantes <= 60:
        cor = "#ffc107"  # Yellow
        urgencia = "🟡 ATENÇÃO"
        mensagem = f"A calibração vence em {dias_restantes} dias."
    else:
        cor = "#28a745"  # Green
        urgencia = "🟢 AVISO"
        mensagem = f"A calibração vence em {dias_restantes} dias."
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f8f9fa; padding: 30px; border: 1px solid #ddd; }}
            .alert-badge {{ display: inline-block; background: {cor}; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 18px; }}
            .info-table {{ width: 100%; margin: 20px 0; }}
            .info-table td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
            .info-table td:first-child {{ font-weight: bold; width: 40%; }}
            .footer {{ background: #1e3a5f; color: white; padding: 15px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; }}
            .btn {{ display: inline-block; background: #2d5a87; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⚗️ CalibraCore Lab</h1>
                <p>Sistema de Controle de Calibração</p>
            </div>
            <div class="content">
                <div style="text-align: center; margin-bottom: 20px;">
                    <span class="alert-badge">{urgencia}</span>
                </div>
                
                <p style="font-size: 16px; text-align: center;">{mensagem}</p>
                
                <table class="info-table">
                    <tr>
                        <td>Código:</td>
                        <td><strong>{equipamento_codigo}</strong></td>
                    </tr>
                    <tr>
                        <td>Descrição:</td>
                        <td>{equipamento_descricao}</td>
                    </tr>
                    <tr>
                        <td>Laboratório:</td>
                        <td>{laboratorio}</td>
                    </tr>
                    <tr>
                        <td>Data de Vencimento:</td>
                        <td><strong style="color: {cor};">{data_vencimento}</strong></td>
                    </tr>
                </table>
                
                <p style="text-align: center;">
                    Por favor, providencie a recalibração o mais breve possível.
                </p>
            </div>
            <div class="footer">
                <p>Este é um e-mail automático do CalibraCore Lab.</p>
                <p>Não responda a este e-mail.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html
