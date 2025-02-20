import streamlit as st
import requests
import json
import os

# Load Configurations (Environment Variables for Security)
BASE_URL = os.getenv("BASE_URL", "https://your-alation-instance.alationcloud.com")
API_TOKEN = os.getenv("API_TOKEN")  # Securely load from environment variable

HEADERS = {'Token': API_TOKEN}

st.title("📄 Alation Document Retriever")

# Input field for Document ID
doc_id = st.text_input("Enter Document ID:", "")

if st.button("Fetch Document Info"):
    if not doc_id:
        st.warning("⚠️ Please enter a Document ID.")
    else:
        try:
            response = requests.get(
                f"{BASE_URL}/integration/v2/document/", headers=HEADERS, params={'id': doc_id}
            )
            response.raise_for_status()
            data = response.json()
            st.json(data)  # Display response in a readable format
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error fetching document {doc_id}: {e}")
