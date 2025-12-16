# CalibraCore Lab

Sistema Inteligente de Controle de Vencimento de Calibração de Equipamentos

## 🚀 Início Rápido

### Requisitos
- Python 3.9+
- Node.js (opcional, para desenvolvimento)

### Instalação

1. **Backend:**
```bash
cd backend
pip install -r requirements.txt
python run.py
```

2. **Acesse:** http://localhost:8000

### Login Padrão
- **Email:** admin@calibracore.lab
- **Senha:** admin123

## 📁 Estrutura

```
CalibraCore Lab/
├── backend/           # API FastAPI + SQLite
├── frontend/          # Interface Web
└── scripts/           # Automação
```

## 📋 Funcionalidades

- ✅ Dashboard com cards de status
- ✅ Cadastro de equipamentos
- ✅ Alertas automáticos por e-mail
- ✅ Controle de acesso por perfil

## 🔔 Regras de Alertas

| Dias para Vencer | Frequência |
|------------------|------------|
| 60 dias | Alerta inicial |
| 59-31 dias | A cada 15 dias |
| 30-0 dias | Semanal |
| Vencido | Semanal até regularizar |

## 📧 Configuração de E-mail

Edite `backend/app/config.py` com suas credenciais SMTP.

## 📜 Licença

Projeto interno - CalibraCore Lab
