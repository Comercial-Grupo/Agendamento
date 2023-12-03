import streamlit as st
from deta import Deta
import schedule
import time
import threading
import requests

# Inicialize o Deta com sua Project Key
deta_project_key = st.secrets["sua_project_key"]
whatsapp_token = st.secrets["seu_token_whatsapp"]# Substitua com sua Project Key
deta = Deta(DETA_PROJECT_KEY)
db = deta.Base("tasks")

# Função para enviar mensagens para o WhatsApp (mesma função anterior)
def send_link(recipient, token, message):
    # ... (código da função)

# Função para agendar e enviar mensagens
def send_scheduled_message(task_id):
    task = db.get(task_id)
    if task:
        send_link(task["whatsapp"], task["token"], f"Lembrete da Tarefa: {task['description']}")
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
    schedule.every().day.at(task_data["time"]).do(send_scheduled_message, task_id=new_task["key"])
    threading.Thread(target=schedule_task, daemon=True).start()
    st.success("Tarefa agendada com sucesso!")

# Expander para mostrar tarefas agendadas
with st.expander("Ver Tarefas Agendadas"):
    tasks = db.fetch().items
    for task in tasks:
        st.write(f"{task['description']} - Horário: {task['time']}")

# Aqui você pode adicionar mais lógica para marcar tarefas como concluídas
