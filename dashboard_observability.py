"""
Dashboard de Observabilidade - Bot Travessia dos Sonhos
Visualização em tempo real de métricas, logs e performance
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import sqlite3

# Configuração da página
st.set_page_config(
    page_title="🔍 Observability Dashboard - Travessia Bot",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .status-healthy {
        color: #28a745;
        font-weight: bold;
    }
    .status-degraded {
        color: #ffc107;
        font-weight: bold;
    }
    .status-unhealthy {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Paths
DB_PATH = "travessia_bot.db"
LOG_FILE = "logs/bot.log"
METRICS_FILE = "logs/metrics.json"


# ===================================
# Funções de Carregamento de Dados
# ===================================

@st.cache_data(ttl=60)
def load_metrics():
    """Carrega métricas do arquivo JSON"""
    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'uptime_seconds': 0,
        'counters': {},
        'gauges': {},
        'timings': {}
    }


@st.cache_data(ttl=30)
def load_logs(limit=100):
    """Carrega logs recentes"""
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                for line in f.readlines()[-limit:]:
                    try:
                        log = json.loads(line.strip())
                        logs.append(log)
                    except json.JSONDecodeError:
                        # Skip non-JSON lines (console format)
                        pass
        except Exception as e:
            st.error(f"Erro ao carregar logs: {e}")
    return logs


@st.cache_data(ttl=60)
def load_database_stats():
    """Carrega estatísticas do banco de dados"""
    if not os.path.exists(DB_PATH):
        return {}

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        stats = {}

        # Total de clientes
        cursor.execute("SELECT COUNT(*) FROM clientes")
        stats['total_clients'] = cursor.fetchone()[0]

        # Clientes por estado
        cursor.execute("""
            SELECT
                json_extract(dados, '$.estado') as estado,
                COUNT(*) as count
            FROM clientes
            WHERE dados IS NOT NULL
            GROUP BY estado
        """)
        stats['clients_by_state'] = dict(cursor.fetchall())

        # Clientes nas últimas 24h
        cursor.execute("""
            SELECT COUNT(*) FROM clientes
            WHERE datetime(ultima_interacao) >= datetime('now', '-1 day')
        """)
        stats['clients_24h'] = cursor.fetchone()[0]

        # Mensagens nas últimas 24h
        cursor.execute("""
            SELECT COUNT(*) FROM mensagens
            WHERE datetime(timestamp) >= datetime('now', '-1 day')
        """)
        stats['messages_24h'] = cursor.fetchone()[0]

        # Taxa de conversão (atendimento solicitado)
        cursor.execute("""
            SELECT COUNT(*) FROM clientes
            WHERE json_extract(dados, '$.estado') = 'atendimento_solicitado'
        """)
        completed = cursor.fetchone()[0]
        stats['conversion_rate'] = (completed / stats['total_clients'] * 100) if stats['total_clients'] > 0 else 0

        # Atividade por hora (últimas 24h)
        cursor.execute("""
            SELECT
                strftime('%H', timestamp) as hour,
                COUNT(*) as count
            FROM mensagens
            WHERE datetime(timestamp) >= datetime('now', '-1 day')
            GROUP BY hour
            ORDER BY hour
        """)
        stats['activity_by_hour'] = dict(cursor.fetchall())

        conn.close()
        return stats

    except Exception as e:
        st.error(f"Erro ao carregar stats do banco: {e}")
        return {}


# ===================================
# Componentes do Dashboard
# ===================================

def render_header():
    """Renderiza cabeçalho do dashboard"""
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        st.markdown('<p class="main-header">🔍 Dashboard de Observabilidade</p>', unsafe_allow_html=True)

    with col2:
        st.metric("Status", "🟢 Online")

    with col3:
        if st.button("🔄 Atualizar", type="primary"):
            st.cache_data.clear()
            st.rerun()


def render_overview_metrics(metrics_data, db_stats):
    """Renderiza métricas de overview"""
    st.subheader("📊 Métricas Principais")

    col1, col2, col3, col4 = st.columns(4)

    # Uptime
    uptime_seconds = metrics_data.get('uptime_seconds', 0)
    uptime_hours = uptime_seconds / 3600
    with col1:
        st.metric(
            "⏱️ Uptime",
            f"{uptime_hours:.1f}h",
            delta=None
        )

    # Total de clientes
    with col2:
        st.metric(
            "👥 Total Clientes",
            db_stats.get('total_clients', 0),
            delta=f"+{db_stats.get('clients_24h', 0)} (24h)"
        )

    # Mensagens 24h
    with col3:
        st.metric(
            "💬 Mensagens (24h)",
            db_stats.get('messages_24h', 0)
        )

    # Taxa de conversão
    with col4:
        conversion = db_stats.get('conversion_rate', 0)
        st.metric(
            "🎯 Taxa Conversão",
            f"{conversion:.1f}%"
        )


def render_performance_chart(metrics_data):
    """Renderiza gráficos de performance"""
    st.subheader("⚡ Performance")

    timings = metrics_data.get('timings', {})

    if not timings:
        st.info("Nenhuma métrica de performance disponível ainda")
        return

    # Preparar dados
    timing_data = []
    for key, values in timings.items():
        timing_data.append({
            'Operação': key.replace('operation.', '').replace('function.', ''),
            'Média (ms)': values.get('avg_ms', 0),
            'Mín (ms)': values.get('min_ms', 0),
            'Máx (ms)': values.get('max_ms', 0),
            'Count': values.get('count', 0),
            'Erros': values.get('errors', 0)
        })

    df = pd.DataFrame(timing_data)

    # Gráfico de barras de tempo médio
    fig = px.bar(
        df.sort_values('Média (ms)', ascending=False).head(10),
        x='Operação',
        y='Média (ms)',
        title='Top 10 Operações por Tempo Médio',
        color='Média (ms)',
        color_continuous_scale='RdYlGn_r'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Tabela detalhada
    with st.expander("📋 Detalhes de Performance"):
        st.dataframe(
            df.style.background_gradient(subset=['Média (ms)'], cmap='RdYlGn_r'),
            use_container_width=True
        )


def render_conversation_funnel(db_stats):
    """Renderiza funil de conversão"""
    st.subheader("🔄 Funil de Conversão")

    states_by_count = db_stats.get('clients_by_state', {})

    # Ordenar estados por ordem do fluxo
    state_order = [
        'aguardando_nome',
        'aguardando_email',
        'menu',
        'pos_conhecer_tripulacao',
        'perguntando_interesses',
        'perguntando_periodo',
        'perguntando_duracao',
        'perguntando_destino',
        'perguntando_forma_contato',
        'perguntando_horario',
        'atendimento_solicitado'
    ]

    funnel_data = []
    for state in state_order:
        if state in states_by_count:
            funnel_data.append({
                'Estado': state.replace('_', ' ').title(),
                'Quantidade': states_by_count[state]
            })

    if funnel_data:
        df = pd.DataFrame(funnel_data)

        fig = go.Figure(go.Funnel(
            y=df['Estado'],
            x=df['Quantidade'],
            textinfo="value+percent initial",
            marker=dict(color='royalblue')
        ))

        fig.update_layout(
            title='Jornada do Cliente',
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Dados insuficientes para gerar funil")


def render_activity_heatmap(db_stats):
    """Renderiza heatmap de atividade por hora"""
    st.subheader("🕐 Atividade por Horário")

    activity = db_stats.get('activity_by_hour', {})

    if not activity:
        st.info("Nenhuma atividade registrada nas últimas 24h")
        return

    # Preparar dados (garantir todas as 24 horas)
    hours = list(range(24))
    counts = [activity.get(f"{h:02d}", 0) for h in hours]

    fig = go.Figure(data=go.Bar(
        x=[f"{h:02d}:00" for h in hours],
        y=counts,
        marker=dict(
            color=counts,
            colorscale='Viridis',
            showscale=True
        )
    ))

    fig.update_layout(
        title='Mensagens por Hora (Últimas 24h)',
        xaxis_title='Hora',
        yaxis_title='Mensagens',
        height=300
    )

    st.plotly_chart(fig, use_container_width=True)


def render_logs_viewer(logs):
    """Renderiza visualizador de logs"""
    st.subheader("📝 Logs Recentes")

    # Filtros
    col1, col2, col3 = st.columns(3)

    with col1:
        level_filter = st.multiselect(
            "Nível",
            options=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            default=['INFO', 'WARNING', 'ERROR', 'CRITICAL']
        )

    with col2:
        module_filter = st.multiselect(
            "Módulo",
            options=list(set([log.get('module', 'unknown') for log in logs])),
            default=None
        )

    with col3:
        limit = st.slider("Quantidade", 10, 500, 100)

    # Filtrar logs
    filtered_logs = logs[-limit:]

    if level_filter:
        filtered_logs = [log for log in filtered_logs if log.get('level') in level_filter]

    if module_filter:
        filtered_logs = [log for log in filtered_logs if log.get('module') in module_filter]

    # Exibir logs
    if not filtered_logs:
        st.info("Nenhum log encontrado com os filtros selecionados")
        return

    # Estatísticas de logs
    level_counts = Counter([log.get('level', 'UNKNOWN') for log in filtered_logs])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("INFO", level_counts.get('INFO', 0))
    with col2:
        st.metric("WARNING", level_counts.get('WARNING', 0))
    with col3:
        st.metric("ERROR", level_counts.get('ERROR', 0))
    with col4:
        st.metric("CRITICAL", level_counts.get('CRITICAL', 0))

    # Tabela de logs
    log_data = []
    for log in reversed(filtered_logs):
        log_data.append({
            'Timestamp': log.get('timestamp', ''),
            'Level': log.get('level', ''),
            'Module': log.get('module', ''),
            'Message': log.get('message', '')[:100] + ('...' if len(log.get('message', '')) > 100 else '')
        })

    df = pd.DataFrame(log_data)

    # Aplicar cores por nível
    def highlight_level(row):
        colors = {
            'DEBUG': 'background-color: #e3f2fd',
            'INFO': 'background-color: #e8f5e9',
            'WARNING': 'background-color: #fff3e0',
            'ERROR': 'background-color: #ffebee',
            'CRITICAL': 'background-color: #f44336; color: white'
        }
        return [colors.get(row['Level'], '')] * len(row)

    st.dataframe(
        df.style.apply(highlight_level, axis=1),
        use_container_width=True,
        height=400
    )

    # Detalhes do log selecionado
    with st.expander("🔍 Ver Detalhes Completos"):
        selected_idx = st.number_input("Índice do log", 0, len(filtered_logs) - 1, 0)
        if 0 <= selected_idx < len(filtered_logs):
            st.json(filtered_logs[selected_idx])


def render_health_status():
    """Renderiza status de health checks"""
    st.subheader("💚 Health Checks")

    col1, col2, col3 = st.columns(3)

    # Database
    with col1:
        db_healthy = os.path.exists(DB_PATH)
        st.markdown(f"""
        <div style="padding: 1rem; border-radius: 10px; background: {'#d4edda' if db_healthy else '#f8d7da'};">
            <h3>🗄️ Database</h3>
            <p class="{'status-healthy' if db_healthy else 'status-unhealthy'}">
                {'✅ Conectado' if db_healthy else '❌ Desconectado'}
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Logs
    with col2:
        logs_healthy = os.path.exists(LOG_FILE)
        st.markdown(f"""
        <div style="padding: 1rem; border-radius: 10px; background: {'#d4edda' if logs_healthy else '#f8d7da'};">
            <h3>📝 Logs</h3>
            <p class="{'status-healthy' if logs_healthy else 'status-unhealthy'}">
                {'✅ Ativo' if logs_healthy else '❌ Inativo'}
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Métricas
    with col3:
        metrics_healthy = os.path.exists(METRICS_FILE)
        st.markdown(f"""
        <div style="padding: 1rem; border-radius: 10px; background: {'#d4edda' if metrics_healthy else '#f8d7da'};">
            <h3>📊 Métricas</h3>
            <p class="{'status-healthy' if metrics_healthy else 'status-unhealthy'}">
                {'✅ Coletando' if metrics_healthy else '❌ Parado'}
            </p>
        </div>
        """, unsafe_allow_html=True)


# ===================================
# Main Dashboard
# ===================================

def main():
    # Sidebar
    with st.sidebar:
        st.title("🔍 Observability")
        st.markdown("---")

        page = st.radio(
            "Navegação",
            ["📊 Overview", "⚡ Performance", "📝 Logs", "🔄 Conversões", "💚 Health"],
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.info(f"Última atualização: {datetime.now().strftime('%H:%M:%S')}")

        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()

    # Carregar dados
    metrics_data = load_metrics()
    db_stats = load_database_stats()
    logs = load_logs(500)

    # Header
    render_header()
    st.markdown("---")

    # Renderizar página selecionada
    if page == "📊 Overview":
        render_overview_metrics(metrics_data, db_stats)
        st.markdown("---")
        render_activity_heatmap(db_stats)
        st.markdown("---")
        render_health_status()

    elif page == "⚡ Performance":
        render_performance_chart(metrics_data)

    elif page == "📝 Logs":
        render_logs_viewer(logs)

    elif page == "🔄 Conversões":
        render_conversation_funnel(db_stats)

    elif page == "💚 Health":
        render_health_status()

        st.markdown("---")
        st.subheader("📊 Métricas do Sistema")

        col1, col2 = st.columns(2)

        with col1:
            if os.path.exists(LOG_FILE):
                log_size = os.path.getsize(LOG_FILE) / 1024 / 1024  # MB
                st.metric("Tamanho do Log", f"{log_size:.2f} MB")

        with col2:
            if os.path.exists(DB_PATH):
                db_size = os.path.getsize(DB_PATH) / 1024 / 1024  # MB
                st.metric("Tamanho do DB", f"{db_size:.2f} MB")


if __name__ == "__main__":
    main()
