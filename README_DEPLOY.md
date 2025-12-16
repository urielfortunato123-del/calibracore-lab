# 🚀 Guia de Implantação (Deploy) - CalibraCore Lab

Este guia passo a passo ensinará como colocar o **CalibraCore Lab** na internet para que você (ou o diretor) possa acessar de qualquer lugar.

O projeto já está configurado para ser implantado facilmente.

---

## 📋 Pré-requisitos
1. **GitHub:** Você precisa ter o código do projeto "subido" para o GitHub (vou assumir que você já sabe usar ou já fez isso).
2. **Conta no Serviço de Hospedagem:** Vamos abordar duas opções:
   - **Render.com** (Mais fácil, tem opção Grátis).
   - **Google Cloud Run** (Robusto, infraestrutura Google, pago por uso - muito barato).

---

## 🌌 Opção 1: Render.com (Recomendado - Mais Fácil)
Esta opção é ideal para testes rápidos e uso sem burocracia.

1. Acesse [render.com](https://render.com) e crie uma conta (pode usar o login do GitHub).
2. Clique no botão **New +** e selecione **Blueprint**.
3. Conecte sua conta do GitHub e selecione o repositório do **CalibraCore Lab**.
4. O Render vai ler automaticamente o arquivo `render.yaml` que eu já deixei pronto no projeto.
5. Clique em **Apply**.
6. **Pronto!** Ele vai começar a construir e em alguns minutos te dará um link (ex: `calibracore-lab.onrender.com`).

---

## ☁️ Opção 2: Google Cloud Run (Infraestrutura Google)
Esta opção é profissional, segura e escala infinitamente. É muito barata se o uso for baixo.
Você precisará ter o **gcloud CLI** instalado ou fazer pelo console web. Vamos pelo **Console Web** que é mais visual.

### Passo 1: Preparar o Projeto
Certifique-se de que o arquivo `Dockerfile` está na raiz do projeto (eu já criei para você).

### Passo 2: Google Cloud Console
1. Acesse [console.cloud.google.com](https://console.cloud.google.com).
2. Crie um **Novo Projeto** (ex: `calibracore-lab`).
3. No menu lateral, procure por **Cloud Run**. (Se pedir para ativar APIs, aceite).
4. Clique em **CRIAR SERVIÇO**.

### Passo 3: Configurar o Serviço (Deploy direto do código)
O Google Cloud agora permite deploy direto do código fonte (sem precisar criar container manualmente antes), mas requer um pouco de configuração. A forma mais fácil hoje em dia para quem está começando é usar o "Cloud Run with Source repo".

1. **Origem:** Selecione **Implantar continuamente de um repositório** (Continuously deploy new revisions from a source repository).
2. Clique em **CONFIGURAR O CLOUD BUILD**.
3. Selecione seu repositório do **GitHub**.
4. **Configuração de Build:**
   - Selecione **Dockerfile**.
   - Localização do Dockerfile: `/Dockerfile` (já deve estar automático).
5. Clique em **Salvar**.

### Passo 4: Configurações Finais
1. **Nome do Serviço:** `calibracore-lab` (ou o que preferir).
2. **Região:** Escolha `southamerica-east1` (São Paulo) para menor latência, ou `us-central1` (EUA) que costuma ser mais barato.
3. **Autenticação:**
   - Selecione **Permitir invocações não autenticadas** (Allow unauthenticated invocations). Isso é importante para que o site seja público (o login do app protege os dados, não o servidor).
4. **Contêiner, Networking, Segurança:**
   - Expanda essa aba.
   - Em **Porta do contêiner**, verifique se está **8080**.
5. Clique em **CRIAR**.

O Google vai construir o projeto (isso leva uns 2-3 minutos).
Quando terminar, ele te dará uma URL segura `https://calibracore-lab-xxxxx.a.run.app`.

---

## 🛠️ Dicas Importantes Pós-Deploy

### 1. Banco de Dados
Por padrão, este projeto está usando **SQLite**.
- **No Render (Plano Grátis):** O banco de dados será "resetado" toda vez que o servidor reiniciar (o que acontece frequentemente no plano free). Para produção séria no Render, você precisaria adicionar um "Disk" (pago) ou usar um banco Postgres externo.
- **No Google Cloud Run:** O mesmo acontece. O container é "efêmero". Se quiser persistência real dos dados (que eles não sumam), você deve configurar um **Cloud SQL (Postgres)** da Google ou montar um **Volume** (agora suportado no Cloud Run).
   - *Solução Rapida:* Para a apresentação do diretor, o SQLite funciona perfeitamente. Só avise que se ele reiniciar o servidor, os dados voltam ao zero.

### 2. Uploads
Igual ao banco de dados: os arquivos PDF salvos ficam dentro do container. Se o container reiniciar, os arquivos somem.
- *Solução Profissional (Futuro):* Configurar para salvar os PDFs no **Google Cloud Storage** ou **AWS S3**.
- *Para Apresentação:* Funciona perfeito do jeito que está.

### 3. Variáveis de Ambiente
Se precisar mudar senhas ou emails sem mexer no código, vá nas configurações do painel (Render ou Google Cloud) e adicione as variáveis que estão no arquivo `.env.example`.

---

## 🚀 Resumo para Apresentação
Se você quer algo **rápido e gratuito** só para mostrar: Vá de **Render**.
Se você quer mostrar que está na **infraestrutura Google**: Vá de **Cloud Run**.

Boa sorte! 🏆
