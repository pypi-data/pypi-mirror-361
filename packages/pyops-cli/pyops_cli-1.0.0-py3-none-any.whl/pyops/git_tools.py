from git import Repo
from pyops.logger import logger
import os

def clone_repo(repo_url):
    logger.info(f"Cloning repository: {repo_url}")
    try:
        Repo.clone_from(repo_url, os.path.basename(repo_url).replace('.git', ''))
        logger.info("Repository cloned successfully.")
        print("✅ Repository cloned successfully.")
    except Exception as e:
        logger.error(f"Failed to clone repository: {e}")
        print(f"❌ Error: {e}")

def git_status():
    logger.info("Checking Git status...")
    try:
        repo = Repo(os.getcwd())
        print(repo.git.status())
        logger.info("Git status fetched.")
    except Exception as e:
        logger.error(f"Git status failed: {e}")
        print(f"❌ Error: {e}")

def git_pull():
    logger.info("Performing git pull...")
    try:
        repo = Repo(os.getcwd())
        print(repo.git.pull())
        logger.info("Git pull completed.")
    except Exception as e:
        logger.error(f"Git pull failed: {e}")
        print(f"❌ Error: {e}")

def git_push():
    logger.info("Performing git push...")
    try:
        repo = Repo(os.getcwd())
        print(repo.git.push())
        logger.info("Git push completed.")
    except Exception as e:
        logger.error(f"Git push failed: {e}")
        print(f"❌ Error: {e}")

def list_branches_and_commits():
    logger.info("Listing branches and recent commits...")
    try:
        repo = Repo(os.getcwd())
        print("\nBranches:")
        for branch in repo.branches:
            print(f" - {branch}")

        print("\nRecent Commits:")
        for commit in repo.iter_commits(max_count=5):
            print(f"{commit.hexsha[:7]} {commit.message.strip()} by {commit.author.name}")
        logger.info("Branches and commits listed.")
    except Exception as e:
        logger.error(f"Listing branches and commits failed: {e}")
        print(f"❌ Error: {e}")