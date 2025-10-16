# 🚀 Migração para PostgreSQL - Guia Completo

## 📋 O QUE VAI ACONTECER

Vamos migrar o bot do SQLite (temporário) para PostgreSQL (permanente) em **3 passos simples**:

1. ✅ Criar banco PostgreSQL no Render (5 min)
2. ✅ Configurar variável de ambiente (2 min)
3. ✅ Deploy do novo código (3 min)

**Tempo total:** ~10 minutos
**Downtime:** 0 (bot continua funcionando)

---

## 🎯 PASSO 1: Criar Banco PostgreSQL no Render

### 1.1 Acessar Dashboard do Render
1. Acesse: https://dashboard.render.com
2. Faça login com sua conta

### 1.2 Criar Novo Banco de Dados
1. Clique no botão **"New +"** (canto superior direito)
2. Selecione **"PostgreSQL"**

### 1.3 Configurar o Banco
Preencha os campos:

```
Name: bot-travessia-db
Database: bot_travessia_db (gerado automaticamente)
User: bot_travessia_db_user (gerado automaticamente)
Region: Ohio (US East) - MESMO REGIÃO DO SEU BOT
PostgreSQL Version: 16 (mais recente)
```

**Plano:** Selecione **"Free"**
- 512 MB de storage
- 90 dias de retenção de backup
- Gratuito para sempre

### 1.4 Criar o Banco
1. Clique em **"Create Database"**
2. Aguarde 1-2 minutos (o Render provisiona o banco)

### 1.5 Copiar URL do Banco
Após a criação, você verá a tela de informações do banco.

**IMPORTANTE:** Copie a **"Internal Database URL"** (NÃO a External!)

Formato da URL:
```
postgresql://bot_travessia_db_user:SENHA_GERADA@dpg-xxxxx-ohio-postgres.render.com/bot_travessia_db
```

💡 **Dica:** Clique no ícone de copiar ao lado da URL

---

## 🎯 PASSO 2: Configurar Variável de Ambiente

### 2.1 Ir para o Serviço do Bot
1. No dashboard Render, clique em **"bot-travessia"** (seu serviço web)
2. Vá na aba **"Environment"**

### 2.2 Adicionar Variável DATABASE_URL
1. Clique em **"Add Environment Variable"**
2. Preencha:
   - **Key:** `DATABASE_URL`
   - **Value:** (cole a Internal Database URL que você copiou)
3. Clique em **"Save Changes"**

**Exemplo:**
```
Key: DATABASE_URL
Value: postgresql://bot_travessia_db_user:d8f7h3k2j...@dpg-ct12345-ohio-postgres.render.com/bot_travessia_db
```

### 2.3 NÃO Reinicie Ainda
O Render vai sugerir reiniciar o serviço. **NÃO clique em "Manual Deploy" ainda**.

Vamos fazer o deploy do código atualizado primeiro.

---

## 🎯 PASSO 3: Deploy do Novo Código

### 3.1 Substituir database.py
O código já está pronto! Agora vamos ativar a nova versão:

**No seu terminal local:**
```bash
# 1. Renomear o arquivo antigo (backup)
mv database.py database_sqlite_old.py

# 2. Ativar a nova versão
mv database_postgres.py database.py

# 3. Commit e push
git add -A
git commit -m "feat: migrar para PostgreSQL com suporte a SQLite"
git push origin main
```

### 3.2 Aguardar Deploy
O Render detecta automaticamente o push e inicia o deploy.

**Acompanhe em:**
Dashboard → bot-travessia → aba **"Logs"**

Você verá:
```
==> Building...
==> Installing dependencies...
==> Starting service...
🐘 Usando PostgreSQL
✅ Banco de dados inicializado com sucesso!
```

**Tempo:** ~2-3 minutos

### 3.3 Verificar Sucesso
Quando aparecer:
```
🐘 Usando PostgreSQL
✅ Banco de dados inicializado com sucesso!
Your service is live 🎉
```

✅ **PRONTO! Migração concluída!**

---

## ✅ VERIFICAÇÃO

### Testar se está usando PostgreSQL:
```bash
curl "https://bot-travessia.onrender.com/health"
```

Você verá:
```json
{
  "database": "conectado",
  "status": "online",
  ...
}
```

### Verificar logs no Render:
Procure por:
```
🐘 Usando PostgreSQL
✅ Banco de dados inicializado com sucesso!
```

Se aparecer **"📁 Usando SQLite"**, algo deu errado. Verifique:
1. Variável `DATABASE_URL` foi adicionada?
2. URL começa com `postgresql://`?
3. Deploy foi feito após adicionar a variável?

---

## 🔄 MIGRAR DADOS ANTIGOS (Opcional)

Se você tinha dados no SQLite local que quer preservar:

### Opção A: Migração Automática (se banco local existe)

**No terminal local:**
```bash
# 1. Copiar banco SQLite local
cp travessia_bot.db travessia_bot_backup.db

# 2. Executar script de migração
python -c "
import os
os.environ['DATABASE_URL'] = 'COLE_AQUI_A_URL_DO_POSTGRES'
from database import migrate_from_sqlite
migrate_from_sqlite('travessia_bot.db')
"
```

### Opção B: Começar do Zero
Se prefere começar com banco limpo (recomendado):

✅ **Nada a fazer!** O banco PostgreSQL já está pronto e vazio.

---

## 🎉 BENEFÍCIOS IMEDIATOS

Após a migração:

1. ✅ **Dados nunca mais se perdem** (mesmo após redeploy)
2. ✅ **Backups automáticos** (Render faz diariamente)
3. ✅ **Performance melhor** (PostgreSQL é otimizado)
4. ✅ **Consultas avançadas** (JSONB, full-text search)
5. ✅ **Escalabilidade** (suporta milhões de registros)

---

## 🔍 MONITORAMENTO DO BANCO

### Ver dados no banco:
1. Dashboard Render → bot-travessia-db
2. Clique em **"Connect"**
3. Use o comando fornecido para conectar via terminal

Ou use ferramentas visuais:
- **TablePlus** (recomendado): https://tableplus.com
- **pgAdmin**: https://www.pgadmin.org
- **DBeaver**: https://dbeaver.io

### Queries úteis:
```sql
-- Ver todos os clientes
SELECT * FROM clientes ORDER BY ultima_interacao DESC;

-- Ver mensagens recentes
SELECT * FROM mensagens ORDER BY timestamp DESC LIMIT 50;

-- Estatísticas
SELECT
  COUNT(DISTINCT telefone) as total_clientes,
  COUNT(*) as total_mensagens
FROM mensagens;
```

---

## 🆘 TROUBLESHOOTING

### Erro: "no module named psycopg2"
**Solução:** O `requirements.txt` já foi atualizado. Aguarde o deploy completar.

### Erro: "connection refused"
**Solução:** Verifique se a URL do banco está correta (deve ser Internal, não External).

### Erro: "SSL connection required"
**Solução:** O código já trata isso automaticamente (`sslmode='require'`).

### Bot não inicia após migração
**Solução:**
1. Verifique logs do Render
2. Se aparecer erro, reverta:
```bash
git revert HEAD
git push origin main
```

### Quero voltar para SQLite
**Solução:**
1. Dashboard Render → bot-travessia → Environment
2. Delete a variável `DATABASE_URL`
3. Save Changes
4. O bot volta a usar SQLite (mas dados serão perdidos!)

---

## 📊 COMPARAÇÃO: ANTES vs DEPOIS

| Aspecto | Antes (SQLite) | Depois (PostgreSQL) |
|---------|----------------|---------------------|
| **Persistência** | ❌ Perde tudo no redeploy | ✅ Nunca perde |
| **Backups** | ❌ Manual | ✅ Automático (diário) |
| **Performance** | ⚠️ OK para poucos dados | ✅ Otimizado |
| **Escalabilidade** | ❌ Limitado | ✅ Milhões de registros |
| **Consultas JSON** | ⚠️ Limitado | ✅ JSONB nativo |
| **Custo** | Grátis | Grátis |
| **Setup** | Zero | 10 minutos |

---

## 🎯 CHECKLIST FINAL

Antes de começar:
- [ ] Conta no Render criada e verificada
- [ ] Bot rodando normalmente
- [ ] Código local atualizado (git pull)

Durante a migração:
- [ ] Banco PostgreSQL criado no Render
- [ ] Internal Database URL copiada
- [ ] Variável DATABASE_URL adicionada ao bot
- [ ] Código commitado e pushed
- [ ] Deploy concluído com sucesso

Após a migração:
- [ ] Logs mostram "🐘 Usando PostgreSQL"
- [ ] Bot responde normalmente (teste mandando msg)
- [ ] Dados aparecem no banco PostgreSQL
- [ ] Health check retorna "database": "conectado"

---

## 🚀 PRÓXIMOS PASSOS

Após a migração estar completa:

1. **Configure cron jobs** ([CRON_JOBS_SETUP.md](CRON_JOBS_SETUP.md))
2. **Teste o dashboard** (https://bot-travessia.onrender.com/dashboard)
3. **Monitore os logs** para garantir que tudo funciona
4. **Divulgue o bot** e comece a receber clientes!

---

**Boa sorte! 🎉**

Se tiver qualquer problema, os logs do Render mostrarão exatamente o que aconteceu.
