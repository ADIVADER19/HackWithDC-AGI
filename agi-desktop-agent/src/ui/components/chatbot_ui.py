import streamlit as st
import os
import tempfile
from src.agents.document_agent import DocumentAgent
from src.agents.groq_client import GroqClient
from src.agents.linkup_wrapper import LinkupWrapper

def render_chatbot_ui():
    st.header("🤖 AGI PDF Chatbot")
    st.markdown("""
    1. **Upload a PDF** (highest priority)
    2. **Or** specify a directory to search for PDFs
    3. If no PDF, fallback to web search (Linkup)
    4. For simple questions, LLM will answer directly
    """)
    
    # Checklist state
    if 'checklist' not in st.session_state:
        st.session_state['checklist'] = {
            'pdf_uploaded': False,
            'directory_scanned': False,
            'llm_answered': False,
            'linkup_used': False
        }
    checklist = st.session_state['checklist']


    # Remove the old PDF upload section; only use the chat input with file attachment below
    pdf_path = None
    checklist['pdf_uploaded'] = False


    # Pure ChatGPT-style UI: just chat input and file attachment


    # (Table extraction for context only; not displayed to user)


    # (Image extraction for context only; not displayed to user)

    # Chatbot conversation
    st.markdown("---")
    st.subheader("Chat with your PDF or the web!")
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    if 'stats' not in st.session_state:
        st.session_state['stats'] = {'pdf_count': 0, 'linkup_count': 0, 'total': 0}
    col1, col2 = st.columns([5,1])
    with col1:
        user_input = st.text_input("Type your message and press Enter or click Send:", key="chat_input")
    with col2:
        uploaded_file = st.file_uploader("Attach PDF or .zip directory", type=["pdf", "zip"], key="chat_file")
    send_btn = st.button("Send")

    if send_btn:
        used_pdf = False
        used_linkup = False
        # Conversational prompt: If no file or directory, ask for one if needed
        if not user_input.strip() and not uploaded_file:
            st.warning("Please enter a message or attach a file.")
        elif uploaded_file:
            # Handle PDF or zip directory upload
            import tempfile, os, zipfile
            file_path = None
            if uploaded_file.name.lower().endswith('.pdf'):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.read())
                    file_path = tmp.name
            elif uploaded_file.name.lower().endswith('.zip'):
                import shutil
                with tempfile.TemporaryDirectory() as tmpdirname:
                    zip_path = os.path.join(tmpdirname, uploaded_file.name)
                    with open(zip_path, "wb") as f:
                        f.write(uploaded_file.read())
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(tmpdirname)
                    pdfs = []
                    for root, _, files in os.walk(tmpdirname):
                        for file in files:
                            if file.lower().endswith('.pdf'):
                                pdfs.append(os.path.join(root, file))
                    if pdfs:
                        st.info(f"{len(pdfs)} PDFs found in uploaded directory. All will be used for context.")
                        persistent_pdf_paths = []
                        for pdf in pdfs:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as persistent_tmp:
                                shutil.copyfileobj(open(pdf, 'rb'), persistent_tmp)
                                persistent_pdf_paths.append(persistent_tmp.name)
                        # Summarize and compare all PDFs for the user's question
                        groq_client = GroqClient()
                        linkup_wrapper = LinkupWrapper()
                        agent = DocumentAgent(groq_client, linkup_wrapper)
                        # Only pass a list if more than one PDF, else pass a single file path
                        pdf_arg = persistent_pdf_paths if len(persistent_pdf_paths) > 1 else persistent_pdf_paths[0]
                        if user_input.strip():
                            result = agent.process(pdf_arg, user_input)
                            checklist['llm_answered'] = True
                            checklist['linkup_used'] = any(result['linkup_sources'])
                            if not result['linkup_sources']:
                                used_pdf = True
                            if result['linkup_sources']:
                                used_linkup = True
                            st.session_state['stats']['total'] += 1
                            if used_pdf:
                                st.session_state['stats']['pdf_count'] += 1
                            if used_linkup:
                                st.session_state['stats']['linkup_count'] += 1
                            # Extraction logs removed
                            st.session_state['chat_history'].append((user_input, result['result'], result.get('extraction_logs', [])))
                        else:
                            st.warning("Please enter a question to process the uploaded files.")
                    else:
                        st.warning("No PDFs found in uploaded directory.")
            else:
                st.warning("Unsupported file type.")
            if file_path and user_input.strip():
                groq_client = GroqClient()
                linkup_wrapper = LinkupWrapper()
                agent = DocumentAgent(groq_client, linkup_wrapper)
                result = agent.process(file_path, user_input)
                checklist['llm_answered'] = True
                checklist['linkup_used'] = any(result['linkup_sources'])
                # Stats tracking
                if not result['linkup_sources']:
                    used_pdf = True
                if result['linkup_sources']:
                    used_linkup = True
                st.session_state['stats']['total'] += 1
                if used_pdf:
                    st.session_state['stats']['pdf_count'] += 1
                if used_linkup:
                    st.session_state['stats']['linkup_count'] += 1
                # Extraction logs removed
                st.session_state['chat_history'].append((user_input, result['result'], result.get('extraction_logs', [])))
            elif not user_input.strip():
                st.warning("Please enter a question to process the uploaded file.")
        else:
            # No file uploaded, just a message
            groq_client = GroqClient()
            linkup_wrapper = LinkupWrapper()
            agent = DocumentAgent(groq_client, linkup_wrapper)
            # If message looks like a directory request, prompt for directory name
            if "directory" in user_input.lower() or "folder" in user_input.lower():
                st.info("Please provide the full path to the directory you want to search for PDFs.")
            # Otherwise, process as a normal question (no PDF context)
            result = agent.process(None, user_input)
            checklist['llm_answered'] = True
            checklist['linkup_used'] = any(result['linkup_sources'])
            if not result['linkup_sources']:
                used_pdf = True
            if result['linkup_sources']:
                used_linkup = True
            st.session_state['stats']['total'] += 1
            if used_pdf:
                st.session_state['stats']['pdf_count'] += 1
            if used_linkup:
                st.session_state['stats']['linkup_count'] += 1
            # Extraction logs removed
            st.session_state['chat_history'].append((user_input, result['result'], result.get('extraction_logs', [])))
    # Display chat history with extraction logs
    for q, a, logs in st.session_state['chat_history']:
        st.markdown(f"**You:** {q}")
        st.markdown(f"**Agent:** {a}")
    # Stats UI
    st.markdown("---")
    st.subheader("Source Stats for This Session")
    stats = st.session_state['stats']
    st.markdown(f"**Total Requests:** {stats['total']}")
    st.markdown(f"**Answered Directly from PDF:** {stats['pdf_count']}")
    st.markdown(f"**Used Linkup/Web Search:** {stats['linkup_count']}")
    st.markdown("---")
    st.subheader("Workflow Checklist")
    st.markdown(f"- {'✅' if checklist['pdf_uploaded'] else '⬜'} PDF uploaded")
    st.markdown(f"- {'✅' if checklist['directory_scanned'] else '⬜'} Directory scanned for PDFs")
    st.markdown(f"- {'✅' if checklist['llm_answered'] else '⬜'} LLM answered using PDF context")
    st.markdown(f"- {'✅' if checklist['linkup_used'] else '⬜'} Linkup web search used (if needed)")
