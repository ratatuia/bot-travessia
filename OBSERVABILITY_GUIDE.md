# 🔍 Guia de Observabilidade - Bot Travessia dos Sonhos

## 📋 Visão Geral

Este guia explica como usar o novo sistema de observabilidade world-class implementado no Bot Travessia.

### **O Que Foi Implementado**

✅ **Logs Estruturados (JSON)** - Logs em formato JSON com rotation automático
✅ **Métricas em Tempo Real** - Contadores, timings, gauges
✅ **Correlation IDs** - Rastreamento de requests end-to-end
✅ **Performance Monitoring** - Tracking automático de performance
✅ **Analytics de Conversação** - Insights sobre jornada do cliente
✅ **Dashboard Interativo** - Visualização em Streamlit
✅ **Health Checks** - Monitoramento de saúde do sistema

---

## 🚀 Quick Start

### 1. Acessar Dashboard de Observabilidade

```bash
# No diretório do projeto
streamlit run dashboard_observability.py
```

**URL**: http://localhost:8501

### 2. Explorar Métricas

O dashboard possui 5 seções:

- **📊 Overview**: Métricas principais + atividade por hora + health status
- **⚡ Performance**: Gráficos de tempo de resposta e operações
- **📝 Logs**: Visualizador de logs com filtros
- **🔄 Conversões**: Funil de conversão da jornada do cliente
- **💚 Health**: Status detalhado de todos os componentes

---

## 📊 Sistema de Logs

### **Logs Estruturados (JSON)**

Todos os logs agora são gravados em formato JSON estruturado em `logs/bot.log`:

```json
{
  "timestamp": "2025-10-16T14:30:45.123456",
  "level": "INFO",
  "logger": "travessia_bot",
  "message": "Conversation started",
  "module": "app",
  "function": "whatsapp_bot",
  "line": 315,
  "context": {
    "correlation_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
    "user_id": "whatsapp:+5511999999999",
    "event_type": "conversation_start"
  }
}
```

### **Rotation Automático**

- **Tamanho máximo por arquivo**: 10MB
- **Número de backups**: 5
- **Localização**: `logs/bot.log`, `logs/bot.log.1`, `logs/bot.log.2`, etc

### **Níveis de Log**

| Nível | Uso | Exemplo |
|-------|-----|---------|
| `DEBUG` | Informações técnicas detalhadas | Valores de variáveis, fluxo interno |
| `INFO` | Eventos importantes | Início de conversa, transições de estado |
| `WARNING` | Situações anormais não críticas | Email inválido, opção de menu não reconhecida |
| `ERROR` | Erros que não param o bot | Falha ao chamar API externa, timeout |
| `CRITICAL` | Erros graves que podem parar o bot | Banco de dados inacessível |

---

## 📈 Sistema de Métricas

### **Tipos de Métricas**

#### 1. **Contadores** (Counters)
Incrementam indefinidamente:

```python
from observability import metrics

metrics.increment('conversation.started')
metrics.increment('message.received', value=1, tags={'type': 'text'})
```

**Exemplos**:
- `conversation.started` - Total de conversas iniciadas
- `message.received` - Mensagens recebidas
- `state.menu` - Quantas vezes entraram no menu
- `error.validation` - Erros de validação

#### 2. **Timings**
Mede duração de operações (em ms):

```python
from observability import metrics

metrics.timing('operation.send_message', duration_ms=150.5)
```

**Exemplos**:
- `operation.process_message` - Tempo para processar mensagem
- `api.openai.chat` - Latência da API OpenAI
- `function.whatsapp_bot` - Tempo total do webhook

#### 3. **Gauges**
Valores instantâneos:

```python
from observability import metrics

metrics.gauge('database.connections', 5)
metrics.gauge('memory.usage_mb', 256.8)
```

**Exemplos**:
- `database.size_mb` - Tamanho do banco
- `active_conversations` - Conversas ativas agora
- `queue.length` - Tamanho da fila

### **Salvando Métricas**

Métricas são automaticamente salvas em `logs/metrics.json` periodicamente.

Para salvar manualmente:

```python
from observability import metrics

metrics.save_to_file()
```

---

## 🔗 Correlation IDs

### **O Que São**

Correlation IDs são UUIDs únicos que permitem rastrear uma requisição através de todo o sistema.

### **Como Funcionam**

```python
from observability import CorrelationContext, logger

# Gerado automaticamente no início de cada requisição
correlation_id = CorrelationContext.get_id()

# Todos os logs subsequentes incluem o correlation_id
logger.info("Processing message", user_id="123")
# Resultado: {"correlation_id": "...", "message": "Processing message", ...}
```

### **Benefícios**

1. **Rastreamento End-to-End**: Acompanhe uma conversa completa
2. **Debug Facilitado**: Encontre todos os logs relacionados a um erro
3. **Análise de Performance**: Veja quanto tempo cada etapa levou

### **Exemplo de Busca**

```bash
# Buscar todos logs de uma conversa específica
cat logs/bot.log | grep "a1b2c3d4-5678"
```

---

## ⚡ Performance Monitoring

### **Uso Automático com Decorator**

```python
from observability import with_correlation_id

@with_correlation_id
def process_order(order_id):
    # Função automaticamente loggada com:
    # - Início e fim
    # - Duração (timing metric)
    # - Correlation ID
    # - Erros (se houver)
    pass
```

### **Uso Manual com Context Manager**

```python
from observability import PerformanceMonitor

with PerformanceMonitor("send_to_openai"):
    response = openai.chat.completions.create(...)
    # Automaticamente grava:
    # - metrics.timing('operation.send_to_openai', duration_ms)
    # - logger.info com duração
```

---

## 🎯 Analytics de Conversação

### **Tracking de Sessões**

```python
from observability import analytics

# Iniciar sessão
analytics.start_session(user_id="whatsapp:+5511999999999")

# Registrar mensagem
analytics.track_message(user_id, message_type="text")

# Registrar transição de estado
analytics.track_state_transition(
    user_id,
    from_state="aguardando_nome",
    to_state="aguardando_email"
)

# Registrar erro
analytics.track_error(user_id, error_type="validation")

# Completar sessão
analytics.complete_session(user_id, success=True)
```

### **Métricas Automáticas**

Ao usar o analytics, as seguintes métricas são geradas automaticamente:

- `conversation.started` - Novas conversas
- `conversation.completed` - Conversas finalizadas com sucesso
- `conversation.abandoned` - Conversas abandonadas
- `conversation.duration` - Duração média
- `message.{type}` - Mensagens por tipo
- `state.{state_name}` - Entradas por estado
- `error.{error_type}` - Erros por tipo

---

## 💚 Health Checks

### **Verificações Incluídas**

1. **Logs**: Arquivo de log está acessível?
2. **Database**: Banco de dados conectado?
3. **Métricas**: Sistema de métricas funcionando?

### **Adicionar Novos Checks**

```python
from observability import health_checker

def check_openai():
    """Verifica se OpenAI está acessível"""
    try:
        # Fazer teste básico
        return True
    except:
        return False

health_checker.register_check('openai', check_openai)
```

### **Executar Checks**

```python
from observability import health_checker

result = health_checker.run_checks()
# {
#   'status': 'healthy',  # ou 'degraded'
#   'timestamp': '2025-10-16T14:30:45',
#   'checks': {
#     'logs': {'status': 'pass', 'duration_ms': 0.5},
#     'database': {'status': 'pass', 'duration_ms': 2.1},
#     'openai': {'status': 'pass', 'duration_ms': 150.3}
#   }
# }
```

---

## 📊 Dashboard de Observabilidade

### **Acessando**

```bash
streamlit run dashboard_observability.py
```

### **Funcionalidades**

#### **1. Overview**
- KPIs principais (Uptime, Clientes, Mensagens, Taxa de Conversão)
- Atividade por horário (últimas 24h)
- Health status de todos os componentes

#### **2. Performance**
- Gráfico de barras: Top 10 operações mais lentas
- Tabela detalhada: Média, mín, máx, count, erros
- Identificação de bottlenecks

#### **3. Logs**
- Visualizador em tempo real
- Filtros por nível (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Filtros por módulo
- Estatísticas de logs
- Visualização detalhada (JSON completo)

#### **4. Conversões**
- Funil de conversão visual
- Quantos clientes em cada estado
- Taxa de dropout por etapa

#### **5. Health**
- Status de database, logs, métricas
- Tamanho dos arquivos
- Verificações de conectividade

### **Atualização**

- **Automática**: Dados re-carregados a cada 30-60 segundos (cache TTL)
- **Manual**: Botão "🔄 Refresh Data" no sidebar

---

## 🔔 Alertas (Telegram)

### **Alertas Automáticos**

O sistema já envia alertas para Telegram em caso de erros:

```python
from log_service import capturar_erro

try:
    # Operação crítica
    pass
except Exception as e:
    capturar_erro("operation_name", e)
    # Envia alerta: "🚨 [BOT ALERTA] Erro em operation_name: ..."
```

### **Alertas Customizados**

```python
from log_service import enviar_alerta_telegram

enviar_alerta_telegram("Pico de tráfego detectado: 500 req/min")
```

---

## 📁 Estrutura de Arquivos

```
bot-travessia-v2/
├── logs/                          # Diretório de logs
│   ├── bot.log                    # Log principal (JSON)
│   ├── bot.log.1                  # Backup 1
│   ├── bot.log.2                  # Backup 2
│   └── metrics.json               # Métricas agregadas
│
├── observability.py               # Sistema de observabilidade
├── dashboard_observability.py     # Dashboard Streamlit
├── log_service.py                 # Serviço de logs (legado - manter para alertas)
└── app.py                         # Aplicação principal (integrada)
```

---

## 🎯 Casos de Uso

### **Caso 1: Debug de Erro em Produção**

**Problema**: Cliente reporta que bot não respondeu.

**Solução**:
1. Acesse dashboard → Logs
2. Filtre por ERROR/CRITICAL
3. Busque pelo número do cliente ou horário
4. Identifique correlation_id do erro
5. Veja sequência completa de eventos:
   ```bash
   cat logs/bot.log | grep "correlation_id_aqui" | jq '.'
   ```

### **Caso 2: Identificar Bottleneck de Performance**

**Problema**: Bot está lento.

**Solução**:
1. Acesse dashboard → Performance
2. Veja gráfico "Top 10 Operações por Tempo Médio"
3. Identifique operação lenta (ex: `api.openai.chat` = 5000ms)
4. Otimize ou adicione cache

### **Caso 3: Análise de Conversão**

**Problema**: Poucos clientes completam a jornada.

**Solução**:
1. Acesse dashboard → Conversões
2. Veja funil: onde há maior dropout?
3. Exemplo: 50% abandonam em "perguntando_destino"
4. Simplifique essa etapa ou melhore mensagem

### **Caso 4: Monitoramento Proativo**

**Setup**:
1. Deixe dashboard aberto em tela secundária
2. Configure alertas Telegram para erros críticos
3. Monitore métricas:
   - Taxa de conversão caindo? Investigar.
   - Tempo de resposta subindo? Escalar recursos.
   - Erros aumentando? Checar logs.

---

## 📊 Métricas Importantes a Monitorar

### **Performance**
- `operation.process_message` < 500ms (alvo)
- `api.openai.chat` < 3000ms (alvo)
- `function.whatsapp_bot` < 1000ms (alvo)

### **Conversão**
- Taxa de conversão > 30% (alvo)
- Dropout em "perguntando_destino" < 20%
- Clientes completando em < 5 minutos (média)

### **Saúde**
- Uptime > 99%
- Erros < 1% das requisições
- Database response time < 50ms

---

## 🔧 Configuração Avançada

### **Ajustar Tamanho dos Logs**

Edite `observability.py`:

```python
MAX_LOG_SIZE = 20 * 1024 * 1024  # 20MB
BACKUP_COUNT = 10                 # 10 backups
```

### **Mudar Formato de Log**

Para logs mais legíveis em desenvolvimento:

```python
# Em observability.py, método __init__ do StructuredLogger
console_handler.setLevel(logging.DEBUG)  # Mais verboso
```

### **Adicionar Tags Customizadas**

```python
metrics.increment('api.call', tags={'service': 'openai', 'endpoint': 'chat'})
# Gera métrica: api.call[endpoint=chat,service=openai]
```

---

## 🚀 Próximos Passos

### **Integração com Serviços Externos**

1. **Sentry**: Tracking de erros em produção
   ```bash
   pip install sentry-sdk
   ```

2. **Prometheus**: Exportar métricas para Prometheus
   ```bash
   pip install prometheus-client
   ```

3. **Grafana**: Dashboards mais avançados
   - Conectar ao Prometheus
   - Criar alertas customizados

### **Melhorias Futuras**

- [ ] Exportar métricas para Prometheus
- [ ] Integração com Sentry
- [ ] Alertas inteligentes (anomaly detection)
- [ ] Tracing distribuído (OpenTelemetry)
- [ ] Dashboard mobile-friendly
- [ ] Exportação de relatórios (PDF)

---

## 📚 Referências

- **Logs Estruturados**: [12 Factor App - Logs](https://12factor.net/logs)
- **Métricas**: [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- **Observabilidade**: [Three Pillars of Observability](https://www.oreilly.com/library/view/distributed-systems-observability/9781492033431/)
- **Streamlit**: [Streamlit Docs](https://docs.streamlit.io/)

---

## 🆘 Troubleshooting

### **Dashboard não abre**

```bash
# Verificar se Streamlit está instalado
pip install streamlit

# Rodar novamente
streamlit run dashboard_observability.py
```

### **Logs não aparecem no dashboard**

1. Verificar se `logs/bot.log` existe
2. Verificar permissões do arquivo
3. Verificar se logs estão em formato JSON válido

### **Métricas não são salvas**

1. Verificar se diretório `logs/` existe
2. Executar manualmente:
   ```python
   from observability import metrics
   metrics.save_to_file()
   ```

---

**Sistema de Observabilidade v1.0**
**Bot Travessia dos Sonhos**
**Última atualização**: 16/10/2025
