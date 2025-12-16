"""
CalibraCore Lab - Configurações do Sistema
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "CalibraCore Lab"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./calibracore.db"
    
    # Security
    SECRET_KEY: str = "calibracore-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Email SMTP Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@calibracore.lab"
    SMTP_FROM_NAME: str = "CalibraCore Lab"
    SMTP_TLS: bool = True
    
    # Alert Recipients (comma-separated emails)
    ALERT_RECIPIENTS: str = ""
    
    # Admin padrão
    ADMIN_EMAIL: str = "admin@calibracore.lab"
    ADMIN_PASSWORD: str = "admin123"
    ADMIN_NAME: str = "Administrador"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
