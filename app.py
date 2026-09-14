import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- FUNÇÃO DE CARREGAMENTO (SUBSTITUA A SUA ANTIGA POR ESSA) ---
@st.cache_data
def carregar_de_para_unidades(file_unidades=None):
    # 1. Se o usuário subiu um arquivo manual na barra lateral, usa ele
    if file_unidades is not None:
        return pd.read_excel(file_unidades)
    
    # 2. Caso contrário, lê o arquivo fixo salvo na pasta do projeto
    try:
        return pd.read_excel("unidades.xlsx")
    except Exception as e:
        st.error("Arquivo 'unidades.xlsx' não encontrado no diretório do projeto.")
        return pd.DataFrame()

# --- CARREGA O MAPEAMENTO DE UNIDADES AUTOMATICAMENTE ---
df_unidades_map = carregar_de_para_unidades()

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

# --- FUNÇÕES DE CARREGAMENTO E PROCESSAMENTO VIA EXCEL ---
@st.cache_data
def carregar_de_para_unidades(file_unidades):
    """Carrega o de-para de Unidades e Clientes."""
    if file_unidades is not None:
        return pd.read_excel(file_unidades)
    try:
        return pd.read_excel("unidades.xlsx")
    except Exception:
        return pd.DataFrame(columns=["Uo", "UNIDADE", "CLIENTE"])

@st.cache_data
def carregar_boletim_veiculo(file_boletim, df_unidades):
    """Carrega o Boletim do Veículo e realiza o merge com a estrutura de Clientes/Unidades."""
    if file_boletim is not None:
        df = pd.read_excel(file_boletim)
    else:
        try:
            df = pd.read_excel("Boletim do Veículo (3).xlsx")
        except Exception:
            return pd.DataFrame()
    
    # Tratamento de datas e tipos numéricos
    if 'Dia' in df.columns:
        df['Dia'] = pd.to_datetime(df['Dia'], errors='coerce')
        
    cols_numericas = ['Distância Percorrida (Km)', 'Distância Identificada (Km)']
    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Merge com o De-Para de Clientes/Unidades
    if not df_unidades.empty and 'Uo' in df.columns and 'Uo' in df_unidades.columns:
        df = df.merge(df_unidades[['Uo', 'UNIDADE', 'CLIENTE']], on='Uo', how='left')
        df['CLIENTE'] = df['CLIENTE'].fillna("Outros / Não Mapeados")
        df['UNIDADE'] = df['UNIDADE'].fillna(df['Uo'])
    else:
        df['CLIENTE'] = "Todos os Clientes"
        df['UNIDADE'] = df['Uo'] if 'Uo' in df.columns else "Geral"

    return df


# --- MENU LATERAL DE NAVEGAÇÃO E UPLOADS ---
st.sidebar.title("📌 Painel de Controle")

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

# 2. Uploads de Planilhas Excel
st.sidebar.subheader("📁 Upload de Arquivos")
uploaded_boletim = st.sidebar.file_uploader(
    "1. Boletim do Veículo (.xlsx)",
    type=["xlsx", "xls"]
)

st.sidebar.divider()

# 3. Módulos
modulo_selecionado = st.sidebar.radio(
    "📊 Módulo:",
    [
        "Gestão de Vigência",
        "Gestão de Saúde do Veículo",
        "Gestão de Eventos",
        "Gestão de Chamados"
    ]
)

# --- CARREGAMENTO INICIAL DAS PLANILHAS ---
df_raw = carregar_boletim_veiculo(uploaded_boletim, df_unidades_map)


# ==========================================
# 1. MÓDULO: GESTÃO DE VIGÊNCIA
# ==========================================
if modulo_selecionado == "Gestão de Vigência":
    
    submodulo_vigencia = st.sidebar.selectbox(
        "📂 Submódulo:",
        ["Vigência Gerencial", "Detalhamento por Veículo"]
    )
    
    if df_raw.empty:
        st.warning("⚠️ Nenhuma base de dados encontrada. Por favor, faça o upload dos arquivos Excel no menu lateral.")
        st.stop()

    if submodulo_vigencia == "Vigência Gerencial":
        st.markdown('<div class="header-bar">CONSOLIDADO VIGÊNCIA GERENCIAL</div>', unsafe_allow_html=True)

        # Filtro de Cliente aplicado no DataFrame
        if cliente_selecionado != "Todos os Clientes":
            df_filtered = df_raw[df_raw["CLIENTE"] == cliente_selecionado]
        else:
            df_filtered = df_raw.copy()

        col_esquerda, col_direita = st.columns([1, 3.8])

        with col_esquerda:
            st.subheader("🔍 Filtros Operacionais")
            
            # Filtro Dinâmico por Unidade
            unidades_opt = ["Todas as Unidades"] + sorted(list(df_filtered["UNIDADE"].dropna().unique()))
            unidade_sel = st.selectbox("Unidade Operacional", unidades_opt)
            
            if unidade_sel != "Todas as Unidades":
                df_filtered = df_filtered[df_filtered["UNIDADE"] == unidade_sel]

            # Filtro Dinâmico por Placa
            placas_opt = ["Todas as Placas"] + sorted(list(df_filtered["Placa"].dropna().unique()))
            placa_sel = st.selectbox("Placa do Veículo", placas_opt)
            
            if placa_sel != "Todas as Placas":
                df_filtered = df_filtered[df_filtered["Placa"] == placa_sel]

            # Métricas e KPIs
            total_frotas = df_filtered["Placa"].nunique()
            total_km = df_filtered["Distância Percorrida (Km)"].sum()
            km_com_vigencia = df_filtered["Distância Identificada (Km)"].sum()
            km_sem_vigencia = max(0.0, total_km - km_com_vigencia)
            pct_vigencia = (km_com_vigencia / total_km * 100) if total_km > 0 else 0.0

            st.markdown("<br>", unsafe_allow_html=True)

            # Cards visuais
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

           # Visão de Unidades (Escala de Cores + Ajuste de Filtro de Unidade)
            st.markdown("##### VIGÊNCIA POR UNIDADE")
            if not df_filtered.empty and "UNIDADE" in df_filtered.columns:
                
                # 1. Agrupa dados do boletim (já filtrado pela página/sidebar)
                df_unid_chart = df_filtered.groupby("UNIDADE").agg({
                    "Distância Percorrida (Km)": "sum",
                    "Distância Identificada (Km)": "sum"
                }).reset_index()

                # 2. Verifica se uma unidade específica foi selecionada no filtro
                # Substitua 'unidade_selecionada' pela sua variável de filtro de unidade da sidebar
                unidade_filtrada = (unidade_selecionada != "Todas as Unidades") if 'unidade_selecionada' in locals() else False

                # 3. Se NÃO houver unidade específica selecionada (visão geral), faz o merge para trazer todas zeradas
                if not unidade_filtrada:
                    if cliente_selecionado != "Todos os Clientes":
                        unidades_do_cliente = df_unidades_map[df_unidades_map["CLIENTE"] == cliente_selecionado][["UNIDADE"]].drop_duplicates()
                    else:
                        unidades_do_cliente = df_unidades_map[["UNIDADE"]].drop_duplicates()
                    
                    df_unid_chart = unidades_do_cliente.merge(df_unid_chart, on="UNIDADE", how="left").fillna(0)

                # 4. Calcula o percentual de vigência
                df_unid_chart["pct"] = df_unid_chart.apply(
                    lambda row: (row["Distância Identificada (Km)"] / row["Distância Percorrida (Km)"] * 100)
                    if row["Distância Percorrida (Km)"] > 0 else 0.0,
                    axis=1
                )

                # Ordena para exibir as maiores vigências no topo do gráfico horizontal
                df_unid_chart = df_unid_chart.sort_values(by="pct", ascending=True)

                # 5. Atribuição da escala de cores (Verde, Amarelo, Vermelho)
                def classificar_cor(pct):
                    if pct >= 90.0:
                        return "#2E7D32"  # Verde
                    elif pct >= 85.0:
                        return "#FBC02D"  # Amarelo
                    else:
                        return "#D32F2F"  # Vermelho

                df_unid_chart["cor"] = df_unid_chart["pct"].apply(classificar_cor)

                # 6. Renderização do Gráfico Plotly
                fig_unid = px.bar(
                    df_unid_chart,
                    x="pct",
                    y="UNIDADE",
                    orientation='h',
                    text=df_unid_chart["pct"].apply(lambda x: f"{x:.1f}%")
                )

                fig_unid.update_traces(
                    marker_color=df_unid_chart["cor"],
                    textposition='outside'
                )

                # Ajusta a altura dinamicamente (se for 1 unidade só, a altura fica compacta)
                altura_grafico = max(200, len(df_unid_chart) * 35)

                fig_unid.update_layout(
                    height=altura_grafico,
                    margin=dict(l=20, r=40, t=25, b=20),
                    xaxis_title="",
                    yaxis_title="",
                    xaxis=dict(range=[0, 115])
                )

                st.plotly_chart(fig_unid, use_container_width=True)
            else:
                st.warning("Nenhum registro encontrado para os filtros selecionados.")

                # Ajusta a altura dinamicamente (se for 1 unidade só, a altura fica compacta)
                altura_grafico = max(200, len(df_unid_chart) * 35)

                fig_unid.update_layout(
                    height=altura_grafico,
                    margin=dict(l=20, r=40, t=25, b=20),
                    xaxis_title="",
                    yaxis_title="",
                    xaxis=dict(range=[0, 115])
                )

                st.plotly_chart(fig_unid, use_container_width=True)
            else:
                st.warning("Nenhum registro encontrado para os filtros selecionados.")
# ==========================================
# OUTROS MÓDULOS
# ==========================================
elif modulo_selecionado in ["Gestão de Saúde do Veículo", "Gestão de Eventos", "Gestão de Chamados"]:
    st.markdown(f'<div class="header-bar">{modulo_selecionado.upper()}</div>', unsafe_allow_html=True)
    st.info(f"Painel em construção para o cliente selecionado: **{cliente_selecionado}**")
