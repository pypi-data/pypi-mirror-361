import subprocess
from pyops.logger import logger

def run_command(command):
    """Run a Linux shell command and print output."""
    logger.info(f"Running command: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        logger.info(f"Command output: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr.strip()}")
        print(f"❌ Error: {e.stderr.strip()}")

def list_files():
    run_command("ls -lah")

def make_directory(dir_name):
    run_command(f"mkdir -p {dir_name}")

def remove_file_or_dir(target):
    run_command(f"rm -rf {target}")

def create_empty_file(file_name):
    run_command(f"touch {file_name}")

def show_current_user():
    run_command("whoami")

def show_uptime():
    run_command("uptime")