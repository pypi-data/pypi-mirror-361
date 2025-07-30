import subprocess
import platform
from automation.logger import logger
from rich.console import Console

console = Console()

def run_shell_command(command):
    logger.info(f"Running shell command: {command}")
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command, shell=True, check=True, executable='/bin/bash', capture_output=True, text=True)
        console.print(f"[bold cyan]{result.stdout.strip()}[/bold cyan]")
        logger.info(f"Command output: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr.strip()}")
        console.print(f"[bold red]❌ Error:[/bold red] {e.stderr.strip()}")