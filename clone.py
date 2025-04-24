from decouple import config
from git import Repo

def cloneRepo(reposToClone):
    for key, value in reposToClone.items():
        github_endpoint = "https://github.com/{}/{}.git".format(key, value)
        Repo.clone_from(github_endpoint, "clones/{}/".format(value))