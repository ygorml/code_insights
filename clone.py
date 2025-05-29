from decouple import config
from git import Repo

clone_base_path = config('CLONE_REPOS_BASE')

def clone_repo(reposToClone):
    for key, value in reposToClone.items():
        github_endpoint = "https://github.com/{}/{}.git".format(key, value)
        Repo.clone_from(github_endpoint, "{}/{}/".format(clone_base_path, value))