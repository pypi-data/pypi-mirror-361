import psutil
from pyops.logger import logger

def show_system_info():
    logger.info("Fetching system information...")
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    print(f"CPU Usage: {cpu}%")
    print(f"Memory Usage: {memory.percent}%")
    print(f"Disk Usage: {disk.percent}%")

    logger.info(f"CPU: {cpu}%, Memory: {memory.percent}%, Disk: {disk.percent}%")

    if disk.percent > 80:
        warning = f"⚠️ WARNING: Disk usage at {disk.percent}%!"
        print(warning)
        logger.warning(warning)