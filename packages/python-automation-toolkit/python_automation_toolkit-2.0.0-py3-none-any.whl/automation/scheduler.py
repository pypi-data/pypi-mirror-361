import schedule
import time
import json
from automation.logger import logger
from automation.linux_tools import run_shell_command
from rich.console import Console

console = Console()

def run_job(command):
    logger.info(f"Running scheduled job: {command}")
    run_shell_command(command)

def schedule_job(interval, command):
    logger.info(f"Scheduling job every {interval} seconds: {command}")
    schedule.every(interval).seconds.do(run_job, command)

def load_jobs_from_config(config_file):
    try:
        with open(config_file, 'r') as f:
            jobs = json.load(f)
        logger.info(f"Loaded {len(jobs)} jobs from {config_file}")
        return jobs
    except Exception as e:
        logger.error(f"Failed to load jobs from config: {e}")
        console.print(f"[bold red]❌ Error loading jobs:[/bold red] {e}")
        return []

def start_scheduler():
    logger.info("Starting scheduler")
    console.print("[bold green]📅 Scheduler started[/bold green]")
    while True:
        schedule.run_pending()
        time.sleep(1)