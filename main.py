import requests
import json
import os

import chardet
import sys

# Importação de variáveis e módulos internos da ferramenta
import issues
import analytics
import utils
from data import repos

# Pipeline:
# 1. Obtenção dos repositórios (Clone)
# 2. Obter issues do repositório via API GitHub V4
# 3. Obter datas dos marcos temporais
# 4. Nas datas dos marcos temporais, encontrar o hash de revision que atende aquela data
# 5. Realizar o checkout nas hashes, iterativamente 
# 6. Calcular Métricas Raw e Halstead para cada revision
# 7. Calcular Métricas Chidamber & Kemerer para cada revision
# 8. Consolidar métricas e issues para cada revision

def main():
    sys.stdout.reconfigure(encoding='utf-8')   
    
    # Demonstração para 1 arquivo do Repositório django/django
    django_path = 'clones/django/django'
    # file_path = 'clones/django/django/__init__.py'
    # file_metrics = analytics.get_code_metrics(file_path)
    
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

