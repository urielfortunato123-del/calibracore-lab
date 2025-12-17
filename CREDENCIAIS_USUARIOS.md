# 🔐 Credenciais de Usuários - CalibraCore Lab

> [!WARNING]
> **ARQUIVO CONFIDENCIAL** - Este arquivo contém credenciais de acesso. 
> NÃO deve ser commitado no GitHub público. Manter apenas em pastas internas do servidor.

## Lista de Usuários e Senhas

### 1. Letícia Silveira (Motiva)
- **E-mail:** leticia.silveira@motiva.com.br
- **Senha:** MotivaLeti9
- **Papel:** Administrador
- **Laboratório:** Motiva

---

### 2. André Pereira (Motiva)
- **E-mail:** andre.pereira@motiva.com.br
- **Senha:** Andre@Motiva9
- **Papel:** Administrador
- **Laboratório:** Motiva

---

### 3. Alan Silva (Núcleo Engenharia)
- **E-mail:** alan.silva@nucleoengenharia.com.br
- **Senha:** NucleoAlan88
- **Papel:** Administrador
- **Laboratório:** Núcleo Engenharia

---

### 4. Fabiano Silva (Núcleo Engenharia)
- **E-mail:** fabiano.silva@nucleoengenharia.com.br
- **Senha:** Fabiano@Eng9
- **Papel:** Administrador
- **Laboratório:** Núcleo Engenharia

---

## Instruções de Uso

### Para Inicializar os Usuários no Servidor:

```bash
cd backend
python init_users.py
```

### Notas de Segurança:
- ✅ Todos os usuários são criados como **Administradores**
- ✅ As senhas são armazenadas com hash Argon2 no banco de dados
- ✅ Os usuários são ativados automaticamente
- ⚠️ **Importante:** Adicione este arquivo ao `.gitignore` para evitar commit acidental

---

**Data de Criação:** 2025-12-17  
**Última Atualização:** 2025-12-17
