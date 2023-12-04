import streamlit as st
from deta import Deta
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pytz
from datetime import datetime

# Configuração
DETA_PROJECT_KEY = st.secrets["sua_project_key"]
whatsapp_token = st.secrets["seu_token_whatsapp"]
deta = Deta(DETA_PROJECT_KEY)
db = deta.Base("tasks")
fuso_horario_desejado = pytz.timezone("America/Sao_Paulo")

# Função para enviar mensagens para o WhatsApp
def send_link(recipient, token, message):
    url = f'https://server.api-wa.me/message/text?key={token}'
    headers = {
        'accept': '*/*',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    payload = {
        "messageData": {
            "to": recipient,
            "text": message
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response.text)
    if response.status_code == 200:
        return response.text
    else:
        return {"error": f"Request failed with status code {response.status_code}"}

# Função para enviar e-mails
def enviar_email(outlook_email, senha, destinatario, assunto, corpo):
    try:
        msg = MIMEMultipart()
        msg['From'] = outlook_email
        msg['To'] = destinatario
        msg['Subject'] = assunto
        msg.attach(MIMEText(corpo, 'plain'))
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(outlook_email, senha)
        server.sendmail(outlook_email, destinatario, msg.as_string())
        server.quit()
        return "E-mail enviado com sucesso!"
    except Exception as e:
        return f"Erro ao enviar e-mail: {e}"

# Interface do Streamlit
st.title("Disparador de Mensagens")

# Sidebar com modelos prontos
modelos = {"Modelo 1": "Texto do Modelo 1", "Modelo 2": "Texto do Modelo 2"}
modelo_selecionado = st.sidebar.selectbox("Escolha um modelo de mensagem", list(modelos.keys()))
mensagem_modelo = modelos[modelo_selecionado]
st.sidebar.text_area("Texto do modelo:", mensagem_modelo, disabled=True)

# Formulário para envio imediato
with st.form("envio_imediato_form"):
    st.write("Envio Imediato de Mensagem e E-mail")
    destinatarios_email = st.text_area("Destinatários do E-mail (separados por vírgula)")
    destinatarios_whatsapp = st.text_area("Números do WhatsApp (separados por vírgula)")
    assunto_email = st.text_input("Assunto do E-mail", value=modelo_selecionado)
    corpo_email = st.text_area("Corpo do E-mail", value=mensagem_modelo)
    outlook_email = st.text_input("Seu E-mail do Outlook")
    senha_email = st.text_input("Senha do E-mail", type="password")
    opcao_envio = st.selectbox("Enviar por", ["Ambos", "Apenas E-mail", "Apenas WhatsApp"])
    botao_envio_imediato = st.form_submit_button("Enviar Agora")

if botao_envio_imediato:
    destinatarios_email_lista = destinatarios_email.split(',')
    destinatarios_whatsapp_lista = destinatarios_whatsapp.split(',')
    
    if opcao_envio in ["Ambos", "Apenas E-mail"]:
        for email in destinatarios_email_lista:
            resposta_email = enviar_email(outlook_email, senha_email, email.strip(), assunto_email, corpo_email)
            st.write(f"Resposta E-mail para {email}: {resposta_email}")

    if opcao_envio in ["Ambos", "Apenas WhatsApp"]:
        for whatsapp in destinatarios_whatsapp_lista:
            resposta_whatsapp = send_link(whatsapp.strip(), whatsapp_token, mensagem_modelo)
            st.write(f"Resposta WhatsApp para {whatsapp}: {resposta_whatsapp}")
