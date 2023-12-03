import streamlit as st
from deta import Deta
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

# Inicialize o scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Funções send_link e enviar_email permanecem as mesmas

# Função para agendar e enviar mensagens
def send_scheduled_message(task_id):
    task = db.get(task_id)
    if task:
        send_link(task["whatsapp"], task["token"], f"Lembrete da Tarefa: {task['description']}")
        # Aqui você pode adicionar a lógica para enviar e-mail

# Função para agendar tarefa com APScheduler
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


with st.expander("Ver Tarefas Agendadas"):
    tasks = db.fetch().items
    for task in tasks:
        st.write(f"{task['description']} - Horário: {task['time']}")
import atexit
atexit.register(lambda: scheduler.shutdown())
