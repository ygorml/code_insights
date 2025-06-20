import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt 
import streamlit as st

import os
import utils
import datetime

def plot_timeline_with_spans(marcos, nome_projeto):
    """
    Generates a timeline plot with specified date markers and shaded spans.

    Args:
        marcos (list): A list of datetime.date objects representing the key
                       temporal milestones. Expected order is [start_span,
                       start_date, end_date, end_span].
    """
    # Convert datetime.date objects to datetime.datetime objects for plotting
    marcos_dt = [datetime.datetime.combine(date, datetime.time.min) for date in marcos]

    # Calculate the span duration from the provided markers
    SPAN = marcos[1] - marcos[0]

    # Create a figure and a set of subplots
    fig, ax = plt.subplots(figsize=(12, 2))

    # Plota os pontos do lado esquerdo (primeiros dois marcos) em azul
    left_dates = marcos_dt[:2]
    ax.plot(left_dates, [0] * len(left_dates), 'o', color='blue')

    # Plota os pontos do lado direito (últimos dois marcos) em vermelho
    right_dates = marcos_dt[2:]
    ax.plot(right_dates, [0] * len(right_dates), 'o', color='red')
    
    # Add vertical lines at the "date_start" and "date_end" points
    ax.axvline(marcos_dt[1], color='blue', linestyle='--', label='Marco Temporal 1')
    ax.axvline(marcos_dt[2], color='red', linestyle='--', label='Marco Temporal 2')

    # Add shaded regions for the SPAN before date_start and after date_end
    ax.axvspan(marcos_dt[0], marcos_dt[1], color='blue', alpha=0.2, label=f'Span ({SPAN.days} dias) antes do MT 1')
    ax.axvspan(marcos_dt[2], marcos_dt[3], color='red', alpha=0.2, label=f'Span ({SPAN.days} dias) depois do MT 2')

    # Set labels and title
    ax.set_xlabel("Data")
    ax.set_title(f"Linha do Tempo do Projeto {nome_projeto}")
    ax.set_yticks([]) # Remove y-axis ticks as it's a timeline visualization

    # Improve date formatting on the x-axis
    fig.autofmt_xdate()

    # Add a legend
    ax.legend()

    # Show the plot
    plt.show()
    
    return fig, ax

st.sidebar.write("code_insights - Configurações")
st.sidebar.divider()

# 1. Obtenção dos Repositórios
st.sidebar.write("1. Obtenção do Repositório")
author = st.sidebar.text_input("GitHub - Autor do repositório")
name = st.sidebar.text_input("GitHub - Nome do repositório")
obter_repo = st.sidebar.button("Obter repositório!")

if obter_repo and author and name:
    repo = {
        f"{author}": f"{name}" 
    }
    utils.clone_repo(repo)

st.sidebar.divider()

# 2. Seleção do Repositório
st.sidebar.write("2. Seleção do Repositório") 
repos_locais = st.sidebar.selectbox("Escolha um repositório local:", utils.listar_repos_clonados())
repo_dir = os.path.join(utils.CLONE_BASE_PATH, repos_locais)

repo_branch = st.sidebar.selectbox("Selecione a branch:", ['main', 'master'])

raw_halstead = st.sidebar.checkbox("Métricas de Halstead e Raw")
ck = st.sidebar.checkbox("Métricas de Chidamber & Kemerer")
issues = st.sidebar.checkbox("Issues via GitHub API v4")

#repo_start_date = ['2024-12-25', '2024-12-24', '2024-12-23', '2024-12-22', '2024-12-21', '2024-12-20']
#repo_start = st.sidebar.selectbox("Selecione a data de início da análise:", repo_start_date)
repo_start = st.sidebar.date_input("Selecione o marco temporal 1 da análise:", format="DD/MM/YYYY", value=datetime.date(2021, 11, 30))

#repo_end_date = ['2024-12-25', '2024-12-24', '2024-12-23', '2024-12-22', '2024-12-21', '2024-12-20']
#repo_end = st.sidebar.selectbox("Selecione a data de fim da análise:", repo_end_date)
repo_end = st.sidebar.date_input("Selecione o marco temporal 2 da análise:", format="DD/MM/YYYY", value=datetime.date(2023, 11, 30))

#st.sidebar.write("⭐ indicam releases do repositório")

window_span = st.sidebar.slider("Selecione o tamanho da janela de análise (em meses):", 0, 24)
SPAN = datetime.timedelta(days=30*window_span)
marcos_temporais = [repo_start-SPAN, repo_start, repo_end, repo_end+SPAN]

rodar_analise = st.sidebar.button("Analisar!")

st.sidebar.divider() 

st.sidebar.write("3. AI Insights")
prompt = st.sidebar.chat_input("O que deseja saber?")
if prompt:
    st.sidebar.write(prompt)
    
i=0
for mt in marcos_temporais:
    i=i+1
    st.write(f"Marco {i}: {mt} - {utils.get_commit_hash_by_date(repo_dir, mt, branch=repo_branch)}")

fig, ax = plot_timeline_with_spans(marcos_temporais, repos_locais)
st.pyplot(fig)
    
