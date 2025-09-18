import streamlit as st
from validate_docbr import CPF
from conexao import conn
import psycopg2
import psycopg2.extras

st.set_page_config(page_title="Cadastro de Usuários", page_icon="📝")
st.title("Cadastro de Usuários com CPF Validado e Formatado ✅")

cpf_validator = CPF()

# Inicializa session_state
for campo in ["nome", "sobrenome", "cpf", "senha"]:
    if campo not in st.session_state:
        st.session_state[campo] = ""

# ----------------------------
# Função para cadastrar no Postgres
# ----------------------------
def cadastrar_postgres():
    nome = st.session_state["nome"]
    sobrenome = st.session_state["sobrenome"]
    cpf_input = st.session_state["cpf"]

    # Remover pontos e traço para salvar no banco
    cpf_numeros = cpf_input.replace(".", "").replace("-", "")

    # Validação do CPF
    if not cpf_validator.validate(cpf_numeros):
        st.error("❌ CPF inválido! Digite um CPF válido.")
        return

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (nome, sobrenome, cpf) VALUES (%s, %s, %s)",
            (nome, sobrenome, cpf_numeros)
        )
        conn.commit()
        cursor.close()

        st.success("✅ Cadastro efetuado com sucesso!")
        st.image("img/emoji-joinha.jpeg", width=100)
        st.balloons()

        # Limpar campos
        for campo in ["nome", "sobrenome", "cpf", "senha"]:
            st.session_state[campo] = ""

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        st.error(f"❌ Erro: o CPF {cpf_numeros} já está cadastrado!")

    except Exception as e:
        conn.rollback()
        st.error(f"❌ Erro ao cadastrar: {e}")

# ----------------------------
# Função para buscar e formatar cadastros
# ----------------------------
def buscar_cadastros():
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM users ORDER BY id")
        registros = cursor.fetchall()
        cursor.close()

        cadastros_formatados = []
        for reg in registros:
            cpf_formatado = CPF().mask(reg['cpf'])
            cadastros_formatados.append({
                "id": reg["id"],
                "nome": reg["nome"],
                "sobrenome": reg["sobrenome"],
                "cpf": cpf_formatado
            })
        return cadastros_formatados
    except Exception as e:
        st.error(f"Erro ao buscar cadastros: {e}")
        return []

# ----------------------------
# Função para limpar campos
# ----------------------------
def limpar():
    for campo in ["nome", "sobrenome", "cpf", "senha"]:
        st.session_state[campo] = ""

# ----------------------------
# Containers para mensagens e histórico
# ----------------------------
mensagens_container = st.container()
historico_container = st.container()

# ----------------------------
# Inputs de cadastro
# ----------------------------
st.text_input("Nome", key="nome")
st.text_input("Sobrenome", key="sobrenome")
st.text_input("CPF", key="cpf")

# ----------------------------
# Layout com colunas para botões
# ----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.button("Cadastrar", on_click=cadastrar_postgres)

with col2:
    st.button("Limpar", on_click=limpar)

with col3:
    st.text_input("Digite a senha para histórico", type="password", key="senha")

    def mostrar_se_historico():
        if st.session_state["senha"] == "123":  # senha para visualizar histórico
            cadastros = buscar_cadastros()
            if cadastros:
                with historico_container:
                    st.subheader("Histórico de Cadastros:")
                    st.table(cadastros)
        else:
            with mensagens_container:
                st.error("🔒 Senha incorreta!")

        # Limpa a senha do campo após tentar mostrar
        st.session_state["senha"] = ""

    st.button("Mostrar Histórico", on_click=mostrar_se_historico)
    
#  atualização do codigo 1
