import requests
import json
import os
import argparse

def fetch_document_info(base_url, api_token, doc_id):
    """Fetch document details from Alation API."""
    headers = {'Token': api_token}
    
    try:
        response = requests.get(
            f"{base_url}/integration/v2/document/", headers=headers, params={'id': doc_id}
        )
        response.raise_for_status()
        return response.json()  # Return JSON response
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Allow command-line execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch Alation Document Information")
    parser.add_argument("base_url", type=str, help="Alation BASE URL")
    parser.add_argument("api_token", type=str, help="API Token")
    parser.add_argument("doc_id", type=int, help="Document ID to fetch details")

    args = parser.parse_args()

    result = fetch_document_info(args.base_url, args.api_token, args.doc_id)
    print(json.dumps(result, indent=4))
