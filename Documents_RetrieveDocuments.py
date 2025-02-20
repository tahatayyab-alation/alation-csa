import requests
import json
import os
import argparse

# Load Configurations
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

BASE_URL = os.getenv("BASE_URL", config["BASE_URL"])
API_TOKEN = os.getenv("API_TOKEN")  # Securely load from environment variable
HEADERS = {'Token': API_TOKEN}

def print_doc_info(doc_id):
    """Fetch and print document details from Alation API."""
    try:
        response = requests.get(f"{BASE_URL}/integration/v2/document/", headers=HEADERS, params={'id': doc_id})
        response.raise_for_status()
        print(json.dumps(response.json(), indent=4))
    except requests.exceptions.RequestException as e:
        print(f"Error fetching document {doc_id}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch Alation Document Information")
    parser.add_argument("doc_id", type=int, help="Document ID to fetch details")

    args = parser.parse_args()

    print_doc_info(args.doc_id)