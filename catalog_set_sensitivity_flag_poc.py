import requests
import streamlit as st

# =========================
# STREAMLIT UI
# =========================
st.title("Catalog Set Sensitivity Flag PoC")

base_url = st.text_input("Alation Base URL", "https://your-instance.alationcloud.com")
api_token = st.text_input("API Token", type="password")
catalog_set_id = st.text_input("Catalog Set ID")

if "attributes" not in st.session_state:
    st.session_state["attributes"] = []

if not (base_url and api_token and catalog_set_id):
    st.stop()

headers = {
    "Token": api_token,
    "accept": "application/json",
}

# =========================
# API FUNCTIONS
# =========================
def get_all_catalog_set_members():
    all_members = []
    limit = 100
    skip = 0

    while True:
        url = f"{base_url}/api/v1/catalog_set/{catalog_set_id}/members/"
        params = {
            "limit": limit,
            "skip": skip,
            "enable_server_count": "true",
            "search": "",
        }

        r = requests.get(url, headers=headers, params=params, timeout=30)
        r.raise_for_status()

        batch = r.json()
        if not batch:
            break

        all_members.extend(batch)
        skip += limit

    return all_members


def set_sensitive(attr_id):
    url = f"{base_url}/ajax/set_attr_sensitivity/{attr_id}/"
    write_headers = {
        "Token": api_token,
        "Connection": "close",
        "accept": "application/json",
    }
    return requests.post(url, headers=write_headers, data={"action": "mark_sensitive"}, timeout=30)

def unset_sensitive(attr_id):
    url = f"{base_url}/ajax/set_attr_sensitivity/{attr_id}/"
    write_headers = {
        "Token": api_token,
        "Connection": "close",
        "accept": "application/json",
    }
    return requests.post(url, headers=write_headers, data={"action": "mark_unsensitive"}, timeout=30)

# =========================
# MAIN FLOW
# =========================
if st.button("Retrieve Catalog Set Members"):
    with st.spinner("Retrieving catalog set members..."):
        members = get_all_catalog_set_members()

    attributes = [m for m in members if m.get("otype") == "attribute"]
    st.session_state["attributes"] = attributes

    st.write(f"Total members returned: {len(members)}")
    st.write(f"Attributes eligible for sensitivity: {len(attributes)}")

    if attributes:
        st.dataframe(
            [
                {
                    "id": a["id"],
                    "title": a.get("title"),
                    "table": a.get("table", {}).get("title"),
                    "schema": a.get("schema", {}).get("title"),
                    "ds": a.get("ds", {}).get("title"),
                }
                for a in attributes
            ]
        )
    else:
        st.warning("No attributes found in this catalog set.")

# =========================
# ACTION BUTTONS
# =========================
attributes = st.session_state.get("attributes", [])
if attributes:
    total = len(attributes)
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Set Sensitivity Flag"):
            progress = st.progress(0)
            failures = []
            for i, a in enumerate(attributes, start=1):
                try:
                    resp = set_sensitive(a["id"])
                    resp.raise_for_status()
                except Exception as e:
                    failures.append((a["id"], str(e)))
                progress.progress(int(i * 100 / total))
            if failures:
                st.error(f"Set completed with {len(failures)} failures. See logs.")
                st.write(failures)
            else:
                st.success("Sensitivity flag set for all attributes.")

    with col2:
        if st.button("Unset Sensitivity Flag"):
            progress = st.progress(0)
            failures = []
            for i, a in enumerate(attributes, start=1):
                try:
                    resp = unset_sensitive(a["id"])
                    resp.raise_for_status()
                except Exception as e:
                    failures.append((a["id"], str(e)))
                progress.progress(int(i * 100 / total))
            if failures:
                st.error(f"Unset completed with {len(failures)} failures. See logs.")
                st.write(failures)
            else:
                st.success("Sensitivity flag unset for all attributes.")
