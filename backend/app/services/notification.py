import os
import logging
from typing import List
from datetime import datetime
from aiosmtplib import SMTP, SMTPException
from twilio.rest import Client as TwilioClient
import pyttsx3

logger = logging.getLogger(__name__)

# Email configuration (expects env vars)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.example.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "user@example.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "password")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)

# Twilio configuration (expects env vars)
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")  # e.g., 'whatsapp:+14155238886'

# Voice engine initialization (offline)
engine = pyttsx3.init()
engine.setProperty('rate', 150)

async def send_email(to: List[str], subject: str, body: str) -> bool:
    """Send an email to a list of recipients.
    Returns True on success, False otherwise.
    """
    message = f"From: {FROM_EMAIL}\nTo: {', '.join(to)}\nSubject: {subject}\n\n{body}"
    try:
        smtp = SMTP(hostname=SMTP_HOST, port=SMTP_PORT, use_tls=False)
        await smtp.connect()
        await smtp.starttls()
        await smtp.login(SMTP_USER, SMTP_PASSWORD)
        await smtp.sendmail(FROM_EMAIL, to, message)
        await smtp.quit()
        logger.info(f"Email sent to {to}")
        return True
    except SMTPException as e:
        logger.error(f"Failed to send email: {e}")
        return False

async def send_whatsapp(to_number: str, message: str) -> bool:
    """Send a WhatsApp message using Twilio.
    `to_number` must be in the format 'whatsapp:+1234567890'.
    """
    if not all([TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER]):
        logger.warning("Twilio credentials not configured; skipping WhatsApp alert.")
        return False
    try:
        client = TwilioClient(TWILIO_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(body=message, from_=TWILIO_WHATSAPP_NUMBER, to=to_number)
        logger.info(f"WhatsApp message sent to {to_number}")
        return True
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message: {e}")
        return False

def send_voice_alert(message: str) -> bool:
    """Play a voice alert on the server (useful for local deployments)."""
    try:
        engine.say(message)
        engine.runAndWait()
        logger.info("Voice alert played.")
        return True
    except Exception as e:
        logger.error(f"Voice alert failed: {e}")
        return False

async def alert_expiration(equipment, recipients_email: List[str], recipients_whatsapp: List[str]):
    """Determine alert level based on days to expiration and send notifications.
    `equipment` is an instance of Equipamento model.
    """
    days = equipment.dias_para_vencer
    if days < 0:
        level = "VENCIDO"
        subject = f"⚠️ Equipamento vencido: {equipment.codigo_interno}"
        body = f"O equipamento {equipment.codigo_interno} ({equipment.descricao}) está vencido desde {equipment.data_vencimento}."
    elif days <= 7:
        level = "URGENTE"
        subject = f"⏰ Aviso urgente: equipamento próximo ao vencimento ({days} dias)"
        body = f"O equipamento {equipment.codigo_interno} vence em {days} dias ({equipment.data_vencimento})."
    elif days <= 15:
        level = "LEMBRETE"
        subject = f"🔔 Lembrete: equipamento vence em {days} dias"
        body = f"O equipamento {equipment.codigo_interno} ({equipment.descricao}) vence em {days} dias ({equipment.data_vencimento})."
    else:
        return  # No alert needed

    # Send email
    await send_email(recipients_email, subject, body)
    # Send WhatsApp for each number
    for num in recipients_whatsapp:
        await send_whatsapp(num, body)
    # Voice alert (optional)
    send_voice_alert(body)
