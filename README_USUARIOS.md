# 🚀 Configuração de Usuários - CalibraCore Lab

## Usuários Iniciais Criados ✅

O sistema foi configurado com **4 usuários administradores**:

1. **Letícia Silveira** (Motiva)
2. **André Pereira** (Motiva)  
3. **Alan Silva** (Núcleo Engenharia)
4. **Fabiano Silva** (Núcleo Engenharia)

> [!IMPORTANT]
> As credenciais completas estão no arquivo `CREDENCIAIS_USUARIOS.md` (arquivo protegido - não será enviado ao GitHub).

---

## 📋 Para Subir no Servidor

### 1. No servidor, execute:

```bash
cd backend
python init_users.py
```

Este script irá:
- ✅ Criar as tabelas do banco de dados automaticamente
- ✅ Adicionar os 4 usuários administradores
- ✅ Criptografar as senhas com Argon2
- ✅ Ativar todos os usuários

---

## 🔐 Segurança Implementada

### Arquivos Protegidos no `.gitignore`:
- `CREDENCIAIS_USUARIOS.md` - Lista de credenciais
- `backend/init_users.py` - Script de inicialização
- Qualquer arquivo com `*credentials*` ou `*CREDENCIAIS*`

### Hash de Senhas:
- ✅ Todas as senhas são criptografadas com **Argon2**
- ✅ Impossível recuperar senha original do banco
- ✅ Proteção contra ataques de força bruta

---

## 📁 Arquivos Criados

| Arquivo | Localização | Descrição |
|---------|-------------|-----------|
| `init_users.py` | `/backend/` | Script para inicializar usuários |
| `CREDENCIAIS_USUARIOS.md` | `/` | Lista de emails e senhas |
| `.gitignore` | `/` | Atualizado para proteger credenciais |

---

## ⚠️ Importante para Deploy

### Antes de Fazer Git Push:

```bash
# Verificar se arquivos sensíveis estão ignorados
git status

# Se aparecer CREDENCIAIS_USUARIOS.md ou init_users.py, NÃO COMMITAR!
```

### No Servidor (após git pull):

1. Copiar manualmente os arquivos:
   - `CREDENCIAIS_USUARIOS.md`
   - `backend/init_users.py`

2. Executar a inicialização:
   ```bash
   cd backend
   python init_users.py
   ```

3. Guardar o arquivo `CREDENCIAIS_USUARIOS.md` em local seguro

---

## 🧪 Testar Login

Após inicialização, você pode fazer login com qualquer um dos 4 usuários:

**Exemplo:**
- Email: `leticia.silveira@motiva.com.br`
- Senha: `MotivaLeti9`

---

**Data:** 2025-12-17  
**Sistema:** CalibraCore Lab v1.0
