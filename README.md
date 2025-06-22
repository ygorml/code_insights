# Code Insights

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-pytest-orange.svg)](tests/)
[![Code Quality](https://img.shields.io/badge/code%20quality-analyzed-brightgreen.svg)](#métricas-disponíveis)
[![Streamlit](https://img.shields.io/badge/interface-streamlit-red.svg)](https://streamlit.io)
[![GitHub Issues](https://img.shields.io/badge/issues-GitHub%20API-blue.svg)](https://docs.github.com/en/rest)

Uma ferramenta abrangente para análise de métricas de qualidade de código, focada em repositórios Python com suporte para métricas Raw/Halstead, Chidamber & Kemerer, e análise de issues do GitHub.

## 📋 Funcionalidades

- **Análise de Métricas Raw/Halstead**: LOC, LLOC, complexidade ciclomática, índice de manutenibilidade
- **Métricas Chidamber & Kemerer**: WMC, DIT, NOC, RFC, CBO, LCOM para análise orientada a objetos
- **Análise de Issues GitHub**: Métricas temporais e estatísticas de issues via API GraphQL
- **Interface Streamlit**: Dashboard interativo para visualização de dados
- **Análise Temporal**: Comparação de métricas entre diferentes revisões do git
- **Exportação de Dados**: DataFrames pandas para análise posterior

## 🏗️ Arquitetura

```
Code Insights
├── main.py              # Ponto de entrada e demonstração
├── analytics.py         # Motores de cálculo de métricas
├── visualization.py     # Interface Streamlit e processamento de dados
├── issues.py           # Integração com API GitHub
├── utils.py            # Utilitários git e gerenciamento de arquivos
├── data.py             # Configuração de repositórios
└── requirements.txt    # Dependências do projeto
```

## 🔄 Pipeline de Análise

1. **Clonagem de Repositórios**: Download automático de repos GitHub
2. **Obtenção de Issues**: Consulta via API GraphQL GitHub V4
3. **Definição de marcos temporais**: Seleção de datas para análise
4. **Checkout por revisão**: Navegação temporal no histórico git
5. **Cálculo de Métricas Raw/Halstead**: Para cada revisão
6. **Cálculo de Métricas C&K**: Análise orientada a objetos
7. **Consolidação**: Agregação de métricas e issues por revisão

## 🚀 Instalação

### Pré-requisitos
- Python 3.8+
- Git
- Acesso à internet para API GitHub

### Configuração

1. **Clone o repositório**:
```bash
git clone <url-do-repositorio>
cd code_insights
```

2. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

3. **Instale dependências de teste (opcional)**:
```bash
pip install -r test-requirements.txt
```

4. **Configure variáveis de ambiente**:
Crie um arquivo `.env` na raiz do projeto:
```env
API_KEY=your_github_token_here
GITHUB_API_URL=https://api.github.com/graphql
CLONE_REPOS_BASE=/path/to/clone/directory
```

### Obtenção do Token GitHub
1. Acesse GitHub → Settings → Developer settings → Personal access tokens
2. Gere um novo token com permissões de leitura para repositórios
3. Adicione o token no arquivo `.env`

## 📖 Uso

### Análise Básica (CLI)
```bash
python main.py
```

### Interface Web (Streamlit)
```bash
streamlit run visualization.py
```

### Uso Programático
```python
import analytics
import utils

# Clona um repositório
utils.clone_repo({"owner": "repo_name"})

# Analisa métricas
project_path = "clones/owner/repo_name"
raw_metrics = analytics.get_project_metrics(project_path)
ck_metrics = analytics.get_ck_metrics(project_path)
stats = analytics.get_project_statistics(raw_metrics, "main")
```

## 📊 Métricas Disponíveis

### Raw & Halstead Metrics
- **LOC**: Total de linhas de código
- **LLOC**: Linhas lógicas de código  
- **SLOC**: Linhas de código fonte
- **Comments**: Número de comentários
- **Complexity**: Complexidade ciclomática média
- **Maintainability Index**: Índice de manutenibilidade

### Chidamber & Kemerer Metrics
- **WMC**: Weighted Methods per Class
- **DIT**: Depth of Inheritance Tree
- **NOC**: Number of Children
- **RFC**: Response for a Class
- **CBO**: Coupling Between Objects
- **LCOM**: Lack of Cohesion of Methods

### Issues Metrics
- **Total Issues**: Número total de issues abertas
- **Duration**: Período de atividade do projeto
- **Issue Rate**: Taxa de criação de issues
- **Temporal Analysis**: Distribuição temporal de issues

## 🔧 API Reference

### analytics.py
- `get_project_metrics(path)`: Métricas Raw/Halstead
- `get_ck_metrics(path)`: Métricas Chidamber & Kemerer
- `get_project_statistics(metrics, revision)`: Estatísticas agregadas

### utils.py
- `clone_repo(repos_dict)`: Clonagem de repositórios
- `checkout_git_revision(path, hash)`: Checkout temporal
- `get_commit_hash_by_date(path, date)`: Hash por data

### issues.py
- `get_issues_df(repos)`: Issues via API GitHub
- `compute_issue_metrics(df)`: Métricas temporais de issues

## 🧪 Testes

### Executar Testes
```bash
# Executar todos os testes
pytest

# Executar testes com cobertura
pytest --cov=. --cov-report=html

# Executar testes específicos
pytest tests/test_analytics.py -v

# Executar testes por categoria
pytest -m unit      # Testes unitários
pytest -m integration # Testes de integração
```

### Estrutura de Testes
```
tests/
├── __init__.py
├── test_analytics.py      # Testes do módulo analytics
├── test_utils.py          # Testes do módulo utils
├── test_issues.py         # Testes do módulo issues
├── test_main.py           # Testes da função principal
├── test_visualization.py  # Testes da interface Streamlit
└── test_data.py           # Testes de configuração de dados
```

## 🎯 Casos de Uso

1. **Pesquisa Acadêmica**: Análise evolutiva de qualidade de código
2. **Code Review**: Identificação de áreas problemáticas
3. **Refatoração**: Métricas antes/depois de melhorias
4. **Benchmarking**: Comparação entre projetos
5. **Monitoramento**: Acompanhamento contínuo da qualidade

## 🔍 Exemplo de Análise

```python
# Análise completa de um projeto
from main import analyze_project

results = analyze_project("clones/django/django", "django")

print("Métricas C&K:")
for file_path, classes in results['ck_metrics'].items():
    for class_name, metrics in classes.items():
        print(f"{class_name}: WMC={metrics['WMC']}, DIT={metrics['DIT']}")

print("Estatísticas Gerais:")
stats = results['statistics']
print(f"Total LOC: {stats['total_loc']}")
print(f"Complexidade Média: {stats['mean_complexity']:.2f}")
```

## 📊 Cobertura de Testes

O projeto inclui uma suíte abrangente de testes cobrindo:

- **Testes Unitários**: Validação de funções individuais
- **Testes de Integração**: Verificação de interação entre módulos
- **Testes de API**: Validação de chamadas para GitHub API
- **Testes de Análise**: Verificação de cálculos de métricas
- **Testes de Interface**: Validação de componentes Streamlit

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Execute os testes (`pytest`)
4. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
5. Push para a branch (`git push origin feature/AmazingFeature`)
6. Abra um Pull Request

### Padrões de Desenvolvimento

- **Cobertura de Testes**: Manter cobertura > 80%
- **Documentação**: Docstrings em todas as funções públicas
- **Estilo de Código**: Seguir PEP 8
- **Testes**: Adicionar testes para novas funcionalidades
