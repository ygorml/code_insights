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
    
    #issues.get_issues(repos) 
    #clone.clone_repo(repos)
    django_metrics = analytics.get_project_metrics('clones/django')
    django_stats = analytics.get_project_statistics(django_metrics)
    print(django_stats)
if __name__ == "__main__":
    main()

