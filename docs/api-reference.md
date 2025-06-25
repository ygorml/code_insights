# API Reference - Code Insights

## Módulos Principais

### `analytics.py` - Motor de Análise de Métricas

#### Classes

##### `ClassInfo`
Armazena informações sobre uma classe para análise de métricas C&K.

```python
class ClassInfo:
    def __init__(self, name: str)
```

**Atributos**:
- `name` (str): Nome da classe
- `methods` (list): Lista de métodos da classe
- `attributes` (set): Conjunto de atributos da classe
- `base_classes` (list): Lista de classes base (herança)
- `children` (list): Lista de classes filhas
- `calls` (set): Conjunto de chamadas feitas pela classe
- `called_by` (set): Conjunto de classes que chamam esta classe

##### `CKAnalyzer`
Analisador de AST para cálculo de métricas Chidamber & Kemerer.

```python
class CKAnalyzer(ast.NodeVisitor):
    def __init__(self)
```

**Métodos**:
- `visit_ClassDef(node)`: Visita definição de classe
- `visit_FunctionDef(node)`: Visita definição de função/método
- `visit_Assign(node)`: Visita atribuição
- `build_hierarchy()`: Constrói hierarquia de herança
- `compute_metrics()`: Calcula métricas C&K

#### Funções Principais

##### `get_code_metrics(file_path: str) -> dict`
Calcula métricas Raw e Halstead para um arquivo Python.

**Parâmetros**:
- `file_path`: Caminho para o arquivo Python

**Retorna**:
```python
{
    'loc': int,                    # Total de linhas de código
    'lloc': int,                   # Linhas lógicas de código
    'sloc': int,                   # Linhas de código fonte
    'comments': int,               # Número de comentários
    'multi': int,                  # Strings multilinha
    'blank': int,                  # Linhas em branco
    'average_complexity': float,   # Complexidade ciclomática média
    'maintainability_index': float # Índice de manutenibilidade
}
```

**Exemplo**:
```python
metrics = get_code_metrics('src/main.py')
print(f"LOC: {metrics['loc']}")
print(f"Complexidade: {metrics['average_complexity']:.2f}")
```

##### `get_project_metrics(project_path: str) -> dict`
Analisa métricas para todos os arquivos Python em um projeto.

**Parâmetros**:
- `project_path`: Caminho para o diretório do projeto

**Retorna**:
```python
{
    'arquivo1.py': {métrica: valor},
    'arquivo2.py': {métrica: valor},
    ...
}
```

##### `get_ck_metrics(path: str) -> dict`
Calcula métricas Chidamber & Kemerer para todos os arquivos Python.

**Parâmetros**:
- `path`: Caminho para o diretório a ser analisado

**Retorna**:
```python
{
    'arquivo.py': {
        'ClassName': {
            'WMC': int,    # Weighted Methods per Class
            'DIT': int,    # Depth of Inheritance Tree
            'NOC': int,    # Number of Children
            'RFC': int,    # Response for a Class
            'CBO': int,    # Coupling Between Objects
            'LCOM': int    # Lack of Cohesion of Methods
        }
    }
}
```

##### `get_project_statistics(metrics_report: dict, revision_id: str) -> dict`
Gera estatísticas agregadas a partir de métricas por arquivo.

**Parâmetros**:
- `metrics_report`: Relatório de métricas por arquivo
- `revision_id`: Identificador da revisão

**Retorna**:
```python
{
    'revision_id': str,
    'total_loc': int,
    'total_lloc': int,
    'total_sloc': int,
    'total_comments': int,
    'total_multi': int,
    'total_blank': int,
    'n_files': int,
    'mean_maintainability_index': float,
    'mean_complexity': float
}
```

---

### `issues.py` - Integração com GitHub API

#### `get_issues_df(query_repos: dict) -> pd.DataFrame`
Consulta a API GraphQL do GitHub para obter issues abertas.

**Parâmetros**:
- `query_repos`: `{"owner": "repo_name", ...}`

**Retorna**:
DataFrame com colunas:
- `repo`: Nome do repositório (formato "owner/repo")
- `number`: Número da issue
- `title`: Título da issue
- `created_at`: Data de criação (datetime)

**Exemplo**:
```python
repos = {"django": "django", "python": "cpython"}
issues_df = get_issues_df(repos)
print(f"Total de issues: {len(issues_df)}")
```

#### `compute_issue_metrics(issues_df: pd.DataFrame) -> pd.DataFrame`
Calcula métricas temporais de issues por repositório.

**Parâmetros**:
- `issues_df`: DataFrame de issues do `get_issues_df()`

**Retorna**:
DataFrame com métricas:
- `repo`: Nome do repositório
- `total_issues`: Total de issues abertas
- `first_issue_date`: Data da primeira issue
- `last_issue_date`: Data da última issue
- `duration_days`: Duração em dias
- `duration_months`: Duração em meses
- `avg_issues_per_month`: Média de issues por mês
- `median_interval_days`: Mediana do intervalo entre issues

---

### `utils.py` - Utilitários Git e Sistema

#### `clone_repo(repos_to_clone: dict) -> bool`
Clona repositórios do GitHub.

**Parâmetros**:
- `repos_to_clone`: `{"owner": "repo_name"}`

**Retorna**:
- `bool`: True se todos os repos foram clonados com sucesso

**Exemplo**:
```python
success = clone_repo({"django": "django"})
if success:
    print("Repositório clonado com sucesso")
```

#### `get_git_revisions(repo_path: str, n: int = 100) -> list`
Obtém as últimas n revisões de um repositório git.

**Parâmetros**:
- `repo_path`: Caminho para o repositório
- `n`: Número de revisões (padrão: 100)

**Retorna**:
- `list`: Lista de hashes de commit

#### `checkout_git_revision(repo_path: str, revision: str) -> bool`
Faz checkout de uma revisão específica.

**Parâmetros**:
- `repo_path`: Caminho para o repositório
- `revision`: Hash do commit, nome da branch ou tag

**Retorna**:
- `bool`: True se o checkout foi bem-sucedido

#### `get_commit_hash_by_date(repo_path: str, date: Union[str, datetime], branch: str = "master") -> str`
Retorna o hash do último commit anterior ou igual à data fornecida.

**Parâmetros**:
- `repo_path`: Caminho para o repositório Git
- `date`: Data como datetime ou string
- `branch`: Branch para busca (padrão: "master")

**Retorna**:
- `str`: Hash do commit encontrado

**Raises**:
- `ValueError`: Se não houver commit até a data
- `RuntimeError`: Se o comando Git falhar

**Exemplo**:
```python
hash_commit = get_commit_hash_by_date(
    "clones/django/django", 
    "2023-01-01", 
    "main"
)
```

#### `listar_repos_clonados() -> list`
Lista todos os repositórios clonados no diretório base.

**Retorna**:
- `list`: Lista de strings no formato "owner/repo"

#### `get_project_checkout_version(project_name: str) -> str`
Obtém a versão atual do checkout do projeto.

**Parâmetros**:
- `project_name`: Nome do projeto

**Retorna**:
- `str`: Hash da revisão atual, ou string vazia em caso de erro

---

### `visualization.py` - Interface e Processamento

#### Funções de Conversão

##### `projeto_to_dataframe(data: dict) -> pd.DataFrame`
Converte métricas de projeto para DataFrame.

**Parâmetros**:
- `data`: `{arquivo: {métrica: valor}}`

**Retorna**:
- DataFrame com métricas organizadas por arquivo

##### `ck_metrics_to_dataframe(data: dict) -> pd.DataFrame`
Converte métricas C&K para DataFrame.

**Parâmetros**:
- `data`: `{arquivo: {classe: {métrica: valor}}}`

**Retorna**:
- DataFrame com métricas C&K por arquivo e classe

##### `relatorio_estatistico_to_dataframe(data: dict) -> pd.DataFrame`
Converte estatísticas do projeto para DataFrame.

#### Funções de Interface

##### `gerar_tabelas(hash_revision: str, repo_dir: str, project_name: str) -> None`
Gera tabelas de métricas no Streamlit.

**Parâmetros**:
- `hash_revision`: Hash da revisão para análise
- `repo_dir`: Caminho para o repositório
- `project_name`: Nome do projeto

**Side Effects**:
- Faz checkout da revisão especificada
- Exibe tabelas no Streamlit
- Pode exibir mensagens de erro

##### `exportar_dados_csv(hash_revision: str, repo_dir: str, project_name: str, output_dir: str = "exports") -> dict`
Exporta todos os dados de métricas para arquivos CSV.

**Parâmetros**:
- `hash_revision`: Hash da revisão do git para análise
- `repo_dir`: Caminho para o diretório do repositório
- `project_name`: Nome do projeto
- `output_dir`: Diretório de saída para os arquivos CSV (padrão: "exports")

**Retorna**:
```python
{
    'issues': str,           # Caminho do CSV de métricas de issues
    'metricas_arquivo': str, # Caminho do CSV de métricas por arquivo
    'estatisticas': str,     # Caminho do CSV de estatísticas do projeto
    'ck_metricas': str      # Caminho do CSV de métricas C&K
}
```

**Side Effects**:
- Cria automaticamente o diretório de saída e todos os subdiretórios necessários
- Gera arquivos CSV com métricas do projeto (issues, métricas por arquivo, estatísticas, C&K)
- Faz checkout da revisão especificada

**Melhorias Recentes**:
- Criação automática de diretórios aninhados para evitar erros de "diretório não existe"
- Suporte robusto para estruturas de pastas complexas (ex: `exports/huggingface/subdir`)

**Exemplo**:
```python
arquivos = exportar_dados_csv(
    "abc123def", 
    "clones/django/django", 
    "django-project"
)
print(f"Métricas salvas em: {arquivos['metricas_arquivo']}")
```

##### `criar_csv_agregado(dados_por_hash: list, project_name: str, output_dir: str = "exports") -> str`
Cria um CSV agregado com métricas de evolução temporal do projeto.

**Parâmetros**:
- `dados_por_hash`: Lista de dicionários com dados de cada hash
- `project_name`: Nome do projeto
- `output_dir`: Diretório de saída para o arquivo CSV (padrão: "exports")

**Retorna**:
- `str`: Caminho do arquivo CSV agregado gerado

**Side Effects**:
- Cria arquivo CSV com métricas agregadas por hash/marco temporal
- Inclui dados de estatísticas, issues e métricas C&K resumidas

**Formato do CSV Agregado**:
```csv
hash,hash_short,timestamp,total_loc,total_lloc,total_sloc,total_comments,total_blank,n_files,mean_maintainability_index,mean_complexity,total_issues,avg_issues_per_month,median_interval_days,total_classes,avg_wmc,avg_dit,avg_noc,avg_rfc,avg_cbo,avg_lcom
```

**Exemplo**:
```python
dados_hashes = [
    {'hash': 'abc123', 'dados': dados_hash1},
    {'hash': 'def456', 'dados': dados_hash2}
]
arquivo_agregado = criar_csv_agregado(dados_hashes, "django-project")
print(f"CSV de evolução temporal: {arquivo_agregado}")
```

##### `coletar_dados_para_agregacao(hash_revision: str, repo_dir: str, project_name: str) -> dict`
Coleta todos os dados de métricas para um hash específico.

**Parâmetros**:
- `hash_revision`: Hash da revisão do git para análise
- `repo_dir`: Caminho para o diretório do repositório
- `project_name`: Nome do projeto

**Retorna**:
```python
{
    'estatisticas': dict,        # Estatísticas agregadas do projeto
    'ck_metrics': pd.DataFrame,  # Métricas C&K em DataFrame
    'issues_metrics': pd.DataFrame  # Métricas de issues (se disponível)
}
```

**Side Effects**:
- Faz checkout da revisão especificada
- Calcula métricas Raw/Halstead, C&K e issues

##### `plot_timeline_with_spans(marcos: list, nome_projeto: str) -> tuple`
Gera gráfico de timeline com marcos temporais.

**Parâmetros**:
- `marcos`: Lista de datetime.date (4 marcos temporais)
- `nome_projeto`: Nome do projeto

**Retorna**:
- `tuple`: (figura_matplotlib, eixos_matplotlib)

---

## Exemplos de Uso Completo

### Análise Básica de Projeto
```python
import analytics
import utils

# 1. Clonar repositório
success = utils.clone_repo({"django": "django"})

# 2. Analisar métricas
project_path = "clones/django/django"
raw_metrics = analytics.get_project_metrics(project_path)
ck_metrics = analytics.get_ck_metrics(project_path)
stats = analytics.get_project_statistics(raw_metrics, "main")

# 3. Exibir resultados
print(f"Total LOC: {stats['total_loc']}")
print(f"Arquivos analisados: {stats['n_files']}")
print(f"Complexidade média: {stats['mean_complexity']:.2f}")
```

### Análise Temporal com Exportação CSV e Agregação
```python
import datetime
import utils
import analytics
from visualization import exportar_dados_csv, coletar_dados_para_agregacao, criar_csv_agregado

repo_path = "clones/django/django"

# Definir marcos temporais
dates = [
    datetime.date(2020, 1, 1),
    datetime.date(2021, 1, 1),
    datetime.date(2022, 1, 1),
    datetime.date(2023, 1, 1)
]

results = []
dados_para_agregacao = []

for date in dates:
    # Obter hash da data
    hash_commit = utils.get_commit_hash_by_date(repo_path, date, "main")
    
    # Fazer checkout
    utils.checkout_git_revision(repo_path, hash_commit)
    
    # Calcular métricas
    raw_metrics = analytics.get_project_metrics(repo_path)
    stats = analytics.get_project_statistics(raw_metrics, hash_commit)
    
    # Exportar para CSV individuais
    csv_files = exportar_dados_csv(hash_commit, repo_path, "django")
    
    # Coletar dados para agregação
    dados_hash = coletar_dados_para_agregacao(hash_commit, repo_path, "django")
    dados_para_agregacao.append({
        'hash': hash_commit,
        'dados': dados_hash
    })
    
    results.append({
        'date': date,
        'hash': hash_commit,
        'loc': stats['total_loc'],
        'complexity': stats['mean_complexity'],
        'csv_files': csv_files
    })

# Gerar CSV agregado de evolução temporal
arquivo_agregado = criar_csv_agregado(dados_para_agregacao, "django")
print(f"CSV agregado gerado: {arquivo_agregado}")

# Análise de evolução
for result in results:
    print(f"{result['date']}: LOC={result['loc']}, Complexity={result['complexity']:.2f}")
    print(f"  CSVs individuais: {list(result['csv_files'].keys())}")
```

### Análise de Issues
```python
import issues

# Obter issues
repos = {"django": "django"}
issues_df = issues.get_issues_df(repos)

# Calcular métricas
metrics = issues.compute_issue_metrics(issues_df)

print("Métricas de Issues:")
for _, row in metrics.iterrows():
    print(f"Repo: {row['repo']}")
    print(f"Total Issues: {row['total_issues']}")
    print(f"Duração: {row['duration_months']} meses")
    print(f"Issues/mês: {row['avg_issues_per_month']:.1f}")
```

## Configuração de Ambiente

### Variáveis Obrigatórias
```env
API_KEY=github_personal_access_token
GITHUB_API_URL=https://api.github.com/graphql
CLONE_REPOS_BASE=/path/to/clone/directory
```

### Estrutura de Dados

#### Configuração de Repositórios (`data.py`)
```python
repos = {
    'django': 'django',
    'scikit-learn': 'scikit-learn',
    'mitmproxy': 'mitmproxy',
    'huggingface': 'transformers',
    'ccxt': 'ccxt'
}
```

### Tratamento de Erros

#### Erros Comuns e Soluções
```python
try:
    metrics = analytics.get_code_metrics('file.py')
except SyntaxError:
    print("Arquivo com erro de sintaxe - ignorado")
except FileNotFoundError:
    print("Arquivo não encontrado")

try:
    hash_commit = utils.get_commit_hash_by_date(repo, date)
except ValueError as e:
    print(f"Nenhum commit encontrado: {e}")
except RuntimeError as e:
    print(f"Erro no Git: {e}")
```