import os
import subprocess

from pydriller import Repository

# Python Metrics
import radon.metrics as metrics
import radon.complexity as complexity
from radon.complexity import cc_visit
import radon.raw as raw

# TODO: Implementar cálculo de métricas para C++ 
# import lizard

# TODO: Obter hashes dos marcos temporais
# import releasy

import ast
import json
from collections import defaultdict

# Importação de módulos internos da ferramenta
from data import repos

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =============================================================================
# Chidamber & Kemerer Metrics Analysis
# =============================================================================

class ClassInfo:
    """
    Armazena informações sobre uma classe para análise de métricas C&K.
    
    Attributes:
        name (str): Nome da classe
        methods (list): Lista de métodos da classe
        attributes (set): Conjunto de atributos da classe
        base_classes (list): Lista de classes base (herança)
        children (list): Lista de classes filhas
        calls (set): Conjunto de chamadas feitas pela classe
        called_by (set): Conjunto de classes que chamam esta classe
    """
    
    def __init__(self, name: str):
        """
        Inicializa uma nova instância de ClassInfo.
        
        Args:
            name: Nome da classe
        """
        self.name = name
        self.methods = []
        self.attributes = set()
        self.base_classes = []
        self.children = []
        self.calls = set()
        self.called_by = set()

class CKAnalyzer(ast.NodeVisitor):
    """
    Analisador de AST para cálculo de métricas Chidamber & Kemerer.
    
    Esta classe visita nodes da AST de código Python para extrair informações
    sobre classes e calcular as métricas C&K.
    
    Attributes:
        classes (dict): Dicionário com informações das classes encontradas
        current_class (str): Nome da classe sendo analisada atualmente
    """
    
    def __init__(self):
        """
        Inicializa o analisador C&K.
        """
        self.classes = {}
        self.current_class = None

    def visit_ClassDef(self, node):
        """
        Visita uma definição de classe na AST.
        
        Args:
            node (ast.ClassDef): Nó da AST representando uma classe
        """
        class_name = node.name
        class_info = self.classes.setdefault(class_name, ClassInfo(class_name))
        class_info.base_classes = [b.id for b in node.bases if isinstance(b, ast.Name)]

        parent_class = self.current_class
        self.current_class = class_name
        for stmt in node.body:
            self.visit(stmt)
        self.current_class = parent_class

    def visit_FunctionDef(self, node):
        """
        Visita uma definição de função/método na AST.
        
        Args:
            node (ast.FunctionDef): Nó da AST representando uma função/método
        """
        if self.current_class:
            self.classes[self.current_class].methods.append(node.name)
            for n in ast.walk(node):
                if isinstance(n, ast.Call):
                    if isinstance(n.func, ast.Attribute):
                        self.classes[self.current_class].calls.add(n.func.attr)
                    elif isinstance(n.func, ast.Name):
                        self.classes[self.current_class].calls.add(n.func.id)
                elif isinstance(n, ast.Attribute):
                    self.classes[self.current_class].attributes.add(n.attr)

    def visit_Assign(self, node):
        """
        Visita uma atribuição na AST.
        
        Args:
            node (ast.Assign): Nó da AST representando uma atribuição
        """
        if self.current_class:
            for target in node.targets:
                if isinstance(target, ast.Attribute):
                    self.classes[self.current_class].attributes.add(target.attr)

    def build_hierarchy(self):
        """
        Constrói a hierarquia de herança entre as classes.
        
        Popula a lista 'children' de cada classe com suas classes filhas.
        """
        for cls in self.classes.values():
            for base in cls.base_classes:
                if base in self.classes:
                    self.classes[base].children.append(cls.name)

    def compute_metrics(self):
        """
        Calcula as métricas Chidamber & Kemerer para todas as classes.
        
        Returns:
            dict: Dicionário com métricas C&K para cada classe:
                - WMC (Weighted Methods per Class): Número de métodos
                - DIT (Depth of Inheritance Tree): Profundidade na árvore de herança
                - NOC (Number of Children): Número de classes filhas
                - RFC (Response for a Class): Conjunto de métodos que podem ser invocados
                - CBO (Coupling Between Objects): Acoplamento entre objetos
                - LCOM (Lack of Cohesion of Methods): Falta de coesão entre métodos
        """
        metrics = {}
        for cls in self.classes.values():
            wmc = len(cls.methods)
            dit = self._compute_dit(cls.name)
            noc = len(cls.children)
            rfc = len(cls.calls) + len(cls.methods)
            cbo = self._compute_cbo(cls)
            lcom = self._compute_lcom(cls)

            metrics[cls.name] = {
                'WMC': wmc,
                'DIT': dit,
                'NOC': noc,
                'RFC': rfc,
                'CBO': cbo,
                'LCOM': lcom
            }
        return metrics

    def _compute_dit(self, class_name):
        """
        Calcula a profundidade na árvore de herança (DIT).
        
        Args:
            class_name (str): Nome da classe
            
        Returns:
            int: Profundidade na árvore de herança
        """
        visited = set()
        def depth(cls):
            """Função auxiliar recursiva para calcular profundidade."""
            if cls not in self.classes or cls in visited:
                return 0
            visited.add(cls)
            bases = self.classes[cls].base_classes
            return 1 + max((depth(base) for base in bases), default=0)
        return depth(class_name)

    def _compute_cbo(self, cls):
        """
        Calcula o acoplamento entre objetos (CBO).
        
        Args:
            cls (ClassInfo): Informações da classe
            
        Returns:
            int: Número de acoplamentos externos
        """
        external_calls = 0
        for call in cls.calls:
            for other_cls in self.classes.values():
                if other_cls.name != cls.name and call in other_cls.methods:
                    external_calls += 1
                    break
        return external_calls

    def _compute_lcom(self, cls):
        """
        Calcula a falta de coesão entre métodos (LCOM).
        
        Args:
            cls (ClassInfo): Informações da classe
            
        Returns:
            int: Número de pares de métodos que não compartilham atributos
        """
        method_attr = []
        for method in cls.methods:
            accessed = set()
            for call in cls.calls:
                if method in call:
                    accessed.update(cls.attributes)
            method_attr.append(accessed)
        pairs = [(a, b) for i, a in enumerate(method_attr) for b in method_attr[i+1:]]
        no_shared = sum(1 for a, b in pairs if a.isdisjoint(b))
        return no_shared

def do_ck_analysis_file(filepath: str) -> dict:
    """
    Realiza análise de métricas C&K em um arquivo Python.
    
    Args:
        filepath: Caminho para o arquivo Python a ser analisado
        
    Returns:
        dict: Métricas C&K para todas as classes encontradas no arquivo
        
    Raises:
        FileNotFoundError: Se o arquivo não for encontrado
        SyntaxError: Se o arquivo contém código Python inválido
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()

    tree = ast.parse(code)
    analyzer = CKAnalyzer()
    analyzer.visit(tree)
    analyzer.build_hierarchy()
    metrics = analyzer.compute_metrics()
    return metrics

def get_ck_metrics(path: str) -> dict:
    """
    Calcula métricas Chidamber & Kemerer para todos os arquivos Python em um diretório.
    
    Args:
        path: Caminho para o diretório a ser analisado
        
    Returns:
        dict: Métricas C&K organizadas por arquivo e classe
              Formato: {arquivo: {classe: {métrica: valor}}}
              
    Note:
        Arquivos com erros de sintaxe são ignorados e o erro é reportado
    """
    results = {}
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.py'):
                fullpath = os.path.join(root, file)
                try:
                    metrics = do_ck_analysis_file(fullpath)
                    results[fullpath] = metrics
                except Exception as e:
                    print(f"Error in {fullpath}: {e}")
    return results

# =============================================================================
# Raw and Halstead Metrics Analysis
# =============================================================================

def get_code_metrics(file_path: str) -> dict:
    """
    Calcula várias métricas de qualidade de software (RAW e Halstead) para um arquivo Python.
    
    Args:
        file_path: Caminho para o arquivo Python a ser analisado
        
    Returns:
        dict: Dicionário com métricas do arquivo:
            - loc: Total de linhas de código
            - lloc: Linhas lógicas de código
            - sloc: Linhas de código fonte
            - comments: Número de comentários
            - multi: Número de strings multilinha
            - blank: Número de linhas em branco
            - average_complexity: Complexidade ciclomática média
            - maintainability_index: Índice de manutenibilidade
            
    Returns:
        None: Em caso de erro na análise
    """
    try:
        with open(file_path, 'r') as file:
            code = file.read()
            
        # Calculate raw metrics
        raw_metrics = raw.analyze(code)
        
        # Calculate cyclomatic complexity
        cc = complexity.cc_visit(code)
        avg_cc = sum(item.complexity for item in cc) / len(cc) if cc else 0
        
        # Calculate Halstead metrics
        hal_metrics = metrics.h_visit(code)
        
        metrics_report = {
            'loc': raw_metrics.loc,  # Lines of code
            'lloc': raw_metrics.lloc,  # Logical lines of code
            'sloc': raw_metrics.sloc,  # Source lines of code
            'comments': raw_metrics.comments,  # Number of comments
            'multi': raw_metrics.multi,  # Number of multi-line strings
            'blank': raw_metrics.blank,  # Number of blank lines
            'average_complexity': avg_cc,  # Average cyclomatic complexity
            'maintainability_index': metrics.mi_visit(code, multi=True),  # Maintainability index
        }
        
        return metrics_report
        
    except Exception as e:
        print(f"Error calculating metrics: {str(e)}")
        return None

def get_project_metrics(project_path: str) -> dict:
    """
    Analisa métricas para todos os arquivos Python em um projeto.
    
    Args:
        project_path: Caminho para o diretório do projeto
        
    Returns:
        dict: Métricas organizadas por arquivo
              Formato: {caminho_arquivo: {métrica: valor}}
              
    Note:
        Apenas arquivos .py são processados. Arquivos com erro são ignorados.
    """
    all_metrics = {}
    
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                metrics = get_code_metrics(file_path)
                if metrics:
                    all_metrics[file_path] = metrics
    
    return all_metrics


def get_project_statistics(metrics_report: dict, revision_id: str) -> dict:
    """
    Gera estatísticas agregadas a partir de um relatório de métricas por arquivo.

    Args:
        metrics_report (dict[str, dict[str, int | float]]): 
            Um dicionário cujo keys são nomes de arquivos e values são dicionários contendo
            as seguintes métricas por arquivo:
                - loc (int): linhas de código totais
                - lloc (int): linhas lógicas de código
                - sloc (int): linhas de código fonte
                - comments (int): linhas de comentário
                - multi (int): linhas de comentário multilinha
                - blank (int): linhas em branco
                - average_complexity (float): complexidade ciclomática média
                - maintainability_index (float): índice de manutenibilidade

    Returns:
        dict[str, int | float]: Um dicionário com as estatísticas gerais do projeto:
            - revision_id: identificador de revisão
            - total_loc (int): soma de todas as linhas de código
            - total_lloc (int): soma de todas as linhas lógicas de código
            - total_sloc (int): soma de todas as linhas de código fonte
            - total_comments (int): soma de todas as linhas de comentário
            - total_multi (int): soma de todas as linhas de comentário multilinha
            - total_blank (int): soma de todas as linhas em branco
            - n_files (int): número de arquivos processados
            - mean_maintainability_index (float): índice médio de manutenibilidade
            - mean_complexity (float): complexidade média
    """
    include_files = False
    # Inicialização de contadores
    totals = {
        'loc': 0, 'lloc': 0, 'sloc': 0, 'comments': 0,
        'multi': 0, 'blank': 0, 'complexity': 0, 'maintainability_index': 0
    }
    n_files = 0

    # Soma de todos os valores
    for fname, stat in metrics_report.items():
        totals['loc'] += stat['loc']
        totals['lloc'] += stat['lloc']
        totals['sloc'] += stat['sloc']
        totals['comments'] += stat['comments']
        totals['multi'] += stat['multi']
        totals['blank'] += stat['blank']
        totals['complexity'] += stat['average_complexity']
        totals['maintainability_index'] += stat['maintainability_index']
        n_files += 1

    # Calcula médias (evita divisão por zero)
    if n_files > 0:
        mean_maintainability = totals['maintainability_index'] / n_files
        mean_complexity = totals['complexity'] / n_files
    else:
        mean_maintainability = mean_complexity = 0

    # Monta dicionário de estatísticas
    statistics = {
        'revision_id': revision_id,
        'total_loc': totals['loc'],
        'total_lloc': totals['lloc'],
        'total_sloc': totals['sloc'],
        'total_comments': totals['comments'],
        'total_multi': totals['multi'],
        'total_blank': totals['blank'],
        'n_files': n_files,
        'mean_maintainability_index': mean_maintainability,
        'mean_complexity': mean_complexity,
    }
    
    # Futura implementação: adicionar arquivos com qualidade abaixo da média
    if include_files:
        # TODO: Implementar lógica para identificar arquivos problemáticos
        pass

    return statistics     