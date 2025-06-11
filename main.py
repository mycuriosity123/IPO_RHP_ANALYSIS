import streamlit as st
import requests
import json
from logger_config import logger

st.title('AI-Powered IPO Analysis: RAG-Based Insights from Red Herring Prospectuses(RHP)')


uploaded_file = st.file_uploader("Upload RHP PDF only", type=["pdf"])

if uploaded_file and st.button("Upload"):
     with st.spinner("Uploading..."):
        response = requests.post("http://localhost:8000/upload",files={"file": (uploaded_file.name, uploaded_file.getvalue(),"application/pdf")})
        if response.status_code == 200:
            st.write("✅ The file was successfully processed!")
            sampledata=response.content
            st.write("sample text from PDF:")
            st.write(f"{json.loads(sampledata.decode('utf-8'))["message"]}")
        else:
            st.error("Upload failed.")



