from pydriller import Repository

# Python Metrics
import radon.metrics as metrics
import radon.complexity as complexity
import radon.raw as raw

# C++ Metrics
import lizard

import os
import subprocess

# Releases
import releasy

# Data - Repositories information
from data import repos

def get_releases_revision(project_path):
    pass

def get_code_metrics(file_path):
    """Calculate various software quality metrics for a Python file."""
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

def get_project_metrics(project_path):
    """Analyze metrics for all Python files in a project."""
    all_metrics = {}
    
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                metrics = get_code_metrics(file_path)
                if metrics:
                    all_metrics[file_path] = metrics
    
    return all_metrics

# Example usage:
# project_metrics = analyze_project_metrics('/path/to/your/project')
# for file_path, metrics in project_metrics.items():
#     print(f"\nMetrics for {file_path}:")
#     for metric, value in metrics.items():
#         print(f"{metric}: {value}")

def get_project_statistics(metrics_report):
    statistics = {}
    below_mean_maintainability = []
    above_mean_complexity    = []

    # inicialização de contadores
    total_loc = total_lloc = total_sloc = total_comments = total_multi = total_blank = 0
    total_complexity = total_maintainability_index = n_files = 0 

    # soma de todos os valores
    for fname, stat in metrics_report.items():
        total_loc                   += stat['loc']
        total_lloc                  += stat['lloc']
        total_sloc                  += stat['sloc']
        total_comments              += stat['comments']
        total_multi                 += stat['multi']
        total_blank                 += stat['blank']
        total_complexity            += stat['average_complexity']
        total_maintainability_index += stat['maintainability_index']
        n_files                     += 1

    # evita divisão por zero
    if n_files:
        mean_maintainability = total_maintainability_index / n_files
        mean_complexity      = total_complexity / n_files
    else:
        mean_maintainability = mean_complexity = 0

    # preenche o dicionário de estatísticas
    statistics.update({
        'revision_id': 0,
        'total_loc': total_loc,
        'total_lloc': total_lloc,
        'total_sloc': total_sloc,
        'total_comments': total_comments,
        'total_multi': total_multi,
        'total_blank': total_blank,
        'n_files': n_files,
        'mean_maintainability_index': mean_maintainability,
        'mean_complexity': mean_complexity,
    })

    # separa arquivos acima/abaixo da média
    for fname, stat in metrics_report.items():
        if stat['average_complexity'] > mean_complexity:
            above_mean_complexity.append(fname)
        if stat['maintainability_index'] < mean_maintainability:
            below_mean_maintainability.append(fname)

    statistics['above_mean_complexity']    = above_mean_complexity
    statistics['below_mean_maintainability'] = below_mean_maintainability

    return statistics
        
def checkout_git_revision(repo_path, revision):
    """
    Checkout a specific revision of a local git repository.
    
    Args:
        repo_path (str): Path to the local git repository
        revision (str): Git revision (commit hash, branch name, or tag)
        
    Returns:
        bool: True if checkout successful, False otherwise
    """
    try:
        # Change to repository directory
        original_dir = os.getcwd()
        os.chdir(repo_path)
        
        # Run git checkout command
        result = subprocess.run(['git', 'checkout', revision], 
                              capture_output=True,
                              text=True)
        
        # Change back to original directory
        os.chdir(original_dir)
        
        if result.returncode == 0:
            return True
        else:
            print(f"Error checking out revision: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error during git checkout: {str(e)}")
        return False

def get_git_revisions(repo_path, n=10):
    """
    Get the last n revisions of a git repository.
    
    Args:
        repo_path (str): Path to the local git repository
        n (int): Number of revisions to retrieve
        
    Returns:
        list: List of commit hashes, or empty list if error
    """
    try:
        # Change to repository directory
        original_dir = os.getcwd()
        os.chdir(repo_path)
        
        # Get commit hashes
        result = subprocess.run(['git', 'log', f'-{n}', '--pretty=format:%H'],
                              capture_output=True,
                              text=True)
                              
        # Change back to original directory
        os.chdir(original_dir)
        
        if result.returncode == 0:
            return result.stdout.split('\n')
        else:
            print(f"Error getting revisions: {result.stderr}")
            return []
            
    except Exception as e:
        print(f"Error retrieving git history: {str(e)}")
        return []