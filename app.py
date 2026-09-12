import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configuração da página
st.set_page_config(
    page_title="Sistema de Gestão Operacional",
    page_icon="🚛",
    layout="wide"
)

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

# --- PÁGINA 1: GESTÃO DE VIGÊNCIA ---
if pagina_selecionada == "Gestão de Vigência":
    st.title("📋 Gestão de Vigência")
    st.markdown("Acompanhamento de contratos, renovações e prazos de validade da frota/equipamentos.")
    
    # Exemplo de KPIs/Métricas
    col1, col2, col3 = st.columns(3)
    col1.metric("Contratos Ativos", "142")
    col2.metric("Vencendo em 30 dias", "8", delta="-2 neste mês", delta_color="inverse")
    col3.metric("Contratos Vencidos", "1", delta="Atenção", delta_color="normal")
    
    st.divider()
    st.subheader("Lista de Vigências")
    # Tabela demonstrativa
    df_vigencia = pd.DataFrame({
        "Contrato/Veículo": ["ABC-1234 (Caminhão 01)", "DEF-5678 (Caminhão 02)", "GHI-9012 (Caminhão 03)"],
        "Tipo": ["Telemetria", "Videotelemetria", "Seguro"],
        "Vencimento": ["2026-10-15", "2026-09-30", "2026-11-20"],
        "Status": ["Em dia", "Atenção (Próximo)", "Em dia"]
    })
    st.dataframe(df_vigencia, use_container_width=True)

# --- PÁGINA 2: GESTÃO DE SAÚDE DO VEÍCULO ---
elif pagina_selecionada == "Gestão de Saúde do Veículo":
    st.title("🚛 Gestão de Saúde do Veículo")
    st.markdown("Status de telemetria, sinal de rastreador, câmeras e diagnósticos de hardware.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Frota Monitorada", "250")
    col2.metric("Equipamentos Online", "242 (96.8%)")
    col3.metric("Sem Sinal (> 24h)", "8", delta="Manutenção necessária", delta_color="inverse")
    
    st.divider()
    st.subheader("Diagnóstico por Veículo")
    df_saude = pd.DataFrame({
        "Placa": ["ABC-1234", "DEF-5678", "XYZ-9999"],
        "Rastreador": ["Online", "Online", "Offline"],
        "Câmeras": ["OK", "Falha Sensor", "Offline"],
        "Última Transmissão": ["Há 2 min", "Há 5 min", "Há 2 dias"]
    })
    st.dataframe(df_saude, use_container_width=True)

# --- PÁGINA 3: GESTÃO DE EVENTOS ---
elif pagina_selecionada == "Gestão de Eventos":
    st.title("⚠️ Gestão de Eventos de Telemetria / Videotelemetria")
    st.markdown("Monitoramento de excesso de velocidade, frenagens bruscas, fadiga e distrações.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Eventos Hoje", "45")
    col2.metric("Eventos de Alto Risco", "6", delta="+2 vs ontem", delta_color="inverse")
    col3.metric("Tempo Médio Tratação", "14 min")
    
    st.divider()
    st.subheader("Últimos Eventos Registrados")
    df_eventos = pd.DataFrame({
        "Data/Hora": ["2026-09-12 10:15", "2026-09-12 11:30", "2026-09-12 13:05"],
        "Placa": ["ABC-1234", "GHI-9012", "DEF-5678"],
        "Tipo de Evento": ["Uso de Celular (Videotelemetria)", "Frenagem Brusca", "Excesso de Velocidade"],
        "Gravidade": ["Alta", "Média", "Alta"],
        "Status Tratamento": ["Tratado", "Pendente", "Pendente"]
    })
    st.dataframe(df_eventos, use_container_width=True)

# --- PÁGINA 4: GESTÃO DE CHAMADOS ---
elif pagina_selecionada == "Gestão de Chamados":
    st.title("🎫 Gestão de Chamados")
    st.markdown("Controle de chamados técnicos para manutenção de câmeras, sensores e telemetria.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Chamados Abertos", "12")
    col2.metric("Em Atendimento", "7")
    col3.metric("Concluídos no Mês", "48")
    
    st.divider()
    st.subheader("Chamados em Aberto")
    df_chamados = pd.DataFrame({
        "ID Chamado": ["#1092", "#1093", "#1094"],
        "Veículo/Unidade": ["ABC-1234 - Matriz", "DEF-5678 - Filial RJ", "XYZ-9999 - Filial MG"],
        "Problema Relatado": ["Câmera de fadiga sem imagem", "No-break desligando", "Perda de sinal GPS"],
        "Abertura": ["2026-09-10", "2026-09-11", "2026-09-12"],
        "Prioridade": ["Alta", "Média", "Alta"]
    })
    st.dataframe(df_chamados, use_container_width=True)

# --- PÁGINA 5: CONFIGURAÇÕES E DISPARO DE E-MAILS ---
elif pagina_selecionada == "Configurações":
    st.title("⚙️ Configurações do Sistema & Disparos Automáticos")
    st.markdown("Parâmetros de envio de relatórios e credenciais SMTP.")
    
    st.subheader("📧 Configurações de E-mail (SMTP)")
    
    col_smtp1, col_smtp2 = st.columns(2)
    with col_smtp1:
        smtp_server = st.text_input("Servidor SMTP", value="smtp.office365.com")
        remetente_email = st.text_input("E-mail Remetente", value="seu-email@empresa.com")
    with col_smtp2:
        smtp_port = st.number_input("Porta", value=587)
        remetente_senha = st.text_input("Senha / Token de App", type="password")
        
    st.divider()
    st.subheader("🚀 Automação de Disparo de Relatórios por Unidade")
    
    # Base de unidades para envio
    df_destinatarios = pd.DataFrame({
        "unidade": ["Matriz - SP", "Filial - RJ", "Filial - MG"],
        "responsavel": ["Gestor SP", "Gestor RJ", "Gestor MG"],
        "email": ["gestor.sp@empresa.com", "gestor.rj@empresa.com", "gestor.mg@empresa.com"],
        "eventos_pendentes": [2, 0, 5]
    })
    
    st.dataframe(df_destinatarios, use_container_width=True)

    if st.button("Disparar Relatórios por E-mail Agora"):
        if not remetente_email or not remetente_senha:
            st.warning("Por favor, preencha o e-mail e a senha SMTP para realizar o teste.")
        else:
            st.success("Simulação de disparo iniciada! (Integração pronta para envio real)")
