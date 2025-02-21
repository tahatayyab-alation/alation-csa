import streamlit as st
from Documents_RetrieveDocuments import fetch_document_info  # Import function

st.title("📄 Alation Document Retriever")

# User inputs
st.sidebar.header("🔧 API Configuration")
base_url = st.sidebar.text_input("🔗 Alation BASE URL", "https://your-alation-instance.alationcloud.com")
api_token = st.sidebar.text_input("🔑 API Token", type="password")
doc_id = st.text_input("Enter Document ID:", "")

# 📌 Add Usage Notice in Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown(
    "⚠️ **Notice of Usage, Rights, and Alation Responsibility:**\n"
    "This code is provided **as-is** with no expressed or implied warranty or support.\n"
    "Alation is **not responsible** for its modification, use, or maintenance."
)

if st.button("Fetch Document Info"):
    if not doc_id:
        st.warning("⚠️ Please enter a Document ID.")
    elif not api_token:
        st.error("❌ API token is required.")
    else:
        # Call the function from Documents_RetrieveDocuments.py
        data = fetch_document_info(base_url, api_token, doc_id)
        if "error" in data:
            st.error(f"❌ {data['error']}")
        else:
            st.json(data)  # Display document info
