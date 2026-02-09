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

    # PDF upload
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if uploaded_file:
        checklist['pdf_uploaded'] = True
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            pdf_path = tmp.name
        st.success("PDF uploaded and ready!")
    else:
        pdf_path = None
        checklist['pdf_uploaded'] = False

    # Directory selection
    if not pdf_path:
        dir_path = st.text_input("Or enter a directory to scan for PDFs:", value=os.path.expanduser("~"))
        if st.button("Scan Directory"):
            pdfs = []
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdfs.append(os.path.join(root, file))
            if pdfs:
                checklist['directory_scanned'] = True
                st.success(f"Found {len(pdfs)} PDF(s). Select one:")
                selected_pdf = st.selectbox("Select a PDF", pdfs)
                pdf_path = selected_pdf
            else:
                checklist['directory_scanned'] = False
                st.warning("No PDFs found in directory.")
        else:
            checklist['directory_scanned'] = False
    else:
        checklist['directory_scanned'] = False

    # Table extraction
    if pdf_path:
        st.markdown("---")
        st.subheader("Extracted Tables from PDF")
        try:
            import camelot
            tables = camelot.read_pdf(pdf_path, pages="all")
            if tables and tables.n > 0:
                for i, table in enumerate(tables):
                    st.markdown(f"**Table {i+1}:**")
                    st.dataframe(table.df)
            else:
                st.info("No tables found in PDF.")
        except Exception as e:
            st.warning(f"Table extraction error: {e}")

    # Image extraction
    if pdf_path:
        st.markdown("---")
        st.subheader("Extracted Images from PDF")
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            img_count = 0
            for page_num in range(len(doc)):
                page = doc[page_num]
                images = page.get_images(full=True)
                for img_index, img in enumerate(images):
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    if pix.n < 5:  # GRAY or RGB
                        img_count += 1
                        img_bytes = pix.tobytes()
                        st.image(img_bytes, caption=f"Page {page_num+1} Image {img_index+1}")
                    pix = None
            if img_count == 0:
                st.info("No images found in PDF.")
        except Exception as e:
            st.warning(f"Image extraction error: {e}")

    # Chatbot conversation
    st.markdown("---")
    st.subheader("Chat with your PDF or the web!")
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    user_input = st.text_input("Your question:")
    if st.button("Send") and user_input:
        groq_client = GroqClient()
        linkup_wrapper = LinkupWrapper()
        agent = DocumentAgent(groq_client, linkup_wrapper)
        if pdf_path:
            result = agent.process(pdf_path, user_input)
            checklist['llm_answered'] = True
            checklist['linkup_used'] = any(result['linkup_sources'])
        else:
            checklist['llm_answered'] = False
            checklist['linkup_used'] = False
            st.warning("No PDF selected or uploaded. Please upload or select a PDF, or ask a simple question.")
            result = {'reasoning_steps': [], 'linkup_sources': [], 'result': ''}
        st.session_state['chat_history'].append((user_input, result['result']))
    # Display chat history
    for q, a in st.session_state['chat_history']:
        st.markdown(f"**You:** {q}")
        st.markdown(f"**Agent:** {a}")
    # Checklist UI
    st.markdown("---")
    st.subheader("Workflow Checklist")
    st.markdown(f"- {'✅' if checklist['pdf_uploaded'] else '⬜'} PDF uploaded")
    st.markdown(f"- {'✅' if checklist['directory_scanned'] else '⬜'} Directory scanned for PDFs")
    st.markdown(f"- {'✅' if checklist['llm_answered'] else '⬜'} LLM answered using PDF context")
    st.markdown(f"- {'✅' if checklist['linkup_used'] else '⬜'} Linkup web search used (if needed)")
