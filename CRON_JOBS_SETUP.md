# 🕐 Configuração de Cron Jobs - Bot Travessia

Este guia mostra como configurar os alertas automáticos do bot usando serviços gratuitos de cron jobs.

---

## 🎯 Jobs Recomendados

### 1. **Alerta de Inatividade** (a cada 6 horas)
Verifica se o bot está recebendo mensagens. Se não houver mensagens nas últimas 12 horas, envia alerta no Telegram.

**URL:** `https://bot-travessia.onrender.com/check-inactivity?hours=12`
**Frequência:** A cada 6 horas
**Horários:** 00:00, 06:00, 12:00, 18:00

### 2. **Relatório Diário** (1x por dia)
Envia resumo do dia com estatísticas de clientes, mensagens e conversão.

**URL:** `https://bot-travessia.onrender.com/daily-stats?notify=true`
**Frequência:** 1x por dia
**Horário:** 18:00 (final do expediente)

### 3. **Health Check** (a cada 1 hora)
Verifica se todos os componentes (database, logs, métricas) estão funcionando.

**URL:** `https://bot-travessia.onrender.com/check-health-components`
**Frequência:** A cada 1 hora
**Horários:** De hora em hora

### 4. **Performance Check** (a cada 3 horas)
Verifica se há operações lentas (>2 segundos).

**URL:** `https://bot-travessia.onrender.com/check-performance`
**Frequência:** A cada 3 horas
**Horários:** 00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00

---

## 🔧 Opção 1: cron-job.org (RECOMENDADO)

**Vantagens:**
- ✅ 100% Gratuito
- ✅ Sem limite de jobs
- ✅ Interface simples
- ✅ Notificações de erro por email
- ✅ Logs de execução

### Passo a Passo:

#### 1. Criar Conta
1. Acesse: https://cron-job.org/en/signup/
2. Preencha email e senha
3. Confirme email

#### 2. Adicionar Jobs

##### Job 1: Alerta de Inatividade
```
Título: Bot Travessia - Alerta Inatividade
URL: https://bot-travessia.onrender.com/check-inactivity?hours=12
Frequência: Every 6 hours
Horários: 00:00, 06:00, 12:00, 18:00
```

**Configuração no cron-job.org:**
- Clique em "Create cronjob"
- **Title:** `Bot Travessia - Alerta Inatividade`
- **Address (URL):** `https://bot-travessia.onrender.com/check-inactivity?hours=12`
- **Schedule:**
  - Type: `Every 6 hours`
  - Start time: `00:00`
- **Enabled:** ✅
- **Save job failure logs:** ✅
- Clique em "Create cronjob"

##### Job 2: Relatório Diário
```
Título: Bot Travessia - Relatório Diário
URL: https://bot-travessia.onrender.com/daily-stats?notify=true
Frequência: Once a day
Horário: 18:00
```

**Configuração no cron-job.org:**
- Clique em "Create cronjob"
- **Title:** `Bot Travessia - Relatório Diário`
- **Address (URL):** `https://bot-travessia.onrender.com/daily-stats?notify=true`
- **Schedule:**
  - Type: `Once a day`
  - Time: `18:00`
- **Enabled:** ✅
- Clique em "Create cronjob"

##### Job 3: Health Check
```
Título: Bot Travessia - Health Check
URL: https://bot-travessia.onrender.com/check-health-components
Frequência: Every hour
```

**Configuração no cron-job.org:**
- Clique em "Create cronjob"
- **Title:** `Bot Travessia - Health Check`
- **Address (URL):** `https://bot-travessia.onrender.com/check-health-components`
- **Schedule:**
  - Type: `Every hour`
- **Enabled:** ✅
- Clique em "Create cronjob"

##### Job 4: Performance Check
```
Título: Bot Travessia - Performance Check
URL: https://bot-travessia.onrender.com/check-performance
Frequência: Every 3 hours
```

**Configuração no cron-job.org:**
- Clique em "Create cronjob"
- **Title:** `Bot Travessia - Performance Check`
- **Address (URL):** `https://bot-travessia.onrender.com/check-performance`
- **Schedule:**
  - Type: `Every 3 hours`
  - Start time: `00:00`
- **Enabled:** ✅
- Clique em "Create cronjob"

---

## 🔧 Opção 2: UptimeRobot

**Vantagens:**
- ✅ Gratuito (50 monitores)
- ✅ Dashboard de uptime
- ✅ Notificações por email/Telegram/Slack
- ✅ Logs de execução

### Passo a Passo:

#### 1. Criar Conta
1. Acesse: https://uptimerobot.com/signUp
2. Preencha dados e confirme email

#### 2. Adicionar Monitores

##### Monitor 1: Alerta de Inatividade
```
Monitor Type: HTTP(s)
Friendly Name: Bot Travessia - Inatividade
URL: https://bot-travessia.onrender.com/check-inactivity?hours=12
Monitoring Interval: 6 hours (360 minutes)
```

**Configuração:**
- Clique em "+ Add New Monitor"
- **Monitor Type:** `HTTP(s)`
- **Friendly Name:** `Bot Travessia - Inatividade`
- **URL (or IP):** `https://bot-travessia.onrender.com/check-inactivity?hours=12`
- **Monitoring Interval:** `360 minutes` (6 horas)
- Clique em "Create Monitor"

##### Monitor 2: Relatório Diário
```
Monitor Type: HTTP(s)
Friendly Name: Bot Travessia - Relatório Diário
URL: https://bot-travessia.onrender.com/daily-stats?notify=true
Monitoring Interval: 1440 minutes (1 dia)
```

##### Monitor 3: Health Check
```
Monitor Type: HTTP(s)
Friendly Name: Bot Travessia - Health
URL: https://bot-travessia.onrender.com/check-health-components
Monitoring Interval: 60 minutes (1 hora)
```

##### Monitor 4: Performance Check
```
Monitor Type: HTTP(s)
Friendly Name: Bot Travessia - Performance
URL: https://bot-travessia.onrender.com/check-performance
Monitoring Interval: 180 minutes (3 horas)
```

---

## 🔧 Opção 3: EasyCron

**Vantagens:**
- ✅ Gratuito (até 10 cron jobs)
- ✅ Interface simples
- ✅ Logs de execução

### Passo a Passo:

1. Acesse: https://www.easycron.com/user/register
2. Crie conta gratuita
3. Adicione os 4 jobs com as mesmas URLs e frequências acima

---

## 🔧 Opção 4: Render Cron Jobs (Pago - $1/mês)

Se preferir uma solução integrada ao Render:

**Criar arquivo `render.yaml` na raiz do projeto:**

```yaml
services:
  # Serviço principal do bot
  - type: web
    name: bot-travessia
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py

  # Cron job: Alerta de Inatividade
  - type: cron
    name: check-inactivity
    env: python
    schedule: "0 */6 * * *"  # A cada 6 horas
    buildCommand: pip install -r requirements.txt
    startCommand: curl https://bot-travessia.onrender.com/check-inactivity?hours=12

  # Cron job: Relatório Diário
  - type: cron
    name: daily-report
    env: python
    schedule: "0 18 * * *"  # Diariamente às 18h
    buildCommand: pip install -r requirements.txt
    startCommand: curl https://bot-travessia.onrender.com/daily-stats?notify=true

  # Cron job: Health Check
  - type: cron
    name: health-check
    env: python
    schedule: "0 * * * *"  # A cada hora
    buildCommand: pip install -r requirements.txt
    startCommand: curl https://bot-travessia.onrender.com/check-health-components

  # Cron job: Performance Check
  - type: cron
    name: performance-check
    env: python
    schedule: "0 */3 * * *"  # A cada 3 horas
    buildCommand: pip install -r requirements.txt
    startCommand: curl https://bot-travessia.onrender.com/check-performance
```

**Custo:** $1/mês por cada cron job = $4/mês total

---

## 📊 Resumo de Frequências

| Job | Frequência | Horários | Alertas/Dia |
|-----|-----------|----------|-------------|
| Inatividade | 6h | 00:00, 06:00, 12:00, 18:00 | 4x (se inativo) |
| Relatório Diário | 24h | 18:00 | 1x |
| Health Check | 1h | De hora em hora | 24x (se problema) |
| Performance | 3h | 00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00 | 8x (se lento) |

**Total de chamadas/dia:**
- Chamadas: 4 + 1 + 24 + 8 = **37 requisições/dia**
- Alertas: Só quando houver problema

---

## ✅ Verificação

Após configurar os cron jobs, você receberá no Telegram:

### **Primeira execução:**
- ⚠️ Alerta de inatividade (pois não há mensagens há 12h+)
- 📊 Relatório diário (às 18h)
- 💚 Health check (se componentes OK, não envia nada)
- ⚡ Performance check (se operações rápidas, não envia nada)

### **Formato das mensagens:**
Todas as mensagens terão **botões clicáveis**:
```
⚠️ Alerta de Inatividade

🕐 Nenhuma mensagem recebida nas últimas 12 horas
...

[🔧 Testar Webhook] [📊 Ver Dashboard]
```

---

## 🐛 Troubleshooting

### Job não está executando
1. Verifique se está "Enabled" no serviço
2. Verifique logs de execução
3. Teste a URL manualmente no navegador

### Não recebo alertas no Telegram
1. Teste manualmente: `curl "https://bot-travessia.onrender.com/test-telegram"`
2. Verifique se `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` estão corretos no .env
3. Verifique logs do bot: https://dashboard.render.com

### Recebo muitos alertas
- **Inatividade:** Aumente o intervalo de 12h para 24h na URL
- **Performance:** Normal se bot estiver lento - otimize código
- **Health:** Verifique qual componente está falhando

---

## 📝 Manutenção

### Desabilitar alertas temporariamente
- No cron-job.org: Desmarque "Enabled" no job
- No UptimeRobot: Pause o monitor

### Ajustar frequências
- Edite o job e mude o schedule
- Recomendado manter inatividade em 6h e relatório em 1x/dia

### Monitorar execuções
- Todos os serviços guardam logs de execução
- Verifique se jobs estão retornando HTTP 200

---

**Recomendação final:** Use **cron-job.org** - é o mais simples, gratuito e confiável! 🎯
