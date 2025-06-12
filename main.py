import streamlit as st
import requests
import json
from logger_config import logger

st.title("📊 AI-Powered IPO Analysis")
st.caption("RAG-Based Insights from Red Herring Prospectuses (RHP)")

# Initialize session state
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False

if "sample_text" not in st.session_state:
    st.session_state.sample_text = ""

if "user_query" not in st.session_state:
    st.session_state.user_query = ""

# Upload RHP PDF
uploaded_file = st.file_uploader("📎 Upload RHP (PDF only)", type=["pdf"])

# Upload button logic
if uploaded_file and st.button("Upload"):
    with st.spinner("Uploading..."):
        try:
            response = requests.post(
                "http://localhost:8000/upload",
                files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            )

            if response.status_code == 200:
                st.session_state.file_uploaded = True
                data = json.loads(response.content.decode("utf-8"))
                st.session_state.sample_text = data.get("message", "")
                st.success("✅ File uploaded and processed successfully!")
            else:
                st.error("❌ Upload failed. Please try again.")
        except Exception as e:
            st.error(f"Error: {e}")

# Show sample text from uploaded file
if st.session_state.file_uploaded:
    st.subheader("📄 Sample Text from PDF")
    st.write(st.session_state.sample_text)

    # User query input
    user_query = st.text_input("🔍 Enter your query", value=st.session_state.user_query, key="query_input")

    if st.button("Ask"):
        if user_query.strip():
            try:
                logger.info(user_query)
                st.session_state.user_query = user_query
                st.write("⏳ Processing your query...")
                url = "http://localhost:8000/user_query"
                headers = {"accept": "application/json","Content-Type": "application/json"}
                payload = {"query": f"{user_query}"}
                resp=requests.post(url,headers=headers,json=payload)
                logger.info(resp.status_code)
                if resp.status_code==200:
                    data = json.loads(resp.content)
                    st.subheader("💬 Response")
                    st.write(data["message"])
            except Exception as e:
                st.error(f"Error:{e}")
        
        else:
            st.warning("❗ Please enter a query.")




