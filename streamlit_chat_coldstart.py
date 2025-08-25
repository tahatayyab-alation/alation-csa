import streamlit as st
import requests
import shlex
import time
from datetime import datetime

# --- API Call Functions ---

def generate_curl_command(base_url, tenant_id, data_product_id, db, schema, if_exists, user_id, api_key):
    """Generates the cURL command string from user inputs."""
    # Clean inputs by stripping whitespace
    base_url = base_url.strip()
    tenant_id = tenant_id.strip()
    data_product_id = data_product_id.strip()
    db = db.strip()
    schema = schema.strip()
    user_id = user_id.strip()
    api_key = api_key.strip()
    
    url = (
        f"{base_url}/nsapi/api/v3/orgs/{tenant_id}/data_product/cold_start_from_data_product_id"
        f"?data_product_id={data_product_id}"
        f"&result_cache_database={db}"
        f"&result_cache_schema={schema}"
        f"&if_exists={if_exists}"
    )
    
    command_parts = [
        'curl', '-X', 'POST', shlex.quote(url),
        '-H', 'accept: application/json',
        '-H', f'alation-user-id: {shlex.quote(user_id)}',
        '-H', f'Authorization: AlationAPIKey {shlex.quote(api_key)}'
    ]
    return ' '.join(command_parts)

def execute_api_call(base_url, tenant_id, data_product_id, db, schema, if_exists, user_id, api_key):
    """Executes the initial Cold Start API call."""
    base_url = base_url.strip()
    tenant_id = tenant_id.strip()
    
    url = f"{base_url}/nsapi/api/v3/orgs/{tenant_id}/data_product/cold_start_from_data_product_id"
    headers = {
        'accept': 'application/json',
        'alation-user-id': user_id.strip(),
        'Authorization': f'AlationAPIKey {api_key.strip()}'
    }
    params = {
        'data_product_id': data_product_id.strip(),
        'result_cache_database': db.strip(),
        'result_cache_schema': schema.strip(),
        'if_exists': if_exists
    }
    
    try:
        response = requests.post(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return True, response, None
    except requests.exceptions.HTTPError as e:
        error_details = {"status_code": e.response.status_code, "reason": e.response.reason, "url": e.request.url}
        try:
            error_details["body"] = e.response.json()
        except ValueError:
            error_details["body"] = e.response.text
        return False, None, error_details
    except requests.exceptions.RequestException as e:
        return False, None, {"error_type": "Network Error", "message": str(e)}

def check_task_status(base_url, tenant_id, task_id, user_id, api_key):
    """Checks the status of a given task ID."""
    base_url = base_url.strip()
    tenant_id = tenant_id.strip()
    task_id = task_id.strip()

    # Note: Using the v1 tasks endpoint as per the user's example
    url = f"{base_url}/nsapi/api/v1/accounts/{tenant_id}/tasks/{task_id}"
    headers = {
        'accept': 'application/json',
        'alation-user-id': user_id.strip(),
        # Assuming the same authorization method is needed for the tasks endpoint
        'Authorization': f'AlationAPIKey {api_key.strip()}'
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return True, response.json(), None
    except requests.exceptions.HTTPError as e:
        error_details = {"status_code": e.response.status_code, "reason": e.response.reason, "url": e.request.url}
        try:
            error_details["body"] = e.response.json()
        except ValueError:
            error_details["body"] = e.response.text
        return False, None, error_details
    except requests.exceptions.RequestException as e:
        return False, None, {"error_type": "Network Error", "message": str(e)}

# --- Streamlit App UI ---

st.set_page_config(layout="wide", page_title="API Command Center")

# Initialize session state
if 'task_id' not in st.session_state:
    st.session_state.task_id = None

st.title("Chat with Data Products - Cold Start Utility 🐻‍❄️")
st.caption("Use this interface to build, preview, and execute your cold start request.")

# --- User Inputs ---
st.header("1. Enter Cold Start Request Details")

col1, col2 = st.columns(2)
with col1:
    base_url = st.text_input("Base URL", placeholder="https://your-alation-instance.com")
    tenant_id = st.text_input("Tenant ID (Account ID)", placeholder="e.g., 123e4567-e89b-12d3-a456-426614174000")
    data_product_id = st.text_input("Data Product ID", placeholder="e.g., my-data-product")
    if_exists = st.selectbox("If Exists Strategy", options=["error", "archive", "delete"], index=0)
with col2:
    result_cache_db = st.text_input("Result Cache Database", placeholder="e.g., PROD_DB")
    result_cache_schema = st.text_input("Result Cache Schema", placeholder="e.g., ANALYTICS")
    alation_user_id = st.text_input("Alation User ID", placeholder="e.g., 5")
    alation_api_key = st.text_input("Alation API Key", type="password", placeholder="Enter your API key")

all_fields_filled = all([base_url, tenant_id, data_product_id, result_cache_db, result_cache_schema, alation_user_id, alation_api_key, if_exists])
st.divider()

# --- Preview and Execute ---
st.header("2. Preview and Execute Cold Start")

preview_col, execute_col = st.columns(2)
with preview_col:
    if st.button("Preview Command", disabled=not all_fields_filled):
        curl_command = generate_curl_command(base_url, tenant_id, data_product_id, result_cache_db, result_cache_schema, if_exists, alation_user_id, alation_api_key)
        st.subheader("Generated cURL Command")
        st.code(curl_command, language="bash")
        st.info("You can copy the command above to use it in your terminal.")

with execute_col:
    if st.button("⚡ Execute API Call", type="primary", disabled=not all_fields_filled):
        st.session_state.task_id = None # Reset task ID on new execution
        with st.spinner("Sending request..."):
            success, response, error_details = execute_api_call(base_url, tenant_id, data_product_id, result_cache_db, result_cache_schema, if_exists, alation_user_id, alation_api_key)
        
        st.subheader("API Response")
        if success:
            response_json = response.json()
            st.success(f"Success! Status Code: {response.status_code}. Task submitted.")
            st.json(response_json)
            if 'id' in response_json:
                st.session_state.task_id = response_json['id']
                st.info(f"Task ID **{st.session_state.task_id}** has been captured. Proceed to Step 3 to track its progress.")
        else:
            st.error("API Call Failed!")
            # Display detailed error context
            if "status_code" in error_details:
                st.write(f"**Status Code:** `{error_details['status_code']} {error_details['reason']}`")
                st.write("**Server Response:**")
                if isinstance(error_details['body'], (dict, list)):
                    st.json(error_details['body'])
                else:
                    st.code(error_details['body'], language='text')
            else:
                st.write(f"**Error Type:** {error_details['error_type']}: {error_details['message']}")

if not all_fields_filled:
    st.warning("Please fill in all the fields to enable the Preview and Execute buttons.")

st.divider()

# --- Task Progress Tracking ---
if st.session_state.task_id:
    st.header("3. Track Task Progress")
    st.write(f"**Current Task ID:** `{st.session_state.task_id}`")

    if st.button("🔄 Track Task Progress", type="secondary"):
        status_placeholder = st.empty()
        
        POLLING_INTERVAL = 5 # seconds
        TERMINAL_STATUSES = ["SUCCESS", "FAILURE", "CANCELLED", "ERROR"]
        
        with st.spinner(f"Polling task status every {POLLING_INTERVAL} seconds..."):
            current_status = ""
            while current_status not in TERMINAL_STATUSES:
                success, task_data, error_details = check_task_status(base_url, tenant_id, st.session_state.task_id, alation_user_id, alation_api_key)

                with status_placeholder.container():
                    if success:
                        current_status = task_data.get("status", "UNKNOWN")
                        
                        if current_status == "SUCCESS":
                            st.success(f"Task Completed: {current_status}")
                        elif current_status in ["FAILURE", "ERROR", "CANCELLED"]:
                            st.error(f"Task Stopped: {current_status}")
                        else:
                            st.info(f"Task In Progress: {current_status}")

                        # Display key details
                        status_col1, status_col2, status_col3 = st.columns(3)
                        status_col1.metric("Created At", datetime.fromisoformat(task_data['created_at'].replace('Z', '+00:00')).strftime('%H:%M:%S'))
                        if task_data.get("completed_at"):
                            status_col2.metric("Completed At", datetime.fromisoformat(task_data['completed_at'].replace('Z', '+00:00')).strftime('%H:%M:%S'))
                        else:
                            status_col2.metric("Completed At", "N/A")
                        
                        if task_data.get("duration_ms"):
                            duration_sec = task_data['duration_ms'] / 1000
                            status_col3.metric("Duration", f"{duration_sec:.2f} s")
                        else:
                            status_col3.metric("Duration", "N/A")
                        
                        with st.expander("Full Task Details"):
                            st.json(task_data)

                    else:
                        st.error("Failed to retrieve task status.")
                        st.json(error_details)
                        break # Exit loop on error
                
                if current_status not in TERMINAL_STATUSES:
                    time.sleep(POLLING_INTERVAL)

