import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib as plt 
import streamlit as st

import utils

st.sidebar.write("code_insights")
st.sidebar.write("Configurar Análise de Repositório")

st.sidebar.divider()

# Obtenção dos Repositórios

st.sidebar.write("1. Obtenção do Repositório")
author = st.sidebar.text_input("GitHub - Autor do repositório")
name = st.sidebar.text_input("GitHub - Nome do repositório")
st.sidebar.write("Ou") 
link = st.sidebar.text_input("GitHub - Link do repositório")
obter_repo = st.sidebar.button("Obter repositório!")

st.sidebar.divider()

# Seleção do Repositório

st.sidebar.write("2. Seleção do Repositório") 
repos_locais_lista = ['mitmproxy', 'scikit-learn', 'django', 'transformers']
repos_locais = st.sidebar.selectbox("Escolha um repositório local:", repos_locais_lista)
raw_halstead = st.sidebar.checkbox("Raw e Métricas de Halstead")
ck = st.sidebar.checkbox("Métricas de Chidamber & Kemerer")
issues = st.sidebar.checkbox("Issues")

repo_start_date = ['2024-12-25', '2024-12-24', '2024-12-23', '2024-12-22', '2024-12-21', '2024-12-20']
repo_start = st.sidebar.selectbox("Selecione a data de início da análise:", repo_start_date)

repo_end_date = ['⭐2024-12-25', '2024-12-24', '2024-12-23', '2024-12-22', '2024-12-21', '2024-12-20']
repo_end = st.sidebar.selectbox("Selecione a data de fim da análise:", repo_end_date)

st.sidebar.write("⭐ indicam releases do repositório")
rodar_analise = st.sidebar.button("Analisar!")

st.sidebar.divider() 

st.sidebar.write("3. AI Insights")
prompt = st.sidebar.chat_input("O que deseja saber?")
if prompt:
    st.sidebar.write(prompt)


