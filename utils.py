import os
import subprocess

from datetime import datetime
from git import Repo
from decouple import config
from pathlib import Path
from typing import Union

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLONE_BASE_PATH = config('CLONE_REPOS_BASE')

def clone_repo(reposToClone):
    for key, value in reposToClone.items():
        github_endpoint = "https://github.com/{}/{}.git".format(key, value)
        Repo.clone_from(github_endpoint, "{}/{}/{}/".format(CLONE_BASE_PATH, key, value))
        
        revisions = get_git_revisions("{}/{}/{}/".format(CLONE_BASE_PATH, key, value))
        save_current_revision_repo("{}/{}/{}/".format(CLONE_BASE_PATH, key, value), revisions[0])

def listar_repos_clonados() -> list:
    """
    Busca em 'caminho' os diretórios e, para cada um, suas subpastas imediatas.
    Retorna uma lista com a formatação 'diretório/subdiretório'.
    
    Exemplo:
    - clones/
       ├── ccxt/
       │    └── ccxt/
       └── huggingface/
            └── transformers/
    
    Retorno: ['ccxt/ccxt', 'huggingface/transformers']
    """
    
    caminho = CLONE_BASE_PATH
    
    resultado = []
    p = Path(caminho)
    
    # Itera sobre cada diretório em 'caminho'
    for diretorio in p.iterdir():
        if diretorio.is_dir():
            # Itera sobre as subpastas imediatas dentro do diretório
            for subdiretorio in diretorio.iterdir():
                if subdiretorio.is_dir():
                    resultado.append(f"{diretorio.name}/{subdiretorio.name}")
    return resultado
            
def get_git_revisions(repo_path, n=100):
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
                
        # Run git checkout command
        result = subprocess.run(['git', 'checkout', revision], 
                              capture_output=True,
                              text=True)
        
        # Change back to original directory
        os.chdir(original_dir)
        
        if result.returncode == 0:
            save_current_revision_repo(repo_path, revision)
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
    
# Implementação futura do pipeline

class Clone:
    def __init__(self, user: str, repository: str):
        """
        user: nome do usuário/org no GitHub
        repository: nome do repositório
        """
        self.user = user
        self.repository = repository

    def run(self, work_dir: str):
        """
        Clona o repo em work_dir. Se já existir, pula.
        """
        target = os.path.join(work_dir, self.repository)
        repo_dict = {self.user: self.repository}

        if not os.path.isdir(target):
            print(f"[Clone] clonando https://github.com/{self.user}/{self.repository}.git → {target}")
            utils.clone_repo(repo_dict, work_dir)
        else:
            print(f"[Clone] {target} já existe, pulando clone")

import subprocess
from datetime import datetime
from typing import Union

def get_commit_hash_by_date(
    repo_path: str,
    date: Union[str, datetime],
    branch: str = "master"
) -> str:
    """
    Retorna o hash do último commit anterior ou igual à data fornecida.

    :param repo_path: caminho para o diretório do repositório Git.
    :param date: data/hora (datetime ou string no formato reconhecido pelo Git,
                 ex: '2025-06-19 14:30:00' ou ISO '2025-06-19T14:30:00').
    :param branch: branch onde buscar o commit (padrão: 'master').
    :return: string com o hash do commit encontrado.
    :raises ValueError: se não houver commit até aquela data.
    :raises RuntimeError: se o comando Git falhar.
    """
    # converte datetime em string compatível
    if isinstance(date, datetime):
        date_str = date.strftime("%Y-%m-%d %H:%M:%S")
    else:
        date_str = date

    cmd = [
        "git", "-C", repo_path,
        "rev-list", "-1",
        f"--before={date_str}",
        branch
    ]
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Erro ao executar Git: {e.stderr.strip()}") from e

    commit_hash = proc.stdout.strip()
    if not commit_hash:
        raise ValueError(f"Nenhum commit encontrado até {date_str} em {branch}")
    return commit_hash
    