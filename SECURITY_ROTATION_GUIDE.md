# 🚨 GUIA DE ROTAÇÃO DE CHAVES - EXECUTAR IMEDIATAMENTE

## ⚠️ SUAS CHAVES FORAM COMPROMETIDAS NO GIT

As seguintes chaves estão expostas no histórico do Git e precisam ser rotacionadas **AGORA**:

---

## 1️⃣ OpenAI API Key

**Chave Comprometida:** `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`

### Passos:
1. Acesse: https://platform.openai.com/api-keys
2. Localize a chave comprometida na lista
3. Clique em **"Revoke"** para invalidá-la
4. Clique em **"Create new secret key"**
5. Copie a nova chave
6. No Render:
   - Vá em: Dashboard → Seu serviço → Environment
   - Edite `OPENAI_API_KEY` com a nova chave
   - Clique em **"Save Changes"**
   - O serviço será reiniciado automaticamente

---

## 2️⃣ Twilio Auth Token

**Account SID Comprometido:** `AC2dc6193c8465b9dd185666428e8f6d29`
**Auth Token Comprometido:** `5742ef371a88a5955bee85562a261285`

### Passos:
1. Acesse: https://console.twilio.com/
2. Vá em **Account → API Keys & Tokens**
3. Na seção "Auth Tokens", clique em **"View secondary auth token"**
4. Clique em **"Promote to primary"** (isso invalida o token antigo)
5. Ou crie um novo Auth Token e revogue o antigo
6. Copie o novo Auth Token
7. No Render:
   - Edite `TWILIO_AUTH_TOKEN` com o novo token
   - Clique em **"Save Changes"**

**Nota:** O Account SID não precisa ser rotacionado (é público), mas o Auth Token sim.

---

## 3️⃣ Telegram Bot Token

**Token Comprometido:** `8147537930:AAGFP2IT2Rz9drJFcKkWLAn79enrWCfMenI`

### Passos:
1. Abra o Telegram e busque por **@BotFather**
2. Envie o comando: `/mybots`
3. Selecione seu bot (Travessia Bot)
4. Clique em **"API Token"**
5. Clique em **"Revoke current token"**
6. Clique em **"Generate new token"**
7. Copie o novo token
8. No Render:
   - Edite `TELEGRAM_BOT_TOKEN` com o novo token
   - Clique em **"Save Changes"**

---

## 4️⃣ Limpar Histórico do Git

### Opção A: Usar git-filter-repo (Recomendado)

```bash
# Instalar git-filter-repo
pip install git-filter-repo

# Fazer backup do repositório primeiro!
cd ..
cp -r bot-travessia-v2 bot-travessia-v2-backup

# Voltar ao repositório
cd bot-travessia-v2

# Remover .env do histórico
git filter-repo --path .env --invert-paths --force

# Force push para o GitHub
git push origin --force --all
git push origin --force --tags
```

### Opção B: Se não conseguir instalar git-filter-repo

```bash
# Método alternativo (mais agressivo)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Limpar referências
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push
git push origin --force --all
git push origin --force --tags
```

### ⚠️ Avisos Importantes:

1. **Force push irá reescrever o histórico** - avise colaboradores
2. **Faça backup** antes de executar
3. **Depois do force push**, todos colaboradores precisam fazer:
   ```bash
   git fetch origin
   git reset --hard origin/main
   ```

---

## 5️⃣ Verificar se o Repositório é Público

```bash
# Verificar URL do repositório
git remote -v
```

Se a URL for `https://github.com/SEU_USER/bot-travessia-v2.git`:

1. Acesse: https://github.com/SEU_USER/bot-travessia-v2/settings
2. Role até "Danger Zone"
3. Se o repositório estiver **público**, considere:
   - Torná-lo **privado** OU
   - Deletar e recriar (se não houver colaboradores)

---

## 6️⃣ Criar .env.example (Para Futuros Desenvolvedores)

Já criei este arquivo automaticamente para você. Ele contém:
- Placeholders para as variáveis de ambiente
- Instruções de configuração
- Sem valores reais

---

## ✅ Checklist de Segurança

Marque conforme for completando:

- [ ] OpenAI: Chave antiga revogada
- [ ] OpenAI: Nova chave criada e adicionada no Render
- [ ] Twilio: Auth Token rotacionado
- [ ] Twilio: Novo token adicionado no Render
- [ ] Telegram: Token antigo revogado
- [ ] Telegram: Novo token criado e adicionado no Render
- [ ] Git: .env removido do histórico (git filter-repo)
- [ ] Git: Force push realizado
- [ ] Render: Serviço reiniciado com novas chaves
- [ ] Teste: Bot funcionando com novas credenciais

---

## 🧪 Testar Após Rotação

```bash
# Testar se o bot responde
curl -X POST https://SEU_APP.onrender.com/health

# Verificar logs no Render
# Dashboard → Logs → Procurar por erros de autenticação
```

---

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs no Render
2. Confirme que as env vars foram salvas corretamente
3. Reinicie o serviço manualmente no Render

**Tempo estimado:** 15-20 minutos

**Status:** 🔴 CRÍTICO - Executar imediatamente
