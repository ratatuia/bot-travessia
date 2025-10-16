# 📋 Logs e Persistência de Dados - Bot Travessia

## 🚨 PROBLEMAS IDENTIFICADOS

### 1. **Logs no Render**
✅ **Logs estão aparecendo no Render!**

O código tem MUITOS `print()` statements que aparecem nos logs do Render:
```python
print("====== NOVA REQUISIÇÃO WEBHOOK ======")
print(f"[CLIENTE] {sender} disse: {incoming_msg}")
print(f"[DEBUG] Estado atual: {estado_atual}")
```

**Como ver os logs no Render:**
1. Acesse: https://dashboard.render.com
2. Clique no serviço `bot-travessia`
3. Vá na aba **"Logs"**
4. Você verá todos os `print()` em tempo real

**Logs disponíveis:**
- ✅ Todas as requisições webhook
- ✅ Mensagens dos clientes
- ✅ Estados da conversa
- ✅ Respostas do bot
- ✅ Erros e tracebacks

### 2. **Persistência de Dados - PROBLEMA CRÍTICO! ⚠️**

❌ **O banco de dados SQLite NÃO persiste no Render!**

**Motivo:**
O Render usa **filesystem efêmero** (temporário). Toda vez que o serviço reinicia, **TODOS OS ARQUIVOS LOCAIS SÃO PERDIDOS**, incluindo:
- `travessia_bot.db` (banco de dados)
- `logs/bot.log` (logs em arquivo)
- `logs/metrics.json` (métricas)

**Evidência:**
```json
{
  "total_clientes": 5,
  "total_mensagens": 124,
  "uptime_horas": 0.07  // Apenas 4 minutos de uptime
}
```

Os 5 clientes e 124 mensagens são de **ANTES** do último deploy. Quando o bot reiniciar novamente, esses dados **SERÃO PERDIDOS**.

---

## 🔧 SOLUÇÕES PARA PERSISTÊNCIA

### Opção 1: **PostgreSQL** (RECOMENDADO) ✅

**Vantagens:**
- ✅ Persistência garantida
- ✅ Backups automáticos
- ✅ Escalável
- ✅ Gratuito no Render (512 MB)

**Implementação:**

#### 1. Criar banco PostgreSQL no Render
1. No dashboard Render, clique em **"New +"** → **"PostgreSQL"**
2. Nome: `bot-travessia-db`
3. Plano: **Free** (512 MB)
4. Clique em **"Create Database"**
5. Copie a **Internal Database URL**

#### 2. Adicionar variável de ambiente
No serviço do bot:
- Settings → Environment
- Adicione: `DATABASE_URL` = (cola a Internal Database URL)

#### 3. Modificar código para usar PostgreSQL
```bash
# Instalar biblioteca
pip install psycopg2-binary
```

**Alterar `database.py`:**
```python
import os
import sqlite3
import psycopg2
from urllib.parse import urlparse

DB_TYPE = os.getenv("DATABASE_URL", "").startswith("postgres")

if DB_TYPE:
    # PostgreSQL
    def get_connection():
        return psycopg2.connect(os.getenv("DATABASE_URL"))
else:
    # SQLite (desenvolvimento)
    def get_connection():
        return sqlite3.connect("travessia_bot.db")

# Usar get_connection() em todas as queries
```

**Custo:** GRÁTIS (512 MB de storage)

---

### Opção 2: **Render Persistent Disks** (Pago - $1/mês) 💰

**Vantagens:**
- ✅ Mantém SQLite (sem mudanças no código)
- ✅ Simples de implementar

**Desvantagens:**
- ❌ Custa $1/mês por 1 GB
- ❌ Não tem backups automáticos

**Implementação:**
1. Dashboard Render → serviço bot → **"Disks"**
2. **"Add Disk"**
   - Name: `bot-travessia-data`
   - Size: 1 GB
   - Mount Path: `/data`
3. Alterar código:
```python
DB_PATH = "/data/travessia_bot.db"
LOG_DIR = "/data/logs"
```

---

### Opção 3: **Supabase PostgreSQL** (GRÁTIS) ✅

**Vantagens:**
- ✅ 500 MB grátis
- ✅ Backups automáticos
- ✅ Dashboard web para ver dados
- ✅ API REST integrada

**Implementação:**
1. Crie conta: https://supabase.com
2. Crie projeto: `bot-travessia`
3. Copie a **Connection String**
4. Adicione variável `DATABASE_URL` no Render
5. Use código do **Opção 1**

---

### Opção 4: **SQLite + Backup Automático em GitHub** (GRÁTIS) ✅

**Vantagens:**
- ✅ Gratuito
- ✅ Versionamento dos dados
- ✅ Mantém SQLite

**Desvantagens:**
- ❌ Complexo de implementar
- ❌ Limitado a arquivos pequenos (<100 MB)

**Implementação:**
Criar script que faz commit do banco a cada X horas:
```python
# backup_db.py
import subprocess
import datetime

def backup_database():
    subprocess.run(["git", "add", "travessia_bot.db"])
    subprocess.run(["git", "commit", "-m", f"backup: {datetime.now()}"])
    subprocess.run(["git", "push"])
```

---

## 📊 COMPARAÇÃO DE SOLUÇÕES

| Solução | Custo | Persistência | Backups | Complexidade | Recomendado |
|---------|-------|--------------|---------|--------------|-------------|
| **PostgreSQL (Render)** | GRÁTIS | ✅ | ✅ | Média | ⭐⭐⭐⭐⭐ |
| **Supabase** | GRÁTIS | ✅ | ✅ | Baixa | ⭐⭐⭐⭐ |
| **Persistent Disk** | $1/mês | ✅ | ❌ | Baixa | ⭐⭐⭐ |
| **GitHub Backup** | GRÁTIS | ⚠️ | ✅ | Alta | ⭐⭐ |

---

## 🎯 RECOMENDAÇÃO FINAL

**Use PostgreSQL do Render (Opção 1)** porque:
1. ✅ **GRÁTIS** (512 MB de storage)
2. ✅ **Persistência garantida** (dados nunca se perdem)
3. ✅ **Backups automáticos**
4. ✅ **Escalável** (suporta milhões de registros)
5. ✅ **Integrado ao Render** (zero configuração extra)

---

## 🚀 IMPLEMENTAÇÃO RÁPIDA (PostgreSQL)

### Passo 1: Criar banco PostgreSQL
```bash
# No dashboard Render:
New + → PostgreSQL
Nome: bot-travessia-db
Plano: Free
Region: Ohio (mesmo do bot)
```

### Passo 2: Copiar URL do banco
```
Internal Database URL (exemplo):
postgresql://bot_travessia_db_user:senha@dpg-xxx.ohio-postgres.render.com/bot_travessia_db
```

### Passo 3: Adicionar ao bot
```bash
# No serviço do bot:
Settings → Environment → Add Environment Variable
DATABASE_URL = (cola a URL copiada)
```

### Passo 4: Instalar biblioteca
Adicionar ao `requirements.txt`:
```
psycopg2-binary==2.9.9
```

### Passo 5: Modificar database.py
Vou criar o código adaptado para você!

---

## 📝 LOGS NO RENDER

### Como visualizar logs:
1. **Dashboard Render** → bot-travessia → **Logs**
2. Veja em tempo real todos os eventos

### Melhorar logs (opcional):
O código já tem sistema de logs avançado (`observability.py`), mas usa principalmente `print()`. Podemos:

**Opção A:** Manter `print()` (simples, funciona)
**Opção B:** Usar apenas o sistema de logs estruturado

**Para Opção B**, substituir todos os `print()` por:
```python
from observability import logger

# Em vez de:
print(f"[CLIENTE] {sender} disse: {incoming_msg}")

# Usar:
logger.info("Mensagem recebida", sender=sender, message=incoming_msg)
```

**Vantagem:** Logs estruturados em JSON (melhor para análise)
**Desvantagem:** Mais verboso

---

## 🔍 VERIFICAR DADOS ATUAIS

### Quantos clientes você tem DE VERDADE?
```bash
# Teste localmente:
sqlite3 travessia_bot.db "SELECT COUNT(*) FROM clientes"
```

Os 5 clientes que aparecem no health check são **dados antigos** que serão perdidos no próximo deploy.

---

## ⚠️ AÇÃO NECESSÁRIA

**URGENTE:** Migre para PostgreSQL AGORA para não perder dados!

**Passo a passo:**
1. Crie banco PostgreSQL no Render (5 minutos)
2. Eu crio o código de migração adaptado
3. Deploy com novo código
4. Dados persistem para sempre ✅

Quer que eu crie o código de migração para PostgreSQL agora?
