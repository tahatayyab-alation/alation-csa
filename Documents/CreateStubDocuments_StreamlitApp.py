import streamlit as st
import requests
import json
import time
from urllib.parse import urlencode

st.title("📄 Alation Stub Document Creator")

# Sidebar - API Configuration
st.sidebar.header("🔧 API Configuration")
base_url = st.sidebar.text_input("🔗 Alation BASE URL", "https://your-instance.alationcloud.com")
api_token = st.sidebar.text_input("🔑 API Token", type="password")

# Sidebar - Document Parameters
st.sidebar.header("📂 Document Settings")
document_hub_id = st.sidebar.number_input("📄 Document Hub ID", value=7, min_value=1)
template_id = st.sidebar.number_input("📝 Template ID", value=72, min_value=1)
parent_folder_id = st.sidebar.number_input("📂 Parent Folder ID", value=57, min_value=1)
nav_link_folder_ids = st.sidebar.text_input("🔗 Navigation Folder IDs (comma-separated)", "58, 59")
num_stub_docs = st.sidebar.number_input("📑 Number of Stub Documents", value=3, min_value=1)
max_retries = st.sidebar.number_input("🔄 Max Retries for Job Polling", value=100, min_value=1)

# Convert nav_link_folder_ids from string to list
nav_link_folder_ids = [int(x.strip()) for x in nav_link_folder_ids.split(",") if x.strip().isdigit()]

# 📌 Add Usage Notice in Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown(
    "⚠️ **Notice of Usage, Rights, and Alation Responsibility:**\n"
    "This code is provided **as-is** with no expressed or implied warranty or support.\n"
    "Alation is **not responsible** for its modification, use, or maintenance."
)

def create_stub_documents():
    """Creates stub documents and returns the job ID."""
    headers = {'Token': api_token}
    payload = [
        {
            "title": f"Stub Document ({i+1} of {num_stub_docs})",
            "document_hub_id": document_hub_id,
            "template_id": template_id,
            "parent_folder_id": parent_folder_id,
            "nav_link_folder_ids": nav_link_folder_ids
        }
        for i in range(num_stub_docs)
    ]

    try:
        response = requests.post(f"{base_url}/integration/v2/document/", headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()
        
        if "job_id" in response_data:
            st.success(f"✅ Stub documents submitted successfully. Job ID: {response_data['job_id']}")
            return response_data["job_id"]
        else:
            st.error("❌ API response does not contain a job ID.")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to create stub documents: {e}")
        return None

def get_job_output(job_id):
    """Polls the job API until completion or failure."""
    url = f"{base_url}/api/v1/bulk_metadata/job/?" + urlencode({'id': job_id})
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers={'Token': api_token})
            response.raise_for_status()
            response_json = response.json()

            job_status = response_json.get("status", "unknown")

            if job_status == "running":
                st.write(f"⏳ Job {job_id} is still running... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(10)
            else:
                st.success(f"✅ Job {job_id} completed with status: {job_status}")
                return response_json

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error checking job status: {e}")
            break

    st.error(f"❌ Job {job_id} did not complete within {max_retries} attempts. You may continue to monitor at {base_url}/monitor/active_tasks/.")
    return None

if st.button("🚀 Create Stub Documents"):
    if not api_token:
        st.error("❌ API token is required.")
    else:
        job_id = create_stub_documents()
        if job_id:
            job_response = get_job_output(job_id)
            if job_response:
                st.json(job_response)
