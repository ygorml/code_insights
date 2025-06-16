import requests
import json

import chardet
import sys

# Importação de módulos internos da ferramenta
import issues
import analytics
import utils

from data import repos

def main():
    sys.stdout.reconfigure(encoding='utf-8')   
    
    # utils.clone_repo(repos)
    # issues.get_issues(repos)
     
    # repo_demo = {'huggingface': 'transformers'}
    
    # Obtenção de Issues via GraphQL API (v4)
    # transformers_issues = issues.get_issues(repo_demo) 
    # print(transformers_issues)
    
    # Demonstração para Repositório django
    # file_path = 'clones/django/django/__init__.py'
    # file_metrics = analytics.get_code_metrics(file_path)
    
    django_path = 'clones/django/django'
    django_raw_metrics = analytics.get_project_metrics(django_path)
    django_ck_metrics = analytics.get_ck_metrics(django_path)
    django_stats = analytics.get_project_statistics(django_raw_metrics, utils.get_project_checkout_version('django'))
    
    #django_metrics_head = analytics.get_project_metrics(django_path)
    #print(json.dumps(all_metrics, indent=4))    
    #print(django_ck)
    
    #django_revisions = analytics.get_git_revisions(django_path, n=100)
    #print(django_revisions)
    #res = analytics.checkout_git_revision(django_path, django_revisions[50])
    #print(f"Operação checkout bem sucedida? {res}\n")
    
    #django_metrics_anterior = analytics.get_project_metrics(django_path)
    #django_stats_anterior = analytics.get_project_statistics(django_metrics_anterior, django_revisions[50])
    
    print(django_ck_metrics)
    print(django_stats)
    
if __name__ == "__main__":
    main()

