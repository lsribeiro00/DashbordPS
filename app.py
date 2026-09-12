import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client

# Inicializa a conexão com Supabase
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["supabase"]["SUPABASE_URL"]
    key = st.secrets["supabase"]["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# Função para carregar os dados
@st.cache_data(ttl=600) # Cache de 10 minutos
def carregar_dados_vigencia(cliente_selecionado):
    query = supabase.table("vigencia_gerencial").select("*")
    
    if cliente_selecionado != "Todos os Clientes":
        query = query.eq("uo_cliente", cliente_selecionado)
        
    response = query.execute()
    return pd.DataFrame(response.data)


# Configuração da página
st.set_page_config(
    page_title="Sistema de Gestão Operacional",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada
st.markdown("""
    <style>
    .header-bar {
        background-color: #1E5631;
        color: white;
        text-align: center;
        padding: 12px;
        border-radius: 8px;
        font-size: 24px;
        font-weight: bold;
        letter-spacing: 1px;
        margin-bottom: 25px;
    }
    
    .kpi-card {
        background-color: #FFFFFF;
        border: 2px solid #E0E0E0;
        border-radius: 20px;
        padding: 12px 10px;
        text-align: center;
        margin-bottom: 12px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.03);
    }
    .kpi-title {
        color: #4F4F4F;
        font-size: 13px;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .kpi-value {
        color: #2D2D2D;
        font-size: 28px;
        font-weight: bold;
    }
    
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- MENU LATERAL DE NAVEGAÇÃO E FILTROS GLOBAIS ---
st.sidebar.title("📌 Menu Principal")

# 1. Filtro Global de Cliente (UO)
lista_clientes = [
    "Todos os Clientes",
    "UO: 10960 - GRUPO COLOMBO AGROINDÚSTRIA",
    "UO: 14384 - JALLES MACHADO - S A",
    "UO: 10371 - GRUPO SUPERGASBRAS - FROTA PROPRIA",
    "UO: 8810 - PEPSICO BRASIL"
]
cliente_selecionado = st.sidebar.selectbox("🏢 Selecione o Cliente (UO):", lista_clientes)

st.sidebar.divider()

# 2. Seleção do Módulo Principal
modulo_selecionado = st.sidebar.radio(
    "📊 Módulo:",
    [
        "Gestão de Vigência",
        "Gestão de Saúde do Veículo",
        "Gestão de Eventos",
        "Gestão de Chamados",
        "Configurações"
    ]
)

st.sidebar.divider()


# ==========================================
# 1. MÓDULO: GESTÃO DE VIGÊNCIA
# ==========================================
if modulo_selecionado == "Gestão de Vigência":
    
    submodulo_vigencia = st.sidebar.selectbox(
        "📂 Submódulo:",
        ["Vigência Gerencial", "Vigência Unidades"]
    )
    
    # --- SUBMÓDULO: VIGÊNCIA GERENCIAL ---
    if submodulo_vigencia == "Vigência Gerencial":
        st.markdown(f'<div class="header-bar">CONSOLIDADO VIGÊNCIA GERENCIAL</div>', unsafe_allow_html=True)

        # Dados Mock
        dados_mock = [
            {"cliente": "UO: 14384 - JALLES MACHADO - S A", "unidade": "JALLES MATRIZ - TERCEIRO", "grupo": "CAMINHÃO TRANSP. BAU UJM", "prefixo": "PF-01", "km_total": 45.0, "km_vigente": 40.2},
            {"cliente": "UO: 14384 - JALLES MACHADO - S A", "unidade": "JALLES OTAVIO LAGE - TERCEIRO", "grupo": "CAMINHÃO TRANSP. CANAVIEIRO UJM", "prefixo": "PF-02", "km_total": 35.0, "km_vigente": 29.5},
            {"cliente": "UO: 10960 - GRUPO COLOMBO AGROINDÚSTRIA", "unidade": "COLOMBO MATRIZ", "grupo": "CAMINHÃO COMBOIO UOL", "prefixo": "PF-03", "km_total": 50.0, "km_vigente": 45.0},
            {"cliente": "UO: 10371 - GRUPO SUPERGASBRAS - FROTA PROPRIA", "unidade": "SUPERGASBRAS RJ", "grupo": "VEÍCULO LEVE UJM", "prefixo": "PF-04", "km_total": 20.0, "km_vigente": 18.0},
            {"cliente": "UO: 8810 - PEPSICO BRASIL", "unidade": "PEPSICO SP", "grupo": "CAMINHÃO PRANCHA UOL", "prefixo": "PF-05", "km_total": 30.0, "km_vigente": 22.0},
        ]
        df_vig = pd.DataFrame(dados_mock)

        # Aplicar filtro de cliente se selecionado
        if cliente_selecionado != "Todos os Clientes":
            df_vig = df_vig[df_vig["cliente"] == cliente_selecionado]

        col_esquerda, col_direita = st.columns([1, 3.8])

        # COLUNA ESQUERDA: Filtros + Cards
        with col_esquerda:
            unidades_opt = ["Todas"] + list(df_vig["unidade"].unique()) if not df_vig.empty else ["Todas"]
            grupos_opt = ["Todos"] + list(df_vig["grupo"].unique()) if not df_vig.empty else ["Todos"]
            prefixos_opt = ["Todos"] + list(df_vig["prefixo"].unique()) if not df_vig.empty else ["Todos"]

            unidade_sel = st.selectbox("Unidade", unidades_opt)
            grupo_sel = st.selectbox("Grupo", grupos_opt)
            prefixo_sel = st.selectbox("Prefixo", prefixos_opt)

            df_filtered = df_vig.copy()
            if unidade_sel != "Todas":
                df_filtered = df_filtered[df_filtered["unidade"] == unidade_sel]
            if grupo_sel != "Todos":
                df_filtered = df_filtered[df_filtered["grupo"] == grupo_sel]
            if prefixo_sel != "Todos":
                df_filtered = df_filtered[df_filtered["prefixo"] == prefixo_sel]

            total_frotas = len(df_filtered)
            total_km = df_filtered["km_total"].sum() if not df_filtered.empty else 0
            km_com_vigencia = df_filtered["km_vigente"].sum() if not df_filtered.empty else 0
            km_sem_vigencia = total_km - km_com_vigencia
            pct_vigencia = (km_com_vigencia / total_km * 100) if total_km > 0 else 0

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown(f'''
                <div class="kpi-card">
                    <div class="kpi-title">VIGÊNCIA</div>
                    <div class="kpi-value">{pct_vigencia:.1f}%</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">TOTAL FROTAS</div>
                    <div class="kpi-value">{total_frotas}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">TOTAL KM</div>
                    <div class="kpi-value">{total_km:.1f} mil</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">KM COM VIGÊNCIA</div>
                    <div class="kpi-value">{km_com_vigencia:.1f} mil</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">KM SEM VIGÊNCIA</div>
                    <div class="kpi-value">{km_sem_vigencia:.1f} mil</div>
                </div>
            ''', unsafe_allow_html=True)

        # COLUNA DIREITA: Gráficos
        with col_direita:
            # 1. Gauge Chart
            st.markdown("##### META VIGÊNCIA")
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=pct_vigencia,
                number={'suffix': "%"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#1E5631"},
                    'bgcolor': "#E0E0E0",
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': pct_vigencia
                    }
                }
            ))
            fig_gauge.update_layout(
                height=200,
                margin=dict(l=30, r=30, t=10, b=10),
                annotations=[dict(text="TOTAL VIGENCIA", x=0.5, y=0.35, showarrow=False, font=dict(size=12, color="gray"))]
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

            # 2. Barras Verticais (Unidade)
            st.markdown("##### VIGÊNCIA UNIDADE")
            if not df_filtered.empty:
                df_unidade = df_filtered.groupby("unidade").agg({"km_total": "sum", "km_vigente": "sum"}).reset_index()
                df_unidade["pct"] = (df_unidade["km_vigente"] / df_unidade["km_total"]) * 100
                df_unidade = df_unidade.sort_values(by="pct", ascending=False)

                fig_unidade = px.bar(
                    df_unidade,
                    x="unidade",
                    y="pct",
                    text=df_unidade["pct"].apply(lambda x: f"{x:.2f}%".replace('.', ',')),
                    color_discrete_sequence=["#1E5631"]
                )
                fig_unidade.update_traces(textposition='outside')
                fig_unidade.update_layout(height=260, margin=dict(l=20, r=20, t=25, b=40), xaxis_title="", yaxis_title="", yaxis=dict(range=[0, 115]))
                st.plotly_chart(fig_unidade, use_container_width=True)
            else:
                st.warning("Nenhum dado encontrado para os filtros selecionados.")

            # 3. Barras Horizontais (Grupo)
            st.markdown("##### VIGÊNCIA POR GRUPO")
            if not df_filtered.empty:
                df_grupo = df_filtered.groupby("grupo").agg({"km_total": "sum", "km_vigente": "sum"}).reset_index()
                df_grupo["pct"] = (df_grupo["km_vigente"] / df_grupo["km_total"]) * 100
                df_grupo = df_grupo.sort_values(by="pct", ascending=True)

                fig_grupo = px.bar(
                    df_grupo,
                    x="pct",
                    y="grupo",
                    orientation='h',
                    text=df_grupo["pct"].apply(lambda x: f"{x:.2f}%".replace('.', ',')),
                    color_discrete_sequence=["#1E5631"]
                )
                fig_grupo.update_traces(textposition='inside')
                fig_grupo.update_layout(height=320, margin=dict(l=20, r=20, t=10, b=20), xaxis_title="", yaxis_title="", xaxis=dict(range=[0, 105], ticksuffix="%"))
                st.plotly_chart(fig_grupo, use_container_width=True)

    # --- SUBMÓDULO: VIGÊNCIA UNIDADES ---
    elif submodulo_vigencia == "Vigência Unidades":
        st.markdown('<div class="header-bar">VIGÊNCIA POR UNIDADES</div>', unsafe_allow_html=True)
        st.info(f"Visão detalhada de unidades para: **{cliente_selecionado}**")


# ==========================================
# 2. MÓDULO: GESTÃO DE SAÚDE DO VEÍCULO
# ==========================================
elif modulo_selecionado == "Gestão de Saúde do Veículo":
    
    submodulo_saude = st.sidebar.selectbox(
        "📂 Submódulo:",
        ["Saúde Gerencial", "Saúde Unidades"]
    )
    
    if submodulo_saude == "Saúde Gerencial":
        st.markdown('<div class="header-bar">SAÚDE GERENCIAL DA FROTA</div>', unsafe_allow_html=True)
        st.info(f"Painel Gerencial de Saúde para: **{cliente_selecionado}**")
        
    elif submodulo_saude == "Saúde Unidades":
        st.markdown('<div class="header-bar">SAÚDE POR UNIDADES</div>', unsafe_allow_html=True)
        st.info(f"Detalhamento por Unidade de Saúde do Veículo para: **{cliente_selecionado}**")


# ==========================================
# 3. MÓDULO: GESTÃO DE EVENTOS
# ==========================================
elif modulo_selecionado == "Gestão de Eventos":
    
    submodulo_eventos = st.sidebar.selectbox(
        "📂 Submódulo:",
        ["Eventos Gerencial", "Eventos Unidades"]
    )
    
    if submodulo_eventos == "Eventos Gerencial":
        st.markdown('<div class="header-bar">EVENTOS GERENCIAL (TELEMETRIA / VIDEOTELEMETRIA)</div>', unsafe_allow_html=True)
        st.info(f"Consolidado Gerencial de Eventos para: **{cliente_selecionado}**")
        
    elif submodulo_eventos == "Eventos Unidades":
        st.markdown('<div class="header-bar">EVENTOS POR UNIDADES</div>', unsafe_allow_html=True)
        st.info(f"Visão de Eventos por Unidade para: **{cliente_selecionado}**")


# ==========================================
# 4. MÓDULO: GESTÃO DE CHAMADOS
# ==========================================
elif modulo_selecionado == "Gestão de Chamados":
    
    submodulo_chamados = st.sidebar.selectbox(
        "📂 Submódulo:",
        ["Chamados Gerencial", "Chamados Unidade"]
    )
    
    if submodulo_chamados == "Chamados Gerencial":
        st.markdown('<div class="header-bar">GESTÃO DE CHAMADOS GERENCIAL</div>', unsafe_allow_html=True)
        st.info(f"Painel Gerencial de Chamados para: **{cliente_selecionado}**")
        
    elif submodulo_chamados == "Chamados Unidade":
        st.markdown('<div class="header-bar">CHAMADOS POR UNIDADE</div>', unsafe_allow_html=True)
        st.info(f"Chamados detalhados por Unidade para: **{cliente_selecionado}**")


# ==========================================
# 5. MÓDULO: CONFIGURAÇÕES
# ==========================================
elif modulo_selecionado == "Configurações":
    st.markdown('<div class="header-bar">CONFIGURAÇÕES & DISPAROS AUTOMÁTICOS</div>', unsafe_allow_html=True)
    st.info("Módulo para gerenciamento de parâmetros, e-mails e credenciais.")
