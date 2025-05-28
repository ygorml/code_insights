import releasy

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
    #issues.getIssues(repos) 
    #clone.cloneRepo(repos)
    test = analytics.get_project_metrics('clones/django')
    print(type(test))
    for key, value in test.items():
        print(f"{key}: {value}\n")
if __name__ == "__main__":
    main()

