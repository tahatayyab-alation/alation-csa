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
def get_all_catalog_set_members():
    all_members = []
    limit = 100
    offset = 0

    while True:
        url = f"{base_url}/api/catalog_set/{catalog_set_id}/members/"
        params = {"limit": limit, "offset": offset}
        r = requests.get(url, headers=headers, params=params, timeout=30)
        r.raise_for_status()

        batch = r.json()
        if not batch:
            break

        all_members.extend(batch)
        offset += limit

    return all_members

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
            for i, a in enumerate(attributes, start=1):
                set_sensitive(a["id"])
                progress.progress(i / total)
            st.success("Sensitivity flag set for all attributes.")

    with col2:
        if st.button("Unset Sensitivity Flag"):
            progress = st.progress(0)
            for i, a in enumerate(attributes, start=1):
                unset_sensitive(a["id"])
                progress.progress(i / total)
            st.success("Sensitivity flag unset for all attributes.")

