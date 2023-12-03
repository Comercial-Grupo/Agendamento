import streamlit as st
from deta import Deta
import schedule
import time
import threading
import requests
import pytz
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.background import BackgroundScheduler

# Inicialização e Configuração
DETA_PROJECT_KEY = st.secrets["sua_project_key"]
whatsapp_token = st.secrets["seu_token_whatsapp"]
deta = Deta(DETA_PROJECT_KEY)
db = deta.Base("tasks")
fuso_horario_desejado = pytz.timezone("America/Sao_Paulo")
scheduler = BackgroundScheduler()
scheduler.start()

# Função para enviar mensagens para o WhatsApp
def send_link(recipient, token, message):
    url = f'https://server.api-wa.me/message/text?key={token}'
    headers = {
        'accept': '*/*',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {"messageData": {"to": recipient, "text": message}}
    response = requests.post(url, json=payload, headers=headers)
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

# Função para agendar e enviar mensagens
def send_scheduled_message(task_id):
    task = db.get(task_id)
    if task:
        send_link(task["whatsapp"], task["token"], f"Lembrete da Tarefa: {task['description']}")

# Função para agendar tarefas
def schedule_task():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Função para agendar tarefa
def agendar_tarefa(horario, task_id):
    try:
        horario_local = fuso_horario_desejado.localize(datetime.strptime(horario, "%H:%M"))
        horario_utc = horario_local.astimezone(pytz.utc)
        scheduler.add_job(send_scheduled_message, 'cron', day_of_week='mon-sun', hour=horario_utc.hour, minute=horario_utc.minute, args=[task_id])
    except ValueError as e:
        print(f"Erro ao converter o horário: {e}")

# Interface do Streamlit
st.title("Agendador de Tarefas")

# Formulário para agendar tarefas
with st.form("task_form"):
    description = st.text_input("Descrição da Tarefa")
    task_time = st.time_input("Horário da Tarefa", step=300)
    email = st.text_input("E-mail")
    whatsapp = st.text_input("Número do WhatsApp")
    token = st.text_input("Token do WhatsApp", type="password")
    submit_button = st.form_submit_button("Agendar Tarefa")

if submit_button:
    task_data = {
        "description": description,
        "time": str(task_time),
        "email": email,
        "whatsapp": whatsapp,
        "token": token
    }
    new_task = db.put(task_data)
    agendar_tarefa(task_data["time"], new_task["key"])
    print(f"Tarefa agendada para {task_data['time']}")
    print(f"Horário atual: {datetime.now(fuso_horario_desejado).strftime('%H:%M')}")
    threading.Thread(target=schedule_task, daemon=True).start()
    st.success("Tarefa agendada com sucesso!")

# Formulário para envio imediato
with st.form("envio_imediato_form"):
    st.write("Envio Imediato de Mensagem e E-mail")
    destinatario_email = st.text_input("Destinatário do E-mail")
    assunto_email = st.text_input("Assunto do E-mail")
    corpo_email = st.text_area("Corpo do E-mail")
    outlook_email = st.text_input("Seu E-mail do Outlook")
    senha_email = st.text_input("Senha do E-mail", type="password")
    botao_envio_imediato = st.form_submit_button("Enviar Agora")

if botao_envio_imediato:
    resposta_whatsapp = send_link(whatsapp, token, description)
    st.write(resposta_whatsapp)
    resposta_email = enviar_email(outlook_email, senha_email, destinatario_email, assunto_email, corpo_email)
    st.write(resposta_email)

st.on_session_end(scheduler.shutdown)
with st.expander("Ver Tarefas Agendadas"):
    tasks = db.fetch().items
    for task in tasks:
        st.write(f"{task['description']} - Horário: {task['time']}")
