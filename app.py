import streamlit as st
from deta import Deta

# Configuração
DETA_PROJECT_KEY = st.secrets["sua_project_key"]
whatsapp_token = st.secrets["seu_token_whatsapp"]
deta = Deta(DETA_PROJECT_KEY)
db = deta.Base("modelos_mensagens")

# Funções CRUD
def criar_modelo(nome, texto):
    return db.put({"key": nome, "texto": texto})

def obter_modelos():
    return db.fetch().items

def atualizar_modelo(nome, texto):
    return db.update({"texto": texto}, nome)

def deletar_modelo(nome):
    return db.delete(nome)

# Interface do Streamlit
st.title("Gerenciador de Modelos de Mensagens")

# Formulário para criar/editar modelos
with st.form("form_modelos"):
    nome_modelo = st.text_input("Nome do Modelo")
    texto_modelo = st.text_area("Texto do Modelo")
    botao_criar = st.form_submit_button("Criar/Atualizar Modelo")
    botao_deletar = st.form_submit_button("Deletar Modelo")

if botao_criar:
    criar_modelo(nome_modelo, texto_modelo)
    st.success("Modelo salvo com sucesso!")

if botao_deletar:
    deletar_modelo(nome_modelo)
    st.success("Modelo deletado com sucesso!")

# Selecionar modelo para edição
modelos = obter_modelos()
modelo_selecionado = st.selectbox("Escolha um modelo para editar", [modelo['key'] for modelo in modelos])
modelo = next((m for m in modelos if m['key'] == modelo_selecionado), None)
if modelo:
    nome_modelo = modelo['key']
    texto_modelo = modelo['texto']

# Mostrar modelos existentes
st.write("Modelos Existentes:")
for modelo in modelos:
    st.text(f"Nome: {modelo['key']}")
    st.text(f"Texto: {modelo['texto']}")
    st.write("---")
