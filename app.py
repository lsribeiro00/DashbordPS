import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
        font-size: 26px;
        font-weight: bold;
    }
    
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- CARREGAMENTO E TRATAMENTO DA BASE DE DADOS VIA EXCEL ---
@st.cache_data
def carregar_dados_excel(file):
    df = pd.read_excel(file)
    
    # Tratamento de datas
    if 'Dia' in df.columns:
        df['Dia'] = pd.to_datetime(df['Dia'], errors='coerce')
        
    # Garantir colunas numéricas sem nulos
    cols_numericas = ['Distância Percorrida (Km)', 'Distância Identificada (Km)']
    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df


# --- MENU LATERAL DE NAVEGAÇÃO E UPLOAD ---
st.sidebar.title("📌 Painel de Controle")

# Upload da Base em Excel
uploaded_file = st.sidebar.file_uploader(
    "📁 Upload da Base (Boletim do Veículo):",
    type=["xlsx", "xls"]
)

# Leitura do arquivo (uploaded ou padrão local)
if uploaded_file is not None:
    df_raw = carregar_dados_excel(uploaded_file)
else:
    try:
        df_raw = carregar_dados_excel("Boletim do Veículo (3).xlsx")
    except Exception:
        df_raw = pd.DataFrame()

st.sidebar.divider()

# Navegação de Módulos
modulo_selecionado = st.sidebar.radio(
    "📊 Módulo:",
    [
        "Gestão de Vigência",
        "Gestão de Saúde do Veículo",
        "Gestão de Eventos",
        "Gestão de Chamados"
    ]
)

st.sidebar.divider()

# ==========================================
# 1. MÓDULO: GESTÃO DE VIGÊNCIA
# ==========================================
if modulo_selecionado == "Gestão de Vigência":
    
    submodulo_vigencia = st.sidebar.selectbox(
        "📂 Submódulo:",
        ["Vigência Gerencial", "Detalhamento por Placa"]
    )
    
    if df_raw.empty:
        st.warning("⚠️ Nenhuma base de dados carregada. Faça o upload do arquivo Excel no menu lateral.")
        st.stop()

    if submodulo_vigencia == "Vigência Gerencial":
        st.markdown('<div class="header-bar">CONSOLIDADO VIGÊNCIA GERENCIAL</div>', unsafe_allow_html=True)

        col_esquerda, col_direita = st.columns([1, 3.8])

        with col_esquerda:
            st.subheader("🔍 Filtros")
            
            # Filtro por UO (Unidade Operacional)
            uos_disponiveis = ["Todas as UOs"] + sorted(list(df_raw["Uo"].dropna().unique()))
            uo_sel = st.selectbox("Unidade Operacional (UO)", uos_disponiveis)
            
            # Filtro por Placa
            if uo_sel != "Todas as UOs":
                df_filtered = df_raw[df_raw["Uo"] == uo_sel]
            else:
                df_filtered = df_raw.copy()

            placas_disponiveis = ["Todas as Placas"] + sorted(list(df_filtered["Placa"].dropna().unique()))
            placa_sel = st.selectbox("Placa", placas_disponiveis)
            
            if placa_sel != "Todas as Placas":
                df_filtered = df_filtered[df_filtered["Placa"] == placa_sel]

            # Cálculo dos KPIs
            total_frotas = df_filtered["Placa"].nunique()
            total_km = df_filtered["Distância Percorrida (Km)"].sum()
            km_com_vigencia = df_filtered["Distância Identificada (Km)"].sum()
            km_sem_vigencia = max(0, total_km - km_com_vigencia)
            pct_vigencia = (km_com_vigencia / total_km * 100) if total_km > 0 else 0

            st.markdown("<br>", unsafe_allow_html=True)

            # Exibição dos Cards de KPI
            st.markdown(f'''
                <div class="kpi-card">
                    <div class="kpi-title">VIGÊNCIA GERAL</div>
                    <div class="kpi-value">{pct_vigencia:.1f}%</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">TOTAL VEÍCULOS</div>
                    <div class="kpi-value">{total_frotas}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">TOTAL KM</div>
                    <div class="kpi-value">{total_km:,.1f}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">KM COM VIGÊNCIA</div>
                    <div class="kpi-value">{km_com_vigencia:,.1f}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">KM SEM VIGÊNCIA</div>
                    <div class="kpi-value">{km_sem_vigencia:,.1f}</div>
                </div>
            ''', unsafe_allow_html=True)

        with col_direita:
            st.markdown("##### META VIGÊNCIA")
            
            # Gráfico de Rosca / Velômetro de Vigência
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
                height=210,
                margin=dict(l=30, r=30, t=10, b=10),
                annotations=[dict(text="TOTAL VIGÊNCIA", x=0.5, y=0.35, showarrow=False, font=dict(size=12, color="gray"))]
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

            # Gráfico de Barras por UO
            st.markdown("##### VIGÊNCIA POR UNIDADE OPERACIONAL (UO)")
            if not df_filtered.empty and "Uo" in df_filtered.columns:
                df_uo = df_filtered.groupby("Uo").agg({
                    "Distância Percorrida (Km)": "sum",
                    "Distância Identificada (Km)": "sum"
                }).reset_index()

                df_uo["pct"] = (df_uo["Distância Identificada (Km)"] / df_uo["Distância Percorrida (Km)"]) * 100
                df_uo = df_uo.sort_values(by="pct", ascending=False).head(15)

                fig_uo = px.bar(
                    df_uo,
                    x="Uo",
                    y="pct",
                    text=df_uo["pct"].apply(lambda x: f"{x:.1f}%"),
                    color_discrete_sequence=["#1E5631"]
                )
                fig_uo.update_traces(textposition='outside')
                fig_uo.update_layout(
                    height=320,
                    margin=dict(l=20, r=20, t=25, b=60),
                    xaxis_title="",
                    yaxis_title="",
                    yaxis=dict(range=[0, 115])
                )
                st.plotly_chart(fig_uo, use_container_width=True)

    elif submodulo_vigencia == "Detalhamento por Placa":
        st.markdown('<div class="header-bar">DETALHAMENTO POR PLACA</div>', unsafe_allow_html=True)
        st.dataframe(df_raw, use_container_width=True)

# ==========================================
# OUTROS MÓDULOS (ESTRUTURA MANTIDA)
# ==========================================
elif modulo_selecionado in ["Gestão de Saúde do Veículo", "Gestão de Eventos", "Gestão de Chamados"]:
    st.markdown(f'<div class="header-bar">{modulo_selecionado.upper()}</div>', unsafe_allow_html=True)
    st.info("Módulo em desenvolvimento. Os dados serão alimentados via Excel.")
