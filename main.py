import requests
import json

import chardet
import sys

# Importação de módulos internos da ferramenta
import issues
import clone
import analytics
from data import repos

def main():
    sys.stdout.reconfigure(encoding='utf-8')   
    
    #clone.clone_repo(repos)
    #issues.get_issues(repos)
     
    repo_demo = {
        'huggingface': 'transformers'
    }
    # Obtenção de Issues via GraphQL API (v4)
    transformers_issues = issues.get_issues(repo_demo) 
    print(transformers_issues)
    
    # Demonstração para Repositório django
    django_path = 'clones/django'
    
    django_metrics_head = analytics.get_project_metrics(django_path)
    django_stats_head = analytics.get_project_statistics(django_metrics_head)
    print(django_stats_head)
    
    django_revisions = analytics.get_git_revisions(django_path, n=100)
    print(django_revisions)
    
    res = analytics.checkout_git_revision(django_path, django_revisions[50])
    print(f"Operação checkout bem sucedida? {res}\n")
    
    django_metrics_anterior = analytics.get_project_metrics(django_path)
    django_stats_anterior = analytics.get_project_statistics(django_metrics_anterior)
    print(django_stats_head)
    print("===============================")
    print(django_stats_anterior)
if __name__ == "__main__":
    main()

