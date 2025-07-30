import requests
from automation.logger import logger

def list_repos(username, token=None):
    logger.info(f"Fetching GitHub repos for user: {username}")
    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'
    try:
        url = f"https://api.github.com/users/{username}/repos"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        repos = response.json()
        for repo in repos:
            private = "🔒" if repo['private'] else "🌐"
            print(f"{private} {repo['name']}")
        logger.info("GitHub repos fetched successfully")
    except Exception as e:
        logger.error(f"Failed to fetch repos: {e}")
        print(f"❌ Error: {e}")