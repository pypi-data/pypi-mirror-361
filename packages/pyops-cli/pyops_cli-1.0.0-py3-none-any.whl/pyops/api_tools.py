import requests
import json
from pyops.logger import logger

def fetch_api_data(url):
    logger.info(f"Fetching API data from: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        pretty_data = json.dumps(data, indent=4)
        print(pretty_data)
        logger.info("API data fetched successfully.")
    except Exception as e:
        logger.error(f"API fetch failed: {e}")
        print(f"❌ Error: {e}")