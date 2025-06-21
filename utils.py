import os
import subprocess

from datetime import datetime
from git import Repo
from decouple import config
from pathlib import Path
from typing import Union

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLONE_BASE_PATH = config('CLONE_REPOS_BASE')

def clone_repo(repos_to_clone: dict) -> bool:
    """
    Clona repositórios do GitHub.
    
    Args:
        repos_to_clone: Dict com formato {"owner": "repo_name"}
        
    Returns:
        bool: True se todos os repos foram clonados com sucesso
    """
    success = True
    
    for owner, repo_name in repos_to_clone.items():
        try:
            github_endpoint = f"https://github.com/{owner}/{repo_name}.git"
            clone_path = os.path.join(CLONE_BASE_PATH, owner, repo_name)
            
            print(f"Clonando {github_endpoint} para {clone_path}")
            Repo.clone_from(github_endpoint, clone_path)
            
            # Salva a revisão atual
            revisions = get_git_revisions(clone_path)
            if revisions:
                save_current_revision_repo(clone_path, revisions[0])
            else:
                print(f"Aviso: Não foi possível obter revisões para {owner}/{repo_name}")
                
        except Exception as e:
            print(f"Erro ao clonar {owner}/{repo_name}: {e}")
            success = False
            
    return success

def listar_repos_clonados() -> list:
    """
    Lista todos os repositórios clonados no diretório base.
    
    Busca recursivamente por estruturas de diretório no formato 'owner/repo'
    dentro do caminho base definido pela variável CLONE_BASE_PATH.
    
    Returns:
        list: Lista de strings no formato 'owner/repo' dos repositórios encontrados
        
    Example:
        Estrutura de diretórios:
        clones/
        ├── ccxt/
        │    └── ccxt/
        └── huggingface/
             └── transformers/
        
        Retorno: ['ccxt/ccxt', 'huggingface/transformers']
        
    Note:
        Utiliza a variável global CLONE_BASE_PATH como diretório base
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
            
def get_git_revisions(repo_path: str, n: int = 100) -> list:
    """
    Obtém as últimas n revisões de um repositório git.
    
    Args:
        repo_path: Caminho para o repositório git local
        n: Número de revisões para recuperar
        
    Returns:
        list: Lista de hashes de commit, ou lista vazia em caso de erro
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
            print(f"Erro ao obter revisões: {result.stderr}")
            return []
            
    except Exception as e:
        print(f"Erro ao recuperar histórico do git: {str(e)}")
        return []

def checkout_git_revision(repo_path: str, revision: str) -> bool:
    """
    Faz checkout de uma revisão específica de um repositório git local.
    
    Args:
        repo_path: Caminho para o repositório git local
        revision: Revisão git (hash do commit, nome da branch, ou tag)
        
    Returns:
        bool: True se o checkout foi bem-sucedido, False caso contrário
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
            print(f"Erro no checkout da revisão: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Erro durante checkout do git: {str(e)}")
        return False
    
def save_current_revision_repo(repo_path: str, revision: str) -> None:
    """
    Salva a revisão atual do repositório em arquivo de configuração.
    
    Args:
        repo_path: Caminho para o diretório do repositório
        revision: Hash da revisão ou identificador do commit
        
    Note:
        Cria arquivo no formato: <BASE_DIR>/current/<nome_do_repo>.ciconf
        O diretório 'current' é criado automaticamente se não existir
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
        
def copy_project_head(repo_path: str) -> None:
    """
    Copia a revisão HEAD atual do repositório para arquivo de configuração.
    
    Args:
        repo_path: Caminho para o diretório do repositório git
        
    Note:
        Lê diretamente o arquivo .git/HEAD e salva usando save_current_revision_repo()
    """
    with open(f"{repo_path}/.git/HEAD", 'r') as handler:
        current_revision = handler.read()
    save_current_revision_repo(repo_path, current_revision)
          
def get_project_checkout_version(project_name: str) -> str:
    """
    Obtém a versão atual do checkout do projeto.
    
    Args:
        project_name: Nome do projeto (usado como nome do arquivo de configuração)
        
    Returns:
        str: Hash da revisão atual, ou string vazia em caso de erro
        
    Note:
        Lê arquivo current/{project_name}.ciconf criado por save_current_revision_repo()
    """
    try:
        with open(f"current/{project_name}.ciconf", 'r') as handler:
            return handler.read().strip()
    except FileNotFoundError:
        print(f"Arquivo de configuração não encontrado para {project_name}")
        return ""
    except Exception as e:
        print(f"Erro ao ler versão do checkout: {e}")
        return ""
    
# =============================================================================
# Classes para pipeline futuro
# =============================================================================

class Clone:
    """Classe para clonagem de repositórios."""
    
    def __init__(self, user: str, repository: str):
        """
        Args:
            user: nome do usuário/org no GitHub
            repository: nome do repositório
        """
        self.user = user
        self.repository = repository

    def run(self, work_dir: str) -> bool:
        """
        Clona o repo em work_dir. Se já existir, pula.
        
        Args:
            work_dir: Diretório de trabalho
            
        Returns:
            bool: True se a operação foi bem-sucedida
        """
        target = os.path.join(work_dir, self.repository)
        repo_dict = {self.user: self.repository}

        if not os.path.isdir(target):
            print(f"[Clone] clonando https://github.com/{self.user}/{self.repository}.git → {target}")
            return clone_repo(repo_dict)
        else:
            print(f"[Clone] {target} já existe, pulando clone")
            return True

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
    
    Args:
        repo_path: Caminho para o diretório do repositório Git
        date: Data/hora como datetime ou string no formato reconhecido pelo Git
             Ex: '2025-06-19 14:30:00', '2025-06-19T14:30:00'
        branch: Branch onde buscar o commit (padrão: 'master')
        
    Returns:
        str: Hash do commit encontrado
        
    Raises:
        ValueError: Se não houver commit até a data especificada
        RuntimeError: Se o comando Git falhar
        
    Note:
        Utiliza o comando 'git rev-list --before' para encontrar o commit
    """
    # Converte datetime para string compatível com git
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
    