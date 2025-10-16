# 🚢 Bot Travessia dos Sonhos v2

Bot conversacional inteligente para agência de cruzeiros, integrado com WhatsApp (via Twilio), Telegram e OpenAI GPT-4.

## 📋 Visão Geral

O Bot Travessia guia clientes através de uma jornada personalizada para:
- Coletar preferências de viagem (destinos, períodos, durações)
- Identificar interesses (gastronomia, entretenimento, relaxamento)
- Qualificar leads e agendar atendimento com especialistas
- Notificar equipe de vendas via Telegram em tempo real

## 🏗️ Arquitetura

```
Cliente WhatsApp → Twilio Webhook → Flask App → SQLite Database
                                              ↓
                                   OpenAI GPT-4 (Q&A)
                                              ↓
                                   Telegram Bot (Notificações)
```

### Stack Tecnológico

- **Backend**: Flask (Python 3.12+)
- **Database**: SQLite (dev) / PostgreSQL (produção recomendada)
- **AI**: OpenAI GPT-4o
- **Messaging**: Twilio (WhatsApp), Telegram Bot API
- **Dashboard**: Streamlit
- **Hosting**: Render
- **Security**: Flask-Limiter, Bleach, Custom validators

## 🔐 Segurança

✅ **Implementações recentes**:
- Validação de webhook Twilio (assinatura HMAC)
- Autenticação via API Key em endpoints sensíveis
- Rate limiting em todas rotas
- Sanitização de inputs (XSS, injection)
- Headers de segurança HTTP
- Logging com mascaramento de dados sensíveis

📖 Veja [SECURITY_ROTATION_GUIDE.md](SECURITY_ROTATION_GUIDE.md) e [DEPLOY_SECURITY_CHECKLIST.md](DEPLOY_SECURITY_CHECKLIST.md)

## 🚀 Setup Local

### 1. Clone o Repositório
```bash
git clone https://github.com/ratatuia/bot-travessia.git
cd bot-travessia-v2
```

### 2. Crie Ambiente Virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale Dependências
```bash
pip install -r requirements.txt
```

### 4. Configure Variáveis de Ambiente
```bash
# Copie o template
cp .env.example .env

# Edite .env com suas credenciais
# Nunca commite o .env no Git!
```

**Variáveis obrigatórias**:
```env
OPENAI_API_KEY=sk-proj-...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
ADMIN_API_KEY=...  # Gere com: python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Inicialize o Banco de Dados
```bash
python -c "from database import init_db; init_db()"
```

### 6. Execute o Bot
```bash
# Desenvolvimento
python app.py

# Produção (Gunicorn)
gunicorn -c gunicorn_config.py app:app
```

### 7. Inicie o Dashboard (Opcional)
```bash
streamlit run dashboard.py
```

## 📡 Endpoints

### Públicos
- `GET /` - Status do bot
- `GET /health` - Health check detalhado (JSON)
- `POST /zap` - Webhook Twilio (valida assinatura)
- `GET /daily-stats` - Estatísticas diárias

### Protegidos (requerem API Key)
- `POST /reset-db` - Reinicia banco (com backup)
- `GET /debug-state?phone=...` - Debug de estado do cliente
- `GET /test-telegram` - Testa integração Telegram

**Uso de endpoints protegidos**:
```bash
curl -H "Authorization: Bearer SUA_ADMIN_API_KEY" \
  https://seu-app.onrender.com/debug-state?phone=whatsapp:+5511999999999
```

## 🎯 Fluxo de Conversação

```
1. Cliente: "Oi"
   ↓
2. Bot: Solicita nome
   ↓
3. Cliente: "João Silva"
   ↓
4. Bot: Solicita email
   ↓
5. Cliente: "joao@email.com"
   ↓
6. Bot: Menu principal
   - Conhecer a tripulação
   - Iniciar planejamento de viagem
   - Solicitar atendimento especializado
   ↓
7. [Fluxo de planejamento]
   - Período de viagem
   - Duração desejada
   - Destino/região
   - Forma de contato preferida
   - Horário de contato
   ↓
8. Bot: Confirmação + Notificação Telegram
   ↓
9. Especialista: Recebe perfil completo no Telegram
```

## 🗂️ Estrutura de Arquivos

```
bot-travessia-v2/
├── app.py                    # Aplicação Flask principal
├── config.py                 # Configurações e constantes
├── database.py               # Operações SQLite
├── security.py               # Módulo de segurança
├── telegram_service.py       # Integração Telegram
├── openai_service.py         # Integração OpenAI
├── log_service.py            # Logging e alertas
├── dashboard.py              # Dashboard Streamlit
├── gunicorn_config.py        # Config do servidor
├── requirements.txt          # Dependências Python
├── .env.example              # Template de variáveis
├── .gitignore                # Arquivos ignorados
├── saldo_apis/               # Monitoramento de créditos
│   ├── openai_monitor.py
│   ├── twilio_monitor.py
│   └── loop_diario.py
├── .github/
│   └── workflows/
│       └── executar_saldo.yml  # GitHub Actions
├── SECURITY_ROTATION_GUIDE.md  # Guia de rotação de chaves
├── DEPLOY_SECURITY_CHECKLIST.md  # Checklist de deploy
└── README.md                   # Este arquivo
```

## 📊 Dashboard

Acesse o dashboard Streamlit para:
- Visualizar estatísticas de clientes
- Analisar preferências de viagem
- Acompanhar leads pendentes
- Exportar dados para CSV

```bash
streamlit run dashboard.py
```

Navegação:
1. **Visão Geral**: KPIs e gráficos de atividade
2. **Preferências**: Análise de destinos, períodos, durações
3. **Atendimentos Pendentes**: Leads aguardando contato
4. **Detalhes de Clientes**: Busca e exportação

## 🔧 Configuração do Twilio

1. Crie conta em: https://www.twilio.com/
2. Configure WhatsApp Sandbox
3. Configure webhook:
   - URL: `https://seu-app.onrender.com/zap`
   - Method: `POST`
   - **Importante**: A assinatura será validada automaticamente

## 🤖 Configuração do Telegram

1. Crie bot com @BotFather
2. Obtenha token: `/newbot`
3. Obtenha Chat ID:
   ```bash
   # Envie mensagem para seu bot, depois:
   curl https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
4. Configure no `.env`

## 📈 Monitoramento

### GitHub Actions (Diário)
- Monitora saldo OpenAI
- Monitora saldo Twilio
- Executa às 8h BRT (11h UTC)

### Logs
- Arquivo: `bot.log`
- Níveis: INFO, WARNING, ERROR, DEBUG
- Alertas críticos enviados via Telegram

### Health Check
```bash
curl https://seu-app.onrender.com/health
```

**Retorno**:
```json
{
  "status": "online",
  "uptime": "5:32:15",
  "database": "conectado",
  "estatisticas": {
    "total_clientes": 42,
    "total_mensagens": 387,
    "clientes_atendimento": 8,
    "mensagens_24h": 15
  },
  "sistema": {
    "memoria_uso_mb": 125.3,
    "cpu_percent": 2.5,
    "threads": 4
  }
}
```

## 🧪 Testes

```bash
# Testar webhook localmente (sem validação Twilio)
curl -X POST http://localhost:5000/zap \
  -d "Body=Oi" \
  -d "From=whatsapp:+5511999999999"

# Testar health check
curl http://localhost:5000/health

# Testar Telegram
curl http://localhost:5000/test-telegram
```

## 🚀 Deploy no Render

1. Crie conta em: https://render.com/
2. Conecte repositório GitHub
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -c gunicorn_config.py app:app`
4. Adicione Environment Variables (veja `.env.example`)
5. Deploy automático em cada push para `main`

## 🔄 CI/CD

### GitHub Actions
- **Workflow**: `.github/workflows/executar_saldo.yml`
- **Trigger**: Diário às 11h UTC ou manual
- **Ação**: Monitora saldos de API

### Deploy
- **Automático**: Push para `main` → Deploy no Render
- **Manual**: Dashboard Render → Deploy manually

## 📝 Boas Práticas

### Desenvolvimento
1. Nunca commite `.env` ou credenciais
2. Use `.env.example` para documentar variáveis
3. Teste localmente antes de push
4. Valide inputs do usuário
5. Use logging estruturado

### Segurança
1. Rotacione chaves regularmente
2. Monitore logs de erro
3. Configure rate limiting adequado
4. Valide assinaturas de webhook
5. Mantenha dependências atualizadas

### Produção
1. Use PostgreSQL ao invés de SQLite
2. Configure backup automático do banco
3. Implemente monitoring (Sentry)
4. Configure alertas de erro
5. Documente mudanças críticas

## 🐛 Troubleshooting

### Bot não responde
1. Verifique `/health` endpoint
2. Veja logs no Render Dashboard
3. Confirme webhook Twilio configurado
4. Teste rate limiting não foi atingido

### Erro "Invalid Twilio signature"
1. Confirme `TWILIO_AUTH_TOKEN` correto
2. Verifique URL do webhook
3. Teste com curl sem decorator (dev)

### Erro OpenAI
1. Verifique saldo em: https://platform.openai.com/usage
2. Confirme `OPENAI_API_KEY` válida
3. Veja logs para detalhes do erro

### Telegram não envia
1. Teste endpoint `/test-telegram`
2. Confirme `TELEGRAM_BOT_TOKEN` válido
3. Verifique `TELEGRAM_CHAT_ID` correto

## 📚 Documentação Adicional

- [Guia de Rotação de Chaves](SECURITY_ROTATION_GUIDE.md)
- [Checklist de Deploy](DEPLOY_SECURITY_CHECKLIST.md)
- [Twilio Docs](https://www.twilio.com/docs/whatsapp)
- [OpenAI API](https://platform.openai.com/docs)
- [Telegram Bot API](https://core.telegram.org/bots/api)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'feat: adicionar nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra Pull Request

## 📄 Licença

Uso privado - Travessia dos Sonhos

## 👥 Autores

- **Desenvolvimento**: Claude (Anthropic)
- **Proprietário**: Travessia dos Sonhos

## 🔗 Links

- **Repositório**: https://github.com/ratatuia/bot-travessia
- **Deploy**: https://seu-app.onrender.com
- **Dashboard**: Local - `streamlit run dashboard.py`

---

**Versão**: 2.0.0
**Última atualização**: Outubro 2025
**Status**: 🟢 Produção (com melhorias de segurança implementadas)
