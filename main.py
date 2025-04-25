import releasy

import requests
import json

import chardet
import sys

import issues
import clone

from data import repos

def main():
    sys.stdout.reconfigure(encoding='utf-8')   
    issues.getIssues(repos) 
    clone.cloneRepo(repos)
    
if __name__ == "__main__":
    main()

