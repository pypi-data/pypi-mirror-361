import requests
from shared.logger import setup_logger
logger = setup_logger(__name__)

def request_with_retry(url, method='GET', headers=None, data=None, retries=3):
    for i in range(retries):
        try:
            response = requests.request(method, url, headers=headers, json=data, timeout=3)
            return response
        except requests.RequestException as e:
            logger.warning(f"Attempt {i+1} failed: {e}")
    raise Exception(f"Failed to call {url} after {retries} retries")
