import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="Consolidado Vigência",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS para recriar os cards arredondados e o cabeçalho verde
st.markdown("""
    <style>
    /* Estilo do cabeçalho superior verde */
    .header-bar {
        background-color: #1E5631;
        color: white;
        text-align: center;
        padding: 12px;
        border-radius: 8px;
        font-size: 26px;
        font-weight: bold;
        letter-spacing: 1px;
        margin-bottom: 25px;
    }
    
    /* Estilo dos cards de KPI arredondados na coluna esquerda */
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
    
    /* Ajustes gerais de espaçamento */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- MENU LATERAL DE NAVEGAÇÃO ---
st.sidebar.title("📌 Menu Principal")
menu_opcoes = [
    "Gestão de Vigência",
    "Gestão de Saúde do Veículo",
    "Gestão de Eventos",
    "Gestão de Chamados",
    "Configurações"
]

pagina_selecionada = st.sidebar.radio("Selecione o módulo:", menu_opcoes)
st.sidebar.divider()


# ==========================================
# MÓDULO: GESTÃO DE VIGÊNCIA
# ==========================================
if pagina_selecionada == "Gestão de Vigência":

    # 1. Cabeçalho Verde no topo
    st.markdown('<div class="header-bar">CONSOLIDADO VIGÊNCIA</div>', unsafe_allow_html=True)

    # 2. Dados Fictícios de Exemplo (Pronto para conectar ao seu banco/Excel)
    dados_mock = [
        {"unidade": "JALLES MATRIZ - TERCEIRO", "grupo": "CAMINHÃO TRANSP. BAU UJM", "prefixo": "PF-01", "km_total": 45.0, "km_vigente": 40.2},
        {"unidade": "JALLES OTAVIO LAGE - TERCEIRO", "grupo": "CAMINHÃO TRANSP. CANAVIEIRO UJM", "prefixo": "PF-02", "km_total": 35.0, "km_vigente": 29.5},
        {"unidade": "JALLES OTAVIO LAGE - PRÓPRIO", "grupo": "CAMINHÃO TRANSP. CANAVIEIRO UOL", "prefixo": "PF-03", "km_total": 31.0, "km_vigente": 26.0},
        {"unidade": "JALLES OTAVIO LAGE - PRÓPRIO", "grupo": "CAMINHÃO COMBOIO UOL", "prefixo": "PF-04", "km_total": 25.0, "km_vigente": 20.96},
        {"unidade": "JALLES SANTA VITORIA - PRÓPRIO", "grupo": "CAMINHÃO TRANSP. VINHAÇA UOL", "prefixo": "PF-05", "km_total": 22.0, "km_vigente": 14.93},
        {"unidade": "JALLES MATRIZ - PRÓPRIO", "grupo": "CAMINHÃO PRANCHA UOL", "prefixo": "PF-06", "km_total": 18.0, "km_vigente": 11.87},
        {"unidade": "JALLES MATRIZ - FROTA LEVE", "grupo": "CAMINHÃO TRANSP. VINHAÇA UJM", "prefixo": "PF-07", "km_total": 11.2, "km_vigente": 3.28},
    ]
    df_vig = pd.DataFrame(dados_mock)

    # Layout de 2 colunas principais: Coluna Esquerda (Filtros + KPIs) | Coluna Direita (Gráficos)
    col_esquerda, col_direita = st.columns([1, 3.8])

    # ------------------------------------------
    # COLUNA ESQUERDA: Filtros + Cards Arredondados
    # ------------------------------------------
    with col_esquerda:
        # Filtros
        unidade_sel = st.selectbox("Unidade", ["Todas"] + list(df_vig["unidade"].unique()))
        grupo_sel = st.selectbox("Grupo", ["Todos"] + list(df_vig["grupo"].unique()))
        prefixo_sel = st.selectbox("Prefixo", ["Todos"] + list(df_vig["prefixo"].unique()))

        # Filtragem dinâmica
        df_filtered = df_vig.copy()
        if unidade_sel != "Todas":
            df_filtered = df_filtered[df_filtered["unidade"] == unidade_sel]
        if grupo_sel != "Todos":
            df_filtered = df_filtered[df_filtered["grupo"] == grupo_sel]
        if prefixo_sel != "Todos":
            df_filtered = df_filtered[df_filtered["prefixo"] == prefixo_sel]

        # Cálculos das Métricas
        total_frotas = len(df_filtered)
        total_km = df_filtered["km_total"].sum()
        km_com_vigencia = df_filtered["km_vigente"].sum()
        km_sem_vigencia = total_km - km_com_vigencia
        pct_vigencia = (km_com_vigencia / total_km * 100) if total_km > 0 else 0

        st.markdown("<br>", unsafe_allow_html=True)

        # Cards com HTML/CSS personalizado
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

    # ------------------------------------------
    # COLUNA DIREITA: Os 3 Gráficos (Gauge, Barras Unidade, Barras Grupo)
    # ------------------------------------------
    with col_direita:
        
        # --- 1. GRÁFICO META VIGÊNCIA (GAUGE / SEMICÍRCULO) ---
        st.markdown("##### META VIGÊNCIA")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pct_vigencia,
            number={'suffix': "%", 'font': {'size': 32, 'color': '#2D2D2D', 'family': 'Arial'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#888888", 'tickvals': [0, 100], 'ticktext': ['0%', '100%']},
                'bar': {'color': "#1E5631", 'thickness': 0.6},
                'bgcolor': "#E0E0E0",
                'bordercolor': "white",
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

        # --- 2. GRÁFICO VIGÊNCIA UNIDADE (BARRAS VERTICAIS VERDES) ---
        st.markdown("##### VIGÊNCIA UNIDADE")
        df_unidade = df_filtered.groupby("unidade").agg({
            "km_total": "sum",
            "km_vigente": "sum"
        }).reset_index()
        df_unidade["pct"] = (df_unidade["km_vigente"] / df_unidade["km_total"]) * 100
        df_unidade = df_unidade.sort_values(by="pct", ascending=False)

        fig_unidade = px.bar(
            df_unidade,
            x="unidade",
            y="pct",
            text=df_unidade["pct"].apply(lambda x: f"{x:.2f}%".replace('.', ',')),
            color_discrete_sequence=["#1E5631"]
        )
        fig_unidade.update_traces(textposition='outside', textfont=dict(weight='bold', color='white'))
        fig_unidade.update_layout(
            height=260,
            margin=dict(l=20, r=20, t=25, b=40),
            xaxis_title="",
            yaxis_title="",
            yaxis=dict(showticklabels=False, range=[0, 115]),
            xaxis=dict(tickangle=0, font=dict(size=10))
        )
        st.plotly_chart(fig_unidade, use_container_width=True)

        # --- 3. GRÁFICO VIGÊNCIA POR GRUPO (BARRAS HORIZONTAIS) ---
        st.markdown("##### VIGÊNCIA POR GRUPO")
        df_grupo = df_filtered.groupby("grupo").agg({
            "km_total": "sum",
            "km_vigente": "sum"
        }).reset_index()
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
        fig_grupo.update_traces(textposition='inside', textfont=dict(color='white', size=10))
        fig_grupo.update_layout(
            height=320,
            margin=dict(l=20, r=20, t=10, b=20),
            xaxis_title="",
            yaxis_title="",
            xaxis=dict(range=[0, 105], ticksuffix="%")
        )
        st.plotly_chart(fig_grupo, use_container_width=True)

# --- OUTROS MÓDULOS (Mantidos para navegação) ---
elif pagina_selecionada == "Gestão de Saúde do Veículo":
    st.title("🚛 Gestão de Saúde do Veículo")
    st.info("Módulo em desenvolvimento...")

elif pagina_selecionada == "Gestão de Eventos":
    st.title("⚠️ Gestão de Eventos")
    st.info("Módulo em desenvolvimento...")

elif pagina_selecionada == "Gestão de Chamados":
    st.title("🎫 Gestão de Chamados")
    st.info("Módulo em desenvolvimento...")

elif pagina_selecionada == "Configurações":
    st.title("⚙️ Configurações & Disparos de E-mail")
    st.info("Módulo em desenvolvimento...")
