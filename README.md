# CalibraCore Lab

Sistema Inteligente de Controle de Vencimento de Calibração de Equipamentos

> **Novidades (v2.0):**
> - 🔐 **Auditoria Completa:** Rastreio de quem criou, editou ou excluiu registros.
> - 👤 **Perfis de Acesso:** Admin (total) e Laboratório (restrito).
> - 📢 **Notificações:** Alertas via E-mail, WhatsApp e Voz.
> - 📱 **Contatos:** Cadastro de email/whatsapp por equipamento.

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
- ✅ **Logs de Auditoria** (Novo)
- ✅ **Alertas via WhatsApp e Voz** (Novo)
- ✅ **Envio de Alerta Manual** (Novo)

## 🔔 Regras de Alertas

| Dias para Vencer | Frequência |
|------------------|------------|
| 60 dias | Alerta inicial |
| 59-31 dias | A cada 15 dias |
| 30-0 dias | Semanal |
| Vencido | Semanal até regularizar |

## 📧 Configuração de E-mail

Edite `backend/.env` com suas credenciais:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu@email.com
SMTP_PASSWORD=sua_senha
TWILIO_SID=seu_sid
TWILIO_AUTH_TOKEN=seu_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

## 📜 Licença

Projeto interno - CalibraCore Lab
