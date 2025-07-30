import click
from pyops.system_monitor import show_system_info
from pyops.git_tools import clone_repo, git_status, git_pull, git_push, list_branches_and_commits
from pyops.api_tools import fetch_api_data
from pyops.linux_tools import (
    list_files, make_directory, remove_file_or_dir, create_empty_file,
    show_current_user, show_uptime
)
from pyops.logger import logger

@click.group()
def main():
    """PyOps CLI Toolkit"""
    logger.info("PyOps CLI started")

# Existing commands
@main.command()
def system():
    """Show system information (CPU, Memory, Disk)"""
    show_system_info()

@main.command()
@click.argument('repo_url')
def clone(repo_url):
    """Clone a Git repository"""
    clone_repo(repo_url)

@main.command()
def status():
    """Show Git status"""
    git_status()

@main.command()
def pull():
    """Pull latest changes from Git repository"""
    git_pull()

@main.command()
def push():
    """Push changes to remote Git repository"""
    git_push()

@main.command()
def list():
    """List branches and recent commits"""
    list_branches_and_commits()

@main.command()
@click.argument('url')
def api(url):
    """Fetch data from an external API"""
    fetch_api_data(url)

# New Linux commands
@main.command()
def ls():
    """List files in the current directory"""
    list_files()

@main.command()
@click.argument('dir_name')
def mkdir(dir_name):
    """Create a new directory"""
    make_directory(dir_name)

@main.command()
@click.argument('target')
def rm(target):
    """Remove a file or directory"""
    remove_file_or_dir(target)

@main.command()
@click.argument('file_name')
def touch(file_name):
    """Create an empty file"""
    create_empty_file(file_name)

@main.command()
def whoami():
    """Show the current user"""
    show_current_user()

@main.command()
def uptime():
    """Show system uptime"""
    show_uptime()