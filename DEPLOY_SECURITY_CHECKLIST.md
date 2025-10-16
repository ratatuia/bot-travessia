# 🔒 Checklist de Segurança e Deploy

## ✅ CONCLUÍDO - Melhorias Implementadas

### 1. Segurança Crítica ✅
- [x] **Git History Limpo**: `.env` removido do histórico com `git-filter-repo`
- [x] **Endpoints Protegidos**: `/reset-db` e `/debug-state` agora exigem API Key
- [x] **Webhook Validado**: Assinatura Twilio (`X-Twilio-Signature`) validada
- [x] **Rate Limiting**: Implementado em todos endpoints críticos
- [x] **Input Sanitization**: Nomes, emails e mensagens sanitizados
- [x] **Security Headers**: X-Frame-Options, CSP, HSTS, etc.
- [x] **Masked Logging**: Dados sensíveis mascarados em logs

### 2. Arquivos Criados ✅
- [x] `security.py` - Módulo completo de segurança
- [x] `.env.example` - Template para desenvolvedores
- [x] `SECURITY_ROTATION_GUIDE.md` - Guia de rotação de chaves
- [x] `DEPLOY_SECURITY_CHECKLIST.md` - Este arquivo

### 3. Dependências Atualizadas ✅
- [x] `flask-limiter` - Rate limiting
- [x] `bleach` - Sanitização HTML/JS

---

## 🚀 PRÓXIMOS PASSOS - VOCÊ PRECISA FAZER

### PASSO 1: Rotacionar Todas as Chaves 🔴 CRÍTICO

Suas chaves antigas foram **expostas no Git** e precisam ser invalidadas:

#### OpenAI
1. Acesse: https://platform.openai.com/api-keys
2. Revogue: `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`
3. Crie nova chave
4. Salve no Render (Environment Variables)

#### Twilio
1. Acesse: https://console.twilio.com/
2. Vá em **Account → API Keys & Tokens**
3. Promova token secundário a primário (invalida o antigo)
4. Copie novo Auth Token
5. Salve no Render

#### Telegram
1. Abra o Telegram, busque **@BotFather**
2. Envie: `/mybots` → Selecione seu bot → **API Token** → **Revoke**
3. Clique em **Generate new token**
4. Copie novo token
5. Salve no Render

#### Gerar Admin API Key (NOVO)
```bash
python -c "import secrets; print('ADMIN_API_KEY=' + secrets.token_urlsafe(32))"
```
Exemplo de saída:
```
ADMIN_API_KEY=jFjG7aYZX3S3k_KSlYfILbekm_2x_2xUms0mUjMUVKo
```

**Adicione no Render:**
- Vá em: Dashboard → Seu serviço → Environment
- Clique em **"Add Environment Variable"**
- Key: `ADMIN_API_KEY`
- Value: (cole a chave gerada)
- Clique em **"Save Changes"**

---

### PASSO 2: Force Push do Git (Remover Histórico) ⚠️

O histórico Git foi limpo localmente. Agora precisa atualizar o GitHub:

```bash
# ATENÇÃO: Isso reescreve o histórico do repositório!
git push origin --force --all
git push origin --force --tags
```

**Se houver outros colaboradores**, avise-os para fazer:
```bash
git fetch origin
git reset --hard origin/main
```

---

### PASSO 3: Atualizar Environment Variables no Render

No **Render Dashboard**:

1. Vá em: https://dashboard.render.com/
2. Selecione seu serviço (bot-travessia)
3. Vá em **Environment** no menu lateral
4. Adicione/Atualize as seguintes variáveis:

```bash
# OpenAI (NOVA CHAVE)
OPENAI_API_KEY=sk-proj-NOVA_CHAVE_AQUI

# Twilio (NOVO AUTH TOKEN)
TWILIO_ACCOUNT_SID=AC2dc6193c8465b9dd185666428e8f6d29  # Pode manter o mesmo
TWILIO_AUTH_TOKEN=NOVO_TOKEN_AQUI

# Telegram (NOVO TOKEN)
TELEGRAM_BOT_TOKEN=NOVO_TOKEN_AQUI
TELEGRAM_CHAT_ID=-1002535493280  # Pode manter o mesmo

# Admin API Key (NOVO - OBRIGATÓRIO)
ADMIN_API_KEY=jFjG7aYZX3S3k_KSlYfILbekm_2x_2xUms0mUjMUVKo

# Flask (opcional)
FLASK_ENV=production
PORT=8080
```

5. Clique em **"Save Changes"**
6. O serviço será reiniciado automaticamente

---

### PASSO 4: Deploy das Mudanças

```bash
# Adiciona todos os arquivos novos
git add .

# Commit
git commit -m "feat: implementar proteções de segurança críticas

- Adicionar autenticação em endpoints sensíveis
- Implementar validação de webhook Twilio
- Adicionar rate limiting em todas rotas
- Sanitizar e validar inputs do usuário
- Adicionar headers de segurança HTTP
- Criar módulo security.py
- Adicionar documentação de segurança"

# Push (após force push anterior)
git push origin main
```

O Render vai detectar o push e fazer deploy automaticamente.

---

### PASSO 5: Testar Endpoints Protegidos

#### Testar Health Check (público):
```bash
curl https://SEU_APP.onrender.com/health
```
**Esperado**: JSON com status do sistema

#### Testar Reset-DB (protegido - DEVE FALHAR sem auth):
```bash
curl -X POST https://SEU_APP.onrender.com/reset-db
```
**Esperado**: `{"error": "Unauthorized", "message": "Missing or invalid Authorization header"}`

#### Testar Reset-DB (protegido - COM auth):
```bash
curl -X POST \
  -H "Authorization: Bearer jFjG7aYZX3S3k_KSlYfILbekm_2x_2xUms0mUjMUVKo" \
  https://SEU_APP.onrender.com/reset-db
```
**Esperado**: `{"success": true, "message": "Banco de dados reiniciado com sucesso"}`

#### Testar Debug State (protegido):
```bash
curl -H "Authorization: Bearer jFjG7aYZX3S3k_KSlYfILbekm_2x_2xUms0mUjMUVKo" \
  "https://SEU_APP.onrender.com/debug-state?phone=whatsapp:+5511999999999"
```

---

### PASSO 6: Verificar Logs no Render

1. Vá em: Dashboard → Logs
2. Procure por:
   - ✅ `Iniciando Bot da Travessia dos Sonhos...`
   - ✅ `Database conectado`
   - ❌ Erros de autenticação (401/403)
   - ❌ Rate limit excedido (429)

3. Se houver erros relacionados a API keys:
   - Verifique se todas env vars foram salvas corretamente
   - Confirme que não há espaços em branco nas chaves
   - Reinicie o serviço manualmente se necessário

---

## 🔐 Usando Endpoints Protegidos

### Reset Database (Emergência)
```bash
curl -X POST \
  -H "Authorization: Bearer SUA_ADMIN_API_KEY" \
  https://seu-app.onrender.com/reset-db
```

### Debug Client State
```bash
curl -H "Authorization: Bearer SUA_ADMIN_API_KEY" \
  "https://seu-app.onrender.com/debug-state?phone=whatsapp:+5511999999999"
```

### Daily Stats com Notificação
```bash
curl "https://seu-app.onrender.com/daily-stats?notify=true"
```

---

## 🛡️ Proteções Implementadas

### Rate Limiting (por IP)
- **/** (root): 200/dia, 50/hora
- **/zap** (webhook): 100/hora
- **/reset-db**: 5/dia
- **/debug-state**: 30/hora
- **/health**: 200/dia, 50/hora

### Validações de Input
- **Nome**: Apenas letras, espaços, hífens, apóstrofes (max 100 chars)
- **Email**: RFC 5321 compliant (max 254 chars)
- **Telefone**: Formato WhatsApp: `whatsapp:+[10-15 dígitos]`
- **Mensagens**: Sanitizadas (remove HTML/JS/control chars, max 500 chars)

### Headers de Segurança HTTP
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

### Webhook Twilio
- Valida `X-Twilio-Signature` usando HMAC-SHA256
- Previne spoofing de mensagens
- Rejeita requisições não autenticadas

---

## 📋 Checklist Final de Deploy

Antes de considerar o deploy concluído:

- [ ] OpenAI: Chave antiga revogada, nova chave funcionando
- [ ] Twilio: Auth Token rotacionado, webhook respondendo
- [ ] Telegram: Token revogado, novo token funcionando
- [ ] Admin API Key: Gerada e salva no Render
- [ ] Git: Force push realizado, histórico limpo
- [ ] Render: Todas env vars atualizadas
- [ ] Deploy: Código atualizado no Render
- [ ] Logs: Sem erros de autenticação
- [ ] Health Check: Retorna status 200
- [ ] Endpoints protegidos: Exigem auth (testado)
- [ ] WhatsApp: Bot respondendo normalmente
- [ ] Telegram: Notificações funcionando
- [ ] Rate Limiting: Funcionando (teste com muitas requests)

---

## 🆘 Troubleshooting

### Erro: "Invalid API key"
- Confirme que `ADMIN_API_KEY` está no Render
- Verifique se não há espaços extras na chave
- Teste com: `echo "Bearer $ADMIN_API_KEY"` antes do curl

### Erro: "Invalid Twilio signature"
- Confirme que `TWILIO_AUTH_TOKEN` está atualizado no Render
- Verifique se a URL do webhook no Twilio está correta
- Temporariamente comente o decorator `@require_twilio_signature` para testar

### Erro: "Too Many Requests" (429)
- Rate limit atingido - normal em testes
- Aguarde 1 hora ou ajuste limites em `app.py`

### Erro: "OpenAI API key invalid"
- Confirme que a chave nova foi salva corretamente
- Teste a chave diretamente: https://platform.openai.com/playground

### Bot não responde no WhatsApp
1. Verifique logs no Render
2. Confirme que o webhook Twilio aponta para `/zap`
3. Teste o endpoint `/health` para confirmar que está online
4. Verifique se o rate limit não foi atingido

---

## 📞 Suporte

Se encontrar problemas:

1. **Logs do Render**: Sempre verifique primeiro
2. **Health Check**: Teste `/health` para status do sistema
3. **Twilio Console**: Veja logs de webhook
4. **OpenAI Dashboard**: Verifique uso da API

---

## 🎯 Próximas Melhorias (Futuro)

Após deploy e rotação de chaves:

1. **PostgreSQL**: Migrar de SQLite para produção
2. **Redis**: Cache e rate limiting distribuído
3. **Sentry**: Monitoring de erros em tempo real
4. **FastAPI**: Migrar de Flask para async
5. **Testes**: Adicionar suite de testes automatizados
6. **CI/CD**: Pipeline completo com testes
7. **Staging**: Ambiente de testes separado

---

**Status**: Segurança implementada, aguardando rotação de chaves e deploy.

**Tempo estimado**: 30-45 minutos para completar todos os passos.

**Prioridade**: 🔴 CRÍTICA - Execute hoje.
