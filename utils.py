import os
import subprocess

from git import Repo
from decouple import config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLONE_BASE_PATH = config('CLONE_REPOS_BASE')

def clone_repo(reposToClone):
    for key, value in reposToClone.items():
        github_endpoint = "https://github.com/{}/{}.git".format(key, value)
        Repo.clone_from(github_endpoint, "{}/{}/{}/".format(CLONE_BASE_PATH, key, value))
        
        revisions = get_git_revisions("{}/{}/{}/".format(CLONE_BASE_PATH, key, value))
        save_current_revision_repo("{}/{}/{}/".format(CLONE_BASE_PATH, key, value), revisions[0])        
        
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
        
        # TODO: Consertar esta função
        save_current_revision_repo(repo_path, revision)
                
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
    
def save_current_revision_repo(repo_path: str, revision: str) -> None:
    """
    Salva a revisão informada (hash identificador) num arquivo:
        <BASE_DIR>/current/<nome_do_repo>.ciconf
    """
    # Extrai só o nome da pasta final do repo_path
    repo_name = os.path.basename(os.path.normpath(repo_path))

    # (2) Monta o heads_dir junto ao script principal
    heads_dir = os.path.join(BASE_DIR, "current")
    os.makedirs(heads_dir, exist_ok=True)

    # (3) Gera o caminho completo do arquivo
    file_path = os.path.join(heads_dir, f"{repo_name}.ciconf")

    # (4) Escreve a revisão
    with open(file_path, "w", encoding="utf-8") as handler:
        handler.write(revision)
        
def copy_project_head(repo_path):
    with open(f"{repo_path}/.git/HEAD", 'r') as HANDLER:
        current_revision = HANDLER.read()
    save_current_revision_repo(repo_path, current_revision)
          
def get_project_checkout_version(project_name):
    with open(f"current/{project_name}.ciconf", 'r') as HANDLER:
        hash = HANDLER.read()
        return hash
    
    