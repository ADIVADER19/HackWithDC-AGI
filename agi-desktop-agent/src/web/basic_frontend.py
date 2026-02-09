
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import streamlit as st
import requests

st.title("AGI Intelligence Agent - Test UI")

st.write("Upload a PDF and ask a question. The agent will use LLM, your file, and/or the web as needed.")

# File upload
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
question = st.text_input("Enter your question")

if st.button("Analyze"):
    if uploaded_file is None or not question:
        st.warning("Please upload a PDF and enter a question.")
    else:
        # Use a temp file path that works on all OS
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            temp_path = tmp.name
        st.info(f"File uploaded to {temp_path}. Sending to backend...")
        # Use openai-based GroqClient for Streamlit compatibility
        from src.agents.document_agent import DocumentAgent
        from src.agents.groq_client import GroqClient
        from src.agents.linkup_wrapper import LinkupWrapper
        groq_client = GroqClient()
        linkup_wrapper = LinkupWrapper()
        agent = DocumentAgent(groq_client, linkup_wrapper)
        result = agent.process(temp_path, question)
        st.subheader("Reasoning Steps:")
        for step in result["reasoning_steps"]:
            st.write(f"- {step}")
        st.subheader("Linkup/Web Sources:")
        for src in result["linkup_sources"]:
            st.write(src)
        st.subheader("Result:")
        st.write(result["result"])
