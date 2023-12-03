import streamlit as st
from deta import Deta
import schedule
import time
import threading
import requests
import pytz
from datetime import datetime

# Inicialize o Deta com sua Project Key
DETA_PROJECT_KEY = st.secrets["sua_project_key"]
whatsapp_token = st.secrets["seu_token_whatsapp"]# Substitua com sua Project Key
deta = Deta(DETA_PROJECT_KEY)
db = deta.Base("tasks")

fuso_horario_desejado = pytz.timezone("America/Sao_Paulo")

def agendar_tarefa(horario, task_id):
    try:
        # Certifique-se de que 'horario' está no formato 'HH:MM'
        horario_local = fuso_horario_desejado.localize(datetime.strptime(horario, "%H:%M"))
        horario_utc = horario_local.astimezone(pytz.utc)

        # Agende a tarefa usando o horário em UTC
        schedule.every().day.at(horario_utc.strftime("%H:%M")).do(send_scheduled_message, task_id=task_id)
    except ValueError as e:
        print(f"Erro ao converter o horário: {e}")


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
        text = msg.as_string()
        server.sendmail(outlook_email, destinatario, text)
        server.quit()
        return "E-mail enviado com sucesso!"
    except Exception as e:
        return f"Erro ao enviar e-mail: {e}"
    
# ... [Código anterior] ...

with st.form("envio_imediato_form"):
    st.write("Envio Imediato de Mensagem e E-mail")
    destinatario_email = st.text_input("Destinatário do E-mail")
    assunto_email = st.text_input("Assunto do E-mail")
    corpo_email = st.text_area("Corpo do E-mail")
    outlook_email = st.text_input("Seu E-mail do Outlook")
    senha_email = st.text_input("Senha do E-mail", type="password")
    botao_envio_imediato = st.form_submit_button("Enviar Agora")

if botao_envio_imediato:
    # Enviar WhatsApp
    resposta_whatsapp = send_link(whatsapp, token, description)
    st.write(resposta_whatsapp)

    # Enviar E-mail
    resposta_email = enviar_email(outlook_email, senha_email, destinatario_email, assunto_email, corpo_email)
    st.write(resposta_email)
        








# Função para enviar mensagens para o WhatsApp (mesma função anterior)
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
        # Faltava fechar o parêntese aqui


    # ... (código da função)

# Função para agendar e enviar mensagens
def send_scheduled_message(task_id):
    task = db.get(task_id)
    if task:
        send_link(task["whatsapp"],whatsapp_token, f"Lembrete da Tarefa: {task['description']}")
        # Adicione aqui a lógica para enviar e-mail

# Função para agendar tarefas
def schedule_task():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Interface do Streamlit
st.title("Agendador de Tarefas")

with st.form("task_form"):
    description = st.text_input("Descrição da Tarefa")
    task_time = st.time_input("Horário da Tarefa")
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



# Expander para mostrar tarefas agendadas
with st.expander("Ver Tarefas Agendadas"):
    tasks = db.fetch().items
    for task in tasks:
        st.write(f"{task['description']} - Horário: {task['time']}")



#Aqui você pode adicionar mais lógica para marcar tarefas como concluídas
