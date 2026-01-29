import requests
import streamlit as st

# =========================
# STREAMLIT UI
# =========================
st.title("Catalog Set Sensitivity Flag PoC")

base_url = st.text_input("Alation Base URL", "https://your-instance.alationcloud.com")
api_token = st.text_input("API Token", type="password")
catalog_set_id = st.text_input("Catalog Set ID")

if not (base_url and api_token and catalog_set_id):
    st.stop()

headers = {
    "Token": api_token,
    "accept": "application/json",
}

# =========================
# API FUNCTIONS
# =========================
def get_catalog_set_members():
    url = f"{base_url}/api/catalog_set/{catalog_set_id}/members/"
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()

def set_sensitive(attr_id):
    url = f"{base_url}/ajax/set_attr_sensitivity/{attr_id}/"
    r = requests.post(
        url,
        headers={"Token": api_token},
        data={"action": "mark_sensitive"},
        timeout=30,
    )
    r.raise_for_status()

def unset_sensitive(attr_id):
    url = f"{base_url}/ajax/set_attr_sensitivity/{attr_id}/"
    r = requests.post(
        url,
        headers={"Token": api_token},
        data={"action": "mark_unsensitive"},
        timeout=30,
    )
    r.raise_for_status()

# =========================
# MAIN FLOW
# =========================
if st.button("Retrieve Catalog Set Members"):
    members = get_catalog_set_members()

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
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Set Sensitivity Flag"):
            with st.spinner("Marking attributes sensitive..."):
                for a in attributes:
                    set_sensitive(a["id"])
            st.success("Sensitivity flag set for all attributes.")

    with col2:
        if st.button("Unset Sensitivity Flag"):
            with st.spinner("Unmarking attributes sensitive..."):
                for a in attributes:
                    unset_sensitive(a["id"])
            st.success("Sensitivity flag unset for all attributes.")
