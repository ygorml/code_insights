import requests
import json
from decouple import config

api_key = config('API_KEY')
api_url = config('GITHUB_API_URL')

def get_issues(query_repos):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    for key, value in query_repos.items():    
        query_issue = """query { repository(owner: "%s", name: "%s") { issues(first: 50, states: OPEN) { nodes { number title createdAt } } } }""" % (key, value)
        
        data = {
            "query": query_issue
        }
        
        response = requests.post(api_url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            issues = result.get("data", {}).get("repository", {}).get("issues", {}).get("nodes", [])
            for issue in issues:
                print(f"Número: {issue.get('number')}")
                print(f"Título: {issue.get('title')}")
                print(f"Criada em: {issue.get('createdAt')}")
                print("-" * 30)
        else:
            print("Erro na requisição:", response.status_code, response.text)