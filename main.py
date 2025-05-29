import requests
import json

import chardet
import sys

import issues
import clone
import analytics

from data import repos

def main():
    sys.stdout.reconfigure(encoding='utf-8')   
    #issues.get_issues(repos) 
    #clone.clone_repo(repos)
    test = analytics.get_project_metrics('clones/django')
    stats = analytics.get_project_statistics(test)
    print(stats)
if __name__ == "__main__":
    main()

