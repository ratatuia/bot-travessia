# 📊 Guia do Dashboard Web - Bot Travessia

## 🎯 **Acesso Rápido**

### **Em Produção (Render)**
```
https://bot-travessia.onrender.com/dashboard
```

### **Local (Desenvolvimento)**
```
http://localhost:5000/dashboard
```

---

## ✨ **Funcionalidades**

### **1. Overview em Tempo Real**
- ⏱️ **Uptime**: Tempo que o bot está rodando
- 👥 **Total Clientes**: Quantidade de clientes registrados
- 💬 **Mensagens (24h)**: Volume nas últimas 24 horas
- 🎯 **Taxa de Conversão**: % de clientes que completam jornada

### **2. Gráficos Interativos**

#### **📊 Atividade por Hora**
- Linha do tempo das últimas 24h
- Identifique horários de pico
- Planeje recursos/atendimento

#### **🔄 Funil de Conversão**
- Visualize etapas da jornada
- Identifique onde clientes abandonam
- Otimize pontos de atrito

#### **⚡ Performance (Top 5)**
- Operações mais lentas
- Identifique bottlenecks
- Monitore tempos de resposta

#### **📈 Clientes por Estado**
- Distribuição nos estados da conversa
- Onde clientes estão agora
- Fluxo em tempo real

### **3. Health Status**
- 🗄️ **Database**: Status de conexão
- 📝 **Logs**: Sistema de logging ativo
- 📊 **Métricas**: Coleta funcionando

### **4. Auto-Refresh**
- Atualização automática a cada 30 segundos
- Countdown visível
- Botão manual de refresh

---

## 🚀 **Como Usar**

### **Monitoramento Diário**

1. **Abra o dashboard** ao começar o dia
2. **Verifique KPIs principais**: Clientes novos, conversão
3. **Analise funil**: Identifique dropoff points
4. **Cheque health**: Todos componentes online?

### **Debug de Problemas**

**Problema: Taxa de conversão caiu**
1. Vá em **Funil de Conversão**
2. Veja onde há maior abandono
3. Analise logs para essa etapa
4. Ajuste mensagens/fluxo

**Problema: Bot lento**
1. Vá em **Performance**
2. Identifique operações lentas (>1000ms)
3. Otimize código dessas operações
4. Monitore melhoria

### **Análise de Tráfego**

1. **Atividade por Hora**: Identifique padrões
   - Pico às 10h? Escale recursos
   - Silêncio à noite? Manutenções

2. **Clientes por Estado**: Veja distribuição
   - Muitos em "aguardando_email"? Simplifique
   - Poucos em "menu"? Melhore onboarding

---

## 🔌 **API Endpoints**

### **Dados Completos**
```bash
GET /api/dashboard/data
```
Retorna tudo (métricas + stats + health)

### **Apenas Métricas**
```bash
GET /api/dashboard/metrics
```
Uptime, counters, timings, gauges

### **Apenas Estatísticas**
```bash
GET /api/dashboard/stats
```
Dados do banco (clientes, conversão, etc)

### **Health Check**
```bash
GET /api/dashboard/health
```
Status dos componentes

### **Health Detalhado**
```bash
GET /api/health/detailed
```
Health check com mensagens descritivas

---

## 📱 **Design Responsivo**

O dashboard se adapta automaticamente a:
- 🖥️ Desktop (full features)
- 💻 Tablet (grid ajustado)
- 📱 Mobile (stack vertical)

---

## ⚙️ **Customização**

### **Mudar Intervalo de Refresh**

Edite `templates/dashboard.html`, linha ~650:

```javascript
countdown = 30;  // Segundos (mude para 60, 120, etc)
```

### **Adicionar Novo Gráfico**

1. **HTML** (templates/dashboard.html):
```html
<div class="chart-card">
    <h3>🆕 Novo Gráfico</h3>
    <canvas id="novoChart"></canvas>
</div>
```

2. **JavaScript** (templates/dashboard.html):
```javascript
const novoCtx = document.getElementById('novoChart').getContext('2d');
novoChart = new Chart(novoCtx, {
    type: 'bar',  // ou 'line', 'doughnut', etc
    data: { /* dados */ },
    options: chartOptions
});
```

3. **API** (dashboard_routes.py):
Adicione dados no endpoint `/api/dashboard/data`

### **Mudar Cores**

Edite `templates/dashboard.html`, seção `<style>`:

```css
/* Gradiente principal */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Cor primária */
color: #667eea;
```

---

## 🎨 **Comparação com Dashboard Figaro**

| Aspecto | Figaro | Travessia Bot |
|---------|--------|---------------|
| **Framework** | Custom | Flask + Chart.js |
| **Deploy** | Render | Render (integrado) |
| **Responsivo** | ✅ | ✅ |
| **Auto-refresh** | ✅ (2 min) | ✅ (30 seg) |
| **Design** | Dark mode | Light + gradientes |
| **Gráficos** | Múltiplos | 4 principais |
| **Health Status** | APIs | Componentes |

**Similaridades:**
- Design moderno e limpo
- KPIs em cards
- Gráficos interativos
- Status de APIs/componentes
- Responsivo

**Diferenças:**
- Travessia usa Chart.js (mais leve)
- Integrado ao bot (não precisa deploy separado)
- Focado em conversação (funil, estados)

---

## 🐛 **Troubleshooting**

### **Dashboard não carrega**

1. Verifique se bot está rodando:
   ```bash
   curl https://bot-travessia.onrender.com/health
   ```

2. Verifique logs no Render

3. Teste rota diretamente:
   ```bash
   curl https://bot-travessia.onrender.com/api/dashboard/data
   ```

### **Gráficos vazios**

**Causa**: Sem dados no banco ainda

**Solução**:
1. Envie mensagens de teste no WhatsApp
2. Aguarde alguns minutos
3. Refresh do dashboard

### **Erro "Cannot read property 'labels'"**

**Causa**: Dados inválidos da API

**Solução**:
1. Verifique formato do JSON: `/api/dashboard/data`
2. Confirme que `db_stats` e `metrics` existem
3. Veja logs do console (F12 no browser)

### **Health Status "Offline"**

**Causa**: Arquivos não encontrados

**Solução**:
```bash
# Inicializar métricas
python init_metrics.py

# Verificar estrutura
ls logs/
ls templates/
```

---

## 📊 **Métricas Disponíveis**

### **Counters** (incremental)
- `conversation.started`
- `conversation.completed`
- `conversation.abandoned`
- `message.received`
- `state.{nome_estado}`
- `error.{tipo_erro}`

### **Timings** (duração em ms)
- `operation.process_message`
- `api.openai.chat`
- `api.twilio.send`
- `function.{nome_funcao}`

### **Gauges** (valor atual)
- `active_conversations`
- `database.size_mb`
- `memory.usage_mb`

---

## 🚀 **Próximas Melhorias**

### **Curto Prazo**
- [ ] Filtro de data (última semana, mês)
- [ ] Exportar dados (CSV, JSON)
- [ ] Alertas visuais (taxa conversão < 20%)
- [ ] Comparação período anterior

### **Médio Prazo**
- [ ] Dark mode toggle
- [ ] Múltiplos dashboards (por região, produto)
- [ ] Drill-down (clicar gráfico → detalhes)
- [ ] Notificações push (WebSockets)

### **Longo Prazo**
- [ ] Predições (ML para prever conversão)
- [ ] A/B testing visualization
- [ ] Heatmaps de interação
- [ ] Gravação de sessões

---

## 📚 **Recursos Externos**

- **Chart.js Docs**: https://www.chartjs.org/docs/
- **Flask Blueprints**: https://flask.palletsprojects.com/blueprints/
- **Responsive Design**: https://developer.mozilla.org/pt-BR/docs/Learn/CSS/CSS_layout/Responsive_Design

---

## ✅ **Checklist de Deploy**

Antes de considerar o dashboard em produção:

- [x] Dashboard acessível em `/dashboard`
- [x] API retorna dados válidos
- [x] Gráficos renderizam corretamente
- [x] Auto-refresh funcionando
- [x] Responsivo (teste mobile)
- [x] Health checks passando
- [ ] Métricas populando (após algumas conversas)
- [ ] Performance aceitável (<2s load)

---

## 🆘 **Suporte**

### **Ver Logs da API**
```bash
# No Render, vá em: Logs
# Filtre por: "dashboard"
```

### **Testar API Localmente**
```bash
python app.py
curl http://localhost:5000/api/dashboard/data | jq '.'
```

### **Debug JavaScript**
1. Abra dashboard
2. Pressione F12 (DevTools)
3. Vá em Console
4. Veja erros

---

**Dashboard Web Integrado v1.0**
**Bot Travessia dos Sonhos**
**Última atualização**: 16/10/2025
