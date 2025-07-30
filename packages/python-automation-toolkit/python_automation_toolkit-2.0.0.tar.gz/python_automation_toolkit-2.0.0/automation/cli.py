import click
import json
import os
from rich.console import Console
from automation.logger import logger
from automation.file_tools import create_file, delete_file, move_file
from automation.linux_tools import run_shell_command
from automation.github_tools import list_repos
from automation.api_tools import call_api
from automation.scheduler import load_jobs_from_config, schedule_job, start_scheduler

console = Console()

def load_json(value):
    """
    Load JSON from string or @file.json
    Auto-fixes BOM/UTF-16 issues.
    """
    if value and value.startswith('@'):
        file_path = value[1:]
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    return json.load(f)
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='utf-16') as f:
                    return json.load(f)
        else:
            raise FileNotFoundError(f"JSON file not found: {file_path}")
    elif value:
        return json.loads(value)
    return None

@click.group()
def main():
    """💻 Python Automation Toolkit CLI"""
    logger.info("Automation Toolkit CLI started")
    console.print("[bold green]🚀 Python Automation Toolkit CLI Ready[/bold green]")

# --------------------------
# 📂 File Automation Commands
# --------------------------
@main.command()
@click.argument('file_name')
def touch(file_name):
    """Create an empty file"""
    create_file(file_name)

@main.command()
@click.argument('file_name')
def rm(file_name):
    """Delete a file"""
    delete_file(file_name)

@main.command()
@click.argument('src')
@click.argument('dst')
def mv(src, dst):
    """Move a file"""
    move_file(src, dst)

# --------------------------
# 🖱 Shell Commands
# --------------------------
@main.command()
@click.argument('command')
def shell(command):
    """Run a shell command (Windows/Linux auto-detect)"""
    run_shell_command(command)

# --------------------------
# 🔗 GitHub API Commands
# --------------------------
@main.command()
@click.argument('username')
@click.option('--token', help='GitHub Personal Access Token')
def github(username, token):
    """List GitHub repos for a user"""
    list_repos(username, token)

# --------------------------
# 🌐 REST API Commands
# --------------------------
@main.command()
@click.argument('url')
@click.option('--method', default='GET', help='HTTP method (GET, POST, PUT, DELETE)')
@click.option('--headers', default=None, help='Request headers as JSON string or @file.json')
@click.option('--data', default=None, help='Request body as JSON string or @file.json')
def api(url, method, headers, data):
    """Call a REST API"""
    try:
        headers = load_json(headers)
        data = load_json(data)
        call_api(url, method, headers, data)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {e}")
        console.print(f"[bold red]❌ Invalid JSON:[/bold red] {e}")
    except Exception as e:
        logger.error(f"API command failed: {e}")
        console.print(f"[bold red]❌ Error:[/bold red] {e}")

# --------------------------
# ⛓ Chain Commands
# --------------------------
@main.command()
@click.argument('commands', nargs=-1)
def chain(commands):
    """Run multiple commands in sequence"""
    logger.info(f"Running chained commands: {commands}")
    for cmd in commands:
        run_shell_command(cmd)

# --------------------------
# ⏲ Cron-Like Scheduling
# --------------------------
@main.command()
@click.argument('interval', type=int)
@click.argument('command')
def cron(interval, command):
    """Run a command every X seconds"""
    logger.info(f"Scheduling '{command}' every {interval} seconds")
    schedule_job(interval, command)
    start_scheduler()

@main.command()
@click.argument('config_file')
def schedule(config_file):
    """Load scheduled jobs from JSON config file"""
    logger.info(f"Loading jobs from {config_file}")
    jobs = load_jobs_from_config(config_file)
    for job in jobs:
        schedule_job(job['interval'], job['command'])
    start_scheduler()