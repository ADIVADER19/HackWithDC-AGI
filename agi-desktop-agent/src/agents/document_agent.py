"""
DocumentAgent for document analysis using Groq LLM and Linkup web search
"""


import logging
import PyPDF2
import os

class DocumentAgent:
    def scan_directory_for_pdfs(self, directory, year=None):
        """Scan directory for PDFs, optionally filter by year in filename."""
        pdfs = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.pdf'):
                    if year and str(year) not in file:
                        continue
                    pdfs.append(os.path.join(root, file))
        return pdfs

    def extract_tables(self, file_path):
        """Extract tables from PDF using camelot."""
        try:
            import camelot
            tables = camelot.read_pdf(file_path, pages="all")
            return [table.df for table in tables] if tables and tables.n > 0 else []
        except Exception as e:
            self.logger.warning(f"Table extraction error: {e}")
            return []

    def extract_images(self, file_path):
        """Extract images from PDF using PyMuPDF."""
        try:
            import fitz
            doc = fitz.open(file_path)
            images = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                for img in page.get_images(full=True):
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    if pix.n < 5:
                        images.append(pix.tobytes())
                    pix = None
            return images
        except Exception as e:
            self.logger.warning(f"Image extraction error: {e}")
            return []

    def __init__(self, groq_client, linkup_wrapper):
        self.groq_client = groq_client
        self.linkup_wrapper = linkup_wrapper
        self.logger = logging.getLogger("DocumentAgent")


    def process(self, file_path_or_paths, question):
        reasoning_steps = []
        self.logger.info(f"Starting document analysis for: {file_path_or_paths}")

        # Step 0: Use LLM to determine if the question is simple/common or complex/rare
        prompt_simple = (
            f"Is the following question simple/common knowledge (e.g., 'What are Newton's Laws?') or does it require specific or complex information from a document?\n"
            f"Question: {question}\n"
            f"Answer with 'simple' or 'complex' only."
        )
        self.logger.info("Classifying question as simple or complex using LLM...")
        classification = self.groq_client.ask(prompt_simple)
        self.logger.info(f"LLM classified question as: {classification}")
        reasoning_steps.append(f"Classified question as: {classification}")

        if 'simple' in str(classification).lower():
            # For simple/common questions, ask the LLM directly
            self.logger.info("Asking LLM directly for simple/common question.")
            prompt_answer = (
                f"Answer the following question as best as possible.\n\n"
                f"Question: {question}\n\n"
                f"If the answer is not common knowledge, say 'I don't know'."
            )
            answer = self.groq_client.ask(prompt_answer)
            self.logger.info(f"LLM answer: {answer}")
            reasoning_steps.append("Answered using LLM only.")
            self.logger.info("Document analysis complete (LLM only).")
            return {
                "reasoning_steps": reasoning_steps,
                "linkup_sources": [],
                "result": answer
            }

        # For complex/rare questions, check PDF(s) first, then web if not found
        # Step 1: Extract text from PDF(s)
        text = ""
        extraction_logs = None  # Extraction logs removed
        # Only allow single PDF for now
        if isinstance(file_path_or_paths, list):
            file_paths = [file_path_or_paths[0]] if file_path_or_paths else []
        else:
            file_paths = [file_path_or_paths]
        for idx, file_path in enumerate(file_paths):
            if not file_path:
                continue
            try:
                pass  # Extraction logs removed
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page_num, page in enumerate(reader.pages):
                        page_text = page.extract_text() or ""
                        pass  # Extraction logs removed
                        text += page_text
                if text.strip():
                    reasoning_steps.append(f"Extracted text from PDF {idx+1} (all pages).")
                    pass  # Extraction logs removed
                else:
                    raise ValueError("No text extracted with PyPDF2.")
            except Exception as e:
                pass  # Extraction logs removed
                try:
                    from pdf2image import convert_from_path
                    import pytesseract
                    from PIL import Image
                    pass  # Extraction logs removed
                    images = convert_from_path(file_path)
                    ocr_text = ""
                    for i, img in enumerate(images):
                        page_ocr = pytesseract.image_to_string(img)
                        pass  # Extraction logs removed
                        ocr_text += page_ocr + "\n"
                    if ocr_text.strip():
                        text += ocr_text
                        reasoning_steps.append(f"Extracted text from PDF {idx+1} using OCR (all pages).")
                        pass  # Extraction logs removed
                    else:
                        raise ValueError("No text extracted with OCR.")
                except Exception as ocr_e:
                    pass  # Extraction logs removed
                    return {
                        "reasoning_steps": reasoning_steps + [f"Failed to extract text: {e}; OCR error: {ocr_e}"],
                        "linkup_sources": [],
                        "result": "Error during PDF extraction (PyPDF2 and OCR failed).",
                        # Extraction logs removed
                    }

        # If text is too long, chunk and summarize before sending to LLM
        MAX_CHUNK_SIZE = 8000  # chars, safe for LLM
        if len(text) > MAX_CHUNK_SIZE:
            chunks = [text[i:i+MAX_CHUNK_SIZE] for i in range(0, len(text), MAX_CHUNK_SIZE)]
            chunk_summaries = []
            for i, chunk in enumerate(chunks):
                chunk_prompt = (
                    f"Summarize the following document chunk in detail, including all key points, definitions, and formulas.\n\nChunk:\n{chunk}\n\nReturn a detailed summary."
                )
                summary = self.groq_client.ask(chunk_prompt)
                chunk_summaries.append(summary)
            text = "\n".join(chunk_summaries)

        # Step 2: Use LLM to identify the most relevant passage/section
        # Step 2: Summarize PDF data for context using LLM
        prompt_context = (
            f"You are an expert teaching assistant. Given the following document text, summarize the entire lecture in detail, including all slide concepts, definitions, formulas, and key points."
            f"\n\nDocument Text:\n{text}\n\n"
            f"Return a comprehensive, structured summary for context."
        )
        pass  # Extraction logs removed
        pdf_context_summary = self.groq_client.ask(prompt_context)
        pass  # Extraction logs removed

        prompt_passage = (
            f"You are an expert teaching assistant. Given the following summarized lecture context and document text, extract and explain ALL detailed lecture concepts, explanations, and key points relevant to the user's question."
            f"\n\nLecture Context Summary:\n{pdf_context_summary}\n\nDocument Text:\n{text}\n\n"
            f"User Question: {question}\n"
            f"Return a comprehensive, structured summary of all relevant concepts, including definitions, formulas, examples, and explanations. If ANY relevant content is found, summarize it. Only say 'Not found in document' if the document is truly unrelated or empty."
        )
        pass  # Extraction logs removed
        passage = self.groq_client.ask(prompt_passage)
        pass  # Extraction logs removed
        reasoning_steps.append("Identified relevant passage/section using LLM.")

        # Improved fallback logic: Only use Linkup if PDF is empty or truly unrelated
        if (not text.strip()) or (isinstance(passage, str) and passage.strip().lower() in ["not found in document", "not found", "no relevant content found", "document unrelated", "document is empty"]):
            pass  # Extraction logs removed
            search_query = f"2025 information or standards for: {question.strip()}"
            linkup_results = self.linkup_wrapper.search(search_query)
            sources = linkup_results.get("sources", []) if isinstance(linkup_results, dict) else linkup_results
            pass  # Extraction logs removed
            reasoning_steps.append("Searched for 2025 information or standards using Linkup.")
            standards_text = "\n".join([src.get("snippet", "") for src in sources]) if sources else ""
            prompt_answer = (
                f"Based on the following web information, answer the user's question as best as possible.\n\n"
                f"Question: {question}\n\n"
                f"2025 Information/Standards:\n{standards_text}\n\n"
                f"Provide a concise answer."
            )
            pass  # Extraction logs removed
            answer = self.groq_client.ask(prompt_answer)
            pass  # Extraction logs removed
            reasoning_steps.append("Answered using web information only.")
            pass  # Extraction logs removed
            return {
                "reasoning_steps": reasoning_steps,
                "linkup_sources": sources,
                "result": answer,
                # Extraction logs removed
            }

        # If found in document, answer directly and skip Linkup
        pass  # Extraction logs removed
        reasoning_steps.append("Answered using PDF only. No web or directory search needed.")
        return {
            "reasoning_steps": reasoning_steps,
            "linkup_sources": [],
            "result": passage
        }
