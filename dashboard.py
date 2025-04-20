import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from log_service import registrar_log, capturar_erro
import json

# Logo URL
LOGO_URL = "https://res.cloudinary.com/dejuykey4/image/upload/v1744305156/Imagem_do_WhatsApp_de_2025-03-30_%C3%A0_s_12.03.57_889f472b_xziked.jpg"

# Configuração da página
st.set_page_config(
    page_title="Painel Travessia dos Sonhos",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado
st.markdown("""
<style>
    .main-header {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 2rem;
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 10px;
    }
    .logo-img {
        width: 100px;
        margin-right: 20px;
    }
    .title-container {
        display: flex;
        flex-direction: column;
    }
    .main-title {
        font-size: 2.5rem;
        margin: 0;
        color: #0066cc;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #4d4d4d;
    }
</style>
""", unsafe_allow_html=True)

# Header com logo e título
st.markdown(f"""
<div class="main-header">
    <img src="{LOGO_URL}" class="logo-img">
    <div class="title-container">
        <h1 class="main-title">Travessia dos Sonhos</h1>
        <p class="subtitle">Painel Administrativo</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Conexão com o banco de dados
@st.cache_resource
def get_connection():
    return sqlite3.connect('travessia_bot.db', check_same_thread=False)

conn = get_connection()

# Funções para carregar os dados
@st.cache_data(ttl=300)
def load_client_data():
    query = """
    SELECT 
        telefone, nome, email, estado, dados, 
        datetime(ultima_interacao) as ultima_interacao
    FROM clientes
    """
    df = pd.read_sql(query, conn)
    dados_expandidos = []
    for _, row in df.iterrows():
        cliente_dados = {
            'telefone': row['telefone'],
            'nome': row['nome'],
            'email': row['email'],
            'estado': row['estado'],
            'ultima_interacao': row['ultima_interacao']
        }
        if row['dados'] and row['dados'] != 'null':
            try:
                dados_json = json.loads(row['dados'])
                for key, value in dados_json.items():
                    cliente_dados[key] = value
            except:
                pass
        dados_expandidos.append(cliente_dados)
    return pd.DataFrame(dados_expandidos)

@st.cache_data(ttl=300)
def load_message_data():
    query = """
    SELECT 
        telefone, mensagem_cliente, mensagem_bot,
        datetime(timestamp) as timestamp, precisa_atendimento
    FROM mensagens
    ORDER BY timestamp DESC
    """
    return pd.read_sql(query, conn)

df_clientes = load_client_data()
df_mensagens = load_message_data()

# Sidebar
st.sidebar.image(LOGO_URL, width=200)
st.sidebar.title("🚢 Travessia dos Sonhos")

pagina = st.sidebar.radio(
    "Navegação",
    ["Visão Geral", "Preferências dos Clientes", "Atendimentos Pendentes", "Detalhes dos Clientes"]
)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Atualizar Dados"):
    st.cache_data.clear()
    st.experimental_rerun()

data_hoje = datetime.now().date()
data_inicio = st.sidebar.date_input("Data Inicial", data_hoje - timedelta(days=30))
data_fim = st.sidebar.date_input("Data Final", data_hoje)

df_clientes['data'] = pd.to_datetime(df_clientes['ultima_interacao']).dt.date
df_clientes_filtrado = df_clientes[(df_clientes['data'] >= data_inicio) & (df_clientes['data'] <= data_fim)]
df_mensagens['data'] = pd.to_datetime(df_mensagens['timestamp']).dt.date
df_mensagens_filtrado = df_mensagens[(df_mensagens['data'] >= data_inicio) & (df_mensagens['data'] <= data_fim)]

# Página: Visão Geral
if pagina == "Visão Geral":
    st.title("📊 Visão Geral")
    col1, col2, col3, col4 = st.columns(4)
    total_clientes = len(df_clientes_filtrado['telefone'].unique())
    col1.metric("Total de Clientes", total_clientes)
    clientes_completos = df_clientes_filtrado[df_clientes_filtrado['estado'] == 'atendimento_solicitado']
    taxa_conversao = round(len(clientes_completos) / total_clientes * 100, 1) if total_clientes > 0 else 0
    col2.metric("Clientes que Completaram", len(clientes_completos))
    col3.metric("Taxa de Conversão", f"{taxa_conversao}%")
    atendimentos = df_mensagens_filtrado[df_mensagens_filtrado['precisa_atendimento'] == 1]
    col4.metric("Solicitações de Atendimento", len(atendimentos))
    st.subheader("Atividade Diária")
    df_atividade = df_mensagens_filtrado.groupby('data').size().reset_index(name='mensagens')
    fig = px.line(df_atividade, x='data', y='mensagens', title="Mensagens por Dia", labels={"data": "Data", "mensagens": "Número de Mensagens"}, color_discrete_sequence=["#0066cc"])
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Estado dos Clientes")
    df_estados = df_clientes_filtrado['estado'].value_counts().reset_index()
    df_estados.columns = ['Estado', 'Quantidade']
    estado_nomes = {
        'aguardando_nome': 'Aguardando Nome',
        'aguardando_email': 'Aguardando Email',
        'menu': 'Menu Principal',
        'pos_conhecer_tripulacao': 'Conhecendo a Empresa',
        'perguntando_interesses': 'Informando Interesses',
        'apos_interesses': 'Após Informar Interesses',
        'perguntando_periodo_viagem': 'Escolhendo Período',
        'perguntando_duracao': 'Escolhendo Duração',
        'perguntando_destino': 'Escolhendo Destino',
        'perguntando_forma_contato': 'Escolhendo Forma de Contato',
        'perguntando_horario': 'Escolhendo Horário',
        'atendimento_solicitado': 'Atendimento Solicitado'
    }
    df_estados['Estado'] = df_estados['Estado'].map(lambda x: estado_nomes.get(x, x))
    fig = px.bar(df_estados, x='Estado', y='Quantidade', color='Quantidade', title="Distribuição de Estados dos Clientes", color_continuous_scale=px.colors.sequential.Blues)
    st.plotly_chart(fig, use_container_width=True)

# Página: Preferências dos Clientes
elif pagina == "Preferências dos Clientes":
    st.title("👥 Preferências dos Clientes")

    st.subheader("Destinos Mais Procurados")
    if 'destino' in df_clientes_filtrado.columns:
        df_destinos = df_clientes_filtrado['destino'].value_counts().reset_index()
        df_destinos.columns = ['Destino', 'Quantidade']
        df_destinos = df_destinos.dropna()
        if not df_destinos.empty:
            fig = px.pie(df_destinos, values='Quantidade', names='Destino', title="Destinos Preferidos")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ainda não há dados suficientes sobre destinos preferidos.")
    else:
        st.info("Ainda não há dados sobre destinos.")

    st.subheader("Interesses Principais")
    if 'interesse_principal' in df_clientes_filtrado.columns:
        df_interesses = df_clientes_filtrado['interesse_principal'].value_counts().reset_index()
        df_interesses.columns = ['Interesse', 'Quantidade']
        df_interesses = df_interesses.dropna()
        if not df_interesses.empty:
            fig = px.bar(df_interesses, x='Interesse', y='Quantidade', color='Interesse', title="Interesses Principais")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ainda não há dados suficientes sobre interesses principais.")
    else:
        st.info("Ainda não há dados sobre interesses.")

    st.subheader("Duração Preferida")
    if 'duracao' in df_clientes_filtrado.columns:
        df_duracao = df_clientes_filtrado['duracao'].value_counts().reset_index()
        df_duracao.columns = ['Duração', 'Quantidade']
        df_duracao = df_duracao.dropna()
        if not df_duracao.empty:
            fig = px.pie(df_duracao, values='Quantidade', names='Duração', title="Duração Preferida")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ainda não há dados suficientes sobre duração preferida.")
    else:
        st.info("Ainda não há dados sobre duração.")

    st.subheader("Períodos de Viagem")
    if 'periodo_viagem' in df_clientes_filtrado.columns:
        df_periodo = df_clientes_filtrado['periodo_viagem'].value_counts().reset_index()
        df_periodo.columns = ['Período', 'Quantidade']
        df_periodo = df_periodo.dropna()
        if not df_periodo.empty:
            fig = px.bar(df_periodo, x='Período', y='Quantidade', color='Quantidade', title="Períodos de Viagem Preferidos")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ainda não há dados suficientes sobre períodos de viagem.")
    else:
        st.info("Ainda não há dados sobre períodos de viagem.")

# Página: Atendimentos Pendentes
elif pagina == "Atendimentos Pendentes":
    st.title("🔔 Atendimentos Pendentes")

    clientes_atendimento = df_clientes_filtrado[df_clientes_filtrado['estado'] == 'atendimento_solicitado']
    if not clientes_atendimento.empty:
        st.subheader(f"Total de {len(clientes_atendimento)} clientes aguardando atendimento")

        for i, cliente in clientes_atendimento.iterrows():
            with st.expander(f"{cliente['nome']} - {cliente['telefone']}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Dados Básicos**")
                    st.write(f"Nome: {cliente['nome']}")
                    st.write(f"Telefone: {cliente['telefone']}")
                    st.write(f"Email: {cliente.get('email', 'Não informado')}")
                    st.write(f"Última interação: {cliente['ultima_interacao']}")

                with col2:
                    st.write("**Preferências**")
                    st.write(f"Destino: {cliente.get('destino', 'Não informado')}")
                    st.write(f"Interesse: {cliente.get('interesse_principal', 'Não informado')}")
                    st.write(f"Período: {cliente.get('periodo_viagem', 'Não informado')}")
                    st.write(f"Duração: {cliente.get('duracao', 'Não informado')}")
                    st.write(f"Método de contato: {cliente.get('metodo_contato', 'Não informado')}")
                    st.write(f"Horário de contato: {cliente.get('horario_contato', 'Não informado')}")

                mensagens_cliente = df_mensagens_filtrado[df_mensagens_filtrado['telefone'] == cliente['telefone']]
                if not mensagens_cliente.empty:
                    st.write("**Últimas mensagens**")
                    for _, msg in mensagens_cliente.head(5).iterrows():
                        st.markdown(f"**Cliente:** {msg['mensagem_cliente']}")
                        st.markdown(f"**Bot:** {msg['mensagem_bot']}")
                        st.markdown("---")
    else:
        st.info("Não há clientes aguardando atendimento no período selecionado.")

# Página: Detalhes dos Clientes
else:
    st.title("📋 Detalhes dos Clientes")

    filtro_estado = st.selectbox("Filtrar por Estado", ["Todos"] + list(df_clientes_filtrado['estado'].unique()))
    if filtro_estado != "Todos":
        df_filtrado = df_clientes_filtrado[df_clientes_filtrado['estado'] == filtro_estado]
    else:
        df_filtrado = df_clientes_filtrado

    busca = st.text_input("Buscar por nome ou telefone")
    if busca:
        df_filtrado = df_filtrado[
            df_filtrado['nome'].str.contains(busca, case=False, na=False) |
            df_filtrado['telefone'].str.contains(busca, case=False, na=False)
        ]

    if not df_filtrado.empty:
        colunas_base = ['nome', 'telefone', 'email', 'estado', 'ultima_interacao']
        colunas_adicionais = [col for col in df_filtrado.columns if col not in colunas_base + ['data']]

        colunas_selecionadas = colunas_base + st.multiselect(
            "Selecione dados adicionais",
            colunas_adicionais,
            default=['destino', 'interesse_principal'] if set(['destino', 'interesse_principal']).issubset(colunas_adicionais) else []
        )

        st.dataframe(df_filtrado[colunas_selecionadas], use_container_width=True)

        csv = df_filtrado[colunas_selecionadas].to_csv(index=False)
        st.download_button(
            label="📥 Exportar para CSV",
            data=csv,
            file_name=f"clientes_travessia_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Nenhum cliente encontrado com os filtros selecionados.")