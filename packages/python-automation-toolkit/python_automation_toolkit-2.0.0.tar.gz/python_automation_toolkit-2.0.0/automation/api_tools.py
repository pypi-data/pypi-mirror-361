import requests
from automation.logger import logger

def call_api(url, method, headers=None, data=None):
    logger.info(f"Calling API: {method} {url}")
    try:
        response = requests.request(method, url, headers=headers, json=data)
        print(response.text)
        logger.info(f"API response: {response.status_code}")
    except Exception as e:
        logger.error(f"API call failed: {e}")
        print(f"❌ Error: {e}")