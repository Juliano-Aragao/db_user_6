import psycopg2
import streamlit as st

# Conexão com o Postgres
conn = psycopg2.connect(
    host="localhost",          # ou IP do servidor
    database="cadastro_user",  # seu banco
    user="juliano",        # seu usuário
    password="senha123"       # sua senha
)
cursor = conn.cursor()
