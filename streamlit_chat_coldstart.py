import streamlit as st
import requests
import shlex

def generate_curl_command(base_url, tenant_id, data_product_id, db, schema, if_exists, user_id, api_key):
    """Generates the cURL command string from user inputs."""
    
    # Construct the full URL with query parameters
    url = (
        f"{base_url}/nsapi/api/v3/orgs/{tenant_id}/data_product/cold_start_from_data_product_id"
        f"?data_product_id={data_product_id}"
        f"&result_cache_database={db}"
        f"&result_cache_schema={schema}"
        f"&if_exists={if_exists}"
    )
    
    # Construct the full cURL command using shlex for proper shell quoting
    command_parts = [
        'curl',
        '-X', 'POST',
        shlex.quote(url),
        '-H', 'accept: application/json',
        '-H', f'alation-user-id: {shlex.quote(user_id)}',
        '-H', f'Authorization: AlationAPIKey {shlex.quote(api_key)}'
    ]
    
    return ' '.join(command_parts)

def execute_api_call(base_url, tenant_id, data_product_id, db, schema, if_exists, user_id, api_key):
    """Executes the API call using the requests library."""
    
    url = f"{base_url}/nsapi/api/v3/orgs/{tenant_id}/data_product/cold_start_from_data_product_id"
    
    headers = {
        'accept': 'application/json',
        'alation-user-id': user_id,
        'Authorization': f'AlationAPIKey {api_key}'
    }
    
    params = {
        'data_product_id': data_product_id,
        'result_cache_database': db,
        'result_cache_schema': schema,
        'if_exists': if_exists
    }
    
    try:
        response = requests.post(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return True, response
    except requests.exceptions.RequestException as e:
        return False, e


# --- Streamlit App UI ---

st.set_page_config(layout="wide", page_title="API Command Center")

st.title("Chat with Data Products - Cold Start Utility 🐻‍❄️")
st.caption("Use this interface to build, preview, and execute your cold start request.")

# --- User Inputs ---
st.header("1. Enter Code Start Request Details")

col1, col2 = st.columns(2)

with col1:
    base_url = st.text_input("Base URL", placeholder="https://your-alation-instance.com")
    tenant_id = st.text_input("Tenant ID", placeholder="e.g., 123e4567-e89b-12d3-a456-426614174000")
    data_product_id = st.text_input("Data Product ID", placeholder="e.g., my-data-product")
    if_exists = st.selectbox("If Exists Strategy", options=["error", "archive", "delete"], index=0)

with col2:
    result_cache_db = st.text_input("Result Cache Database", placeholder="e.g., PROD_DB")
    result_cache_schema = st.text_input("Result Cache Schema", placeholder="e.g., ANALYTICS")
    alation_user_id = st.text_input("Alation User ID", placeholder="e.g., 5")
    alation_api_key = st.text_input("Alation API Key", type="password", placeholder="Enter your API key")

# --- Form Validation ---
all_fields_filled = all([
    base_url, tenant_id, data_product_id, result_cache_db, 
    result_cache_schema, alation_user_id, alation_api_key, if_exists
])

st.divider()

# --- Preview and Execute ---
st.header("2. Preview and Execute")

preview_col, execute_col = st.columns(2)

with preview_col:
    if st.button("Preview Command", disabled=not all_fields_filled):
        curl_command = generate_curl_command(
            base_url, tenant_id, data_product_id, result_cache_db,
            result_cache_schema, if_exists, alation_user_id, alation_api_key
        )
        st.subheader("Generated cURL Command")
        st.code(curl_command, language="bash")
        st.info("You can copy the command above to use it in your terminal.")

with execute_col:
    if st.button("⚡ Execute API Call", type="primary", disabled=not all_fields_filled):
        with st.spinner("Sending request..."):
            success, result = execute_api_call(
                base_url, tenant_id, data_product_id, result_cache_db,
                result_cache_schema, if_exists, alation_user_id, alation_api_key
            )
        
        st.subheader("API Response")
        if success:
            st.success(f"Success! Status Code: {result.status_code}")
            try:
                # Try to display the JSON response
                st.json(result.json())
            except ValueError:
                # If response is not JSON, display as text
                st.text(result.text)
        else:
            st.error(f"An error occurred:")
            st.exception(result)

if not all_fields_filled:
    st.warning("Please fill in all the fields to enable the Preview and Execute buttons.")

