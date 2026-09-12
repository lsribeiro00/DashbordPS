import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

st.set_page_config(page_title="Central de Disparo de Relatórios", layout="wide")

st.title("📧 Automação de Disparo de Relatórios por E-mail")

# 1. Carregar dados das Unidades/Destinatários
@st.cache_data
def carregar_base_unidades():
    # Exemplo de tabela com e-mail e métricas por unidade/gestor
    dados = {
        "unidade": ["Matriz - SP", "Filial - RJ", "Filial - MG"],
        "responsavel": ["Carlos Silva", "Ana Souza", "Roberto Lima"],
        "email": ["carlos@empresa.com", "ana@empresa.com", "roberto@empresa.com"],
        "total_ocorrencias": [12, 5, 18],
        "status_frota": ["98% Ok", "100% Ok", "91% Ok"]
    }
    return pd.DataFrame(dados)

df = carregar_base_unidades()

# Exibe a tabela no Streamlit
st.subheader("Unidades e Destinatários Cadastrados")
st.dataframe(df, use_container_width=True)

st.divider()

# 2. Configurações do Servidor de E-mail (Credenciais)
st.sidebar.header("⚙️ Configurações SMTP")
smtp_server = st.sidebar.text_input("Servidor SMTP", value="smtp.office365.com")
smtp_port = st.sidebar.number_input("Porta", value=587)
remetente_email = st.sidebar.text_input("E-mail Remetente", value="seu-email@empresa.com")
remetente_senha = st.sidebar.text_input("Senha / Token de App", type="password")

# 3. Função para Montar e Enviar E-mail em HTML
def enviar_email(destino, nome, unidade, ocorrencias, status):
    msg = MIMEMultipart()
    msg['From'] = remetente_email
    msg['To'] = destino
    msg['Subject'] = f" Relatório Operacional - {unidade}"

    # Corpo do e-mail formatado em HTML
    corpo_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif;">
        <h2>Olá, {nome}!</h2>
        <p>Segue o resumo operacional da <b>{unidade}</b> referente ao período atual:</p>
        <ul>
          <li><b>Total de Ocorrências:</b> {ocorrencias}</li>
          <li><b>Status Operacional da Frota:</b> {status}</li>
        </ul>
        <p>Por favor, verifique o painel completo no sistema caso necessite de mais detalhes.</p>
        <br>
        <p><i>Atenciosamente,<br>Equipe de Controle e Operações</i></p>
      </body>
    </html>
    """
    msg.attach(MIMEText(corpo_html, 'html'))

    # Conexão e envio
    server = smtplib.SMTP(smtp_server, int(smtp_port))
    server.starttls()
    server.login(remetente_email, remetente_senha)
    server.sendmail(remetente_email, destino, server.as_string())
    server.quit()

# 4. Botão de Disparo em Massa
st.subheader("🚀 Executar Disparos")

if st.button("Disparar E-mails para Todas as Unidades"):
    if not remetente_email or not remetente_senha:
        st.warning("Por favor, preencha as credenciais SMTP na barra lateral.")
    else:
        barra_progresso = st.progress(0)
        status_texto = st.empty()
        
        total = len(df)
        sucessos = 0
        
        for index, row in df.iterrows():
            status_texto.text(f"Enviando para {row['unidade']} ({row['email']})...")
            try:
                enviar_email(
                    destino=row['email'],
                    nome=row['responsavel'],
                    unidade=row['unidade'],
                    ocorrencias=row['total_ocorrencias'],
                    status=row['status_frota']
                )
                sucessos += 1
            except Exception as e:
                st.error(f"Erro ao enviar para {row['email']}: {e}")
            
            # Atualiza barra de progresso
            barra_progresso.progress((index + 1) / total)
        
        status_texto.text("")
        st.success(f" Processo concluído! {sucessos} de {total} e-mails enviados com sucesso.")