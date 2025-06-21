import sys
import os

# Importação de variáveis e módulos internos da ferramenta
import analytics
import utils

# Pipeline:
# 1. Obtenção dos repositórios (Clone)
# 2. Obter issues do repositório via API GitHub V4
# 3. Obter datas dos marcos temporais
# 4. Nas datas dos marcos temporais, encontrar o hash de revision que atende aquela data
# 5. Realizar o checkout nas hashes, iterativamente 
# 6. Calcular Métricas Raw e Halstead para cada revision
# 7. Calcular Métricas Chidamber & Kemerer para cada revision
# 8. Consolidar métricas e issues para cada revision

def analyze_project(project_path: str, project_name: str):
    """
    Analisa um projeto e retorna métricas Raw/Halstead e Chidamber & Kemerer.
    
    Args:
        project_path: Caminho para o diretório do projeto
        project_name: Nome do projeto para identificação
        
    Returns:
        dict: Dicionário com métricas do projeto
    """
    try:
        raw_metrics = analytics.get_project_metrics(project_path)
        ck_metrics = analytics.get_ck_metrics(project_path)
        
        current_version = utils.get_project_checkout_version(project_name)
        stats = analytics.get_project_statistics(raw_metrics, current_version)
        
        return {
            'raw_metrics': raw_metrics,
            'ck_metrics': ck_metrics,
            'statistics': stats,
            'version': current_version
        }
    except Exception as e:
        print(f"Erro ao analisar projeto {project_name}: {e}")
        return None

def main():
    """
    Função principal para demonstração de análise de código.
    
    Executa uma análise completa do projeto Django localizado em 'clones/django/django',
    incluindo métricas Raw/Halstead, Chidamber & Kemerer e estatísticas gerais.
    Os resultados são exibidos no console.
    
    Raises:
        Exception: Se houver erro na análise do projeto
    """
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Demonstração para o Repositório django/django
    django_path = 'clones/django/django'
    project_name = 'django'
    
    print(f"Analisando projeto: {project_name}")
    results = analyze_project(django_path, project_name)
    
    if results:
        print("Métricas Chidamber & Kemerer:")
        print(results['ck_metrics'])
        print("\nEstatísticas do Projeto:")
        print(results['statistics'])
    else:
        print("Falha na análise do projeto.")
    
if __name__ == "__main__":
    main()

