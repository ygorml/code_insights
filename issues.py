import requests
import json
from decouple import config
import pandas as pd
import datetime

api_key = config('API_KEY')
api_url = config('GITHUB_API_URL')

def get_issues_df(query_repos: dict) -> pd.DataFrame:
    """
    Consulta a API GraphQL do GitHub e retorna um DataFrame com as issues abertas dos repositórios.
    
    Args:
        query_repos: Dicionário onde a chave é o owner e o valor é o nome do repo,
                    ex: {"my-org": "my-repo", "user": "project"}
                    
    Returns:
        pd.DataFrame: DataFrame contendo:
            - repo: Nome do repositório no formato "owner/repo"
            - number: Número da issue
            - title: Título da issue
            - created_at: Data de criação da issue (tipo datetime)
            
    Note:
        Utiliza as variáveis globais `api_key` e `api_url` para autenticação.
        Issues com erro são ignoradas e o erro é reportado no console.
        Retorna DataFrame vazio se nenhuma issue for encontrada.
        
    Raises:
        requests.RequestException: Em caso de erro na requisição HTTP
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    issues_data = []

    for owner, repo in query_repos.items():
        query = """
        query {
          repository(owner: "%s", name: "%s") {
            issues(first: 100, states: OPEN) {
              nodes {
                number
                title
                createdAt
              }
            }
          }
        }
        """ % (owner, repo)

        try:
            resp = requests.post(api_url, headers=headers, json={"query": query})
            resp.raise_for_status()
            result = resp.json()

            # Verifica se há erros na resposta GraphQL
            if "errors" in result:
                print(f"[DEBUG] Erros GraphQL para {owner}/{repo}: {result['errors']}")
                continue

            data_section = result.get("data")
            if data_section is None:
                print(f"[DEBUG] Resposta sem 'data' para {owner}/{repo}. Resposta completa: {result}")
                continue

            repository = data_section.get("repository")
            if repository is None:
                print(f"[DEBUG] Repositório {owner}/{repo} não encontrado ou sem dados válidos. Resposta: {result}")
                continue

            issues_container = repository.get("issues")
            if issues_container is None:
                print(f"[DEBUG] Issues não encontradas para {owner}/{repo}. Resposta: {result}")
                continue

            nodes = issues_container.get("nodes", [])
            if not nodes:
                print(f"[DEBUG] Nenhuma issue retornada para {owner}/{repo}.")
            
            for i in nodes:
                issues_data.append({
                    "repo": f"{owner}/{repo}",
                    "number": i.get("number"),
                    "title": i.get("title"),
                    "created_at": pd.to_datetime(i.get("createdAt"))
                })
        except Exception as e:
            print(f"[DEBUG] Erro ao processar repositório {owner}/{repo}: {e}")

    return pd.DataFrame(issues_data)


def compute_issue_metrics(issues_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula métricas gerais de issues para cada repositório utilizando todo o período registrado.
    
    Args:
        issues_df: DataFrame com issues obtido de get_issues_df()
        
    Returns:
        pd.DataFrame: DataFrame com métricas por repositório contendo:
            - repo: Nome do repositório
            - total_issues: Total de issues abertas
            - first_issue_date: Data da criação da primeira issue
            - last_issue_date: Data da criação da última issue
            - duration_days: Duração em dias entre primeira e última issue
            - duration_months: Duração em meses (aproximada, 30 dias/mês)
            - avg_issues_per_month: Média de issues por mês
            - median_interval_days: Mediana do intervalo entre issues consecutivas
            
    Note:
        - Se duration_days for zero, considera 1 mês para evitar divisão por zero
        - median_interval_days será None se houver apenas uma issue no repositório
        - Agrupa issues por repositório para cálculo das métricas
    """
    rows = []
    for repo, grp in issues_df.groupby("repo"):
        total_issues = len(grp)
        first_issue_date = grp["created_at"].min()
        last_issue_date = grp["created_at"].max()
        duration_days = (last_issue_date - first_issue_date).days
        
        # Evita divisão por zero: se duração for zero, considera 1 mês
        duration_months = duration_days / 30 if duration_days > 0 else 1
        avg_issues_per_month = total_issues / duration_months
        
        # Calcula mediana dos intervalos entre issues consecutivas
        sorted_dates = grp["created_at"].sort_values()
        if len(sorted_dates) > 1:
            intervals = sorted_dates.diff().dropna().dt.days
            median_interval_days = intervals.median()
        else:
            median_interval_days = None
            
        rows.append({
            "repo": repo,
            "total_issues": total_issues,
            "first_issue_date": first_issue_date,
            "last_issue_date": last_issue_date,
            "duration_days": duration_days,
            "duration_months": round(duration_months, 2),
            "avg_issues_per_month": round(avg_issues_per_month, 2),
            "median_interval_days": median_interval_days
        })
        
    return pd.DataFrame(rows)