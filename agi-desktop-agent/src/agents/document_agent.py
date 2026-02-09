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

    def process(self, file_path, question):
        reasoning_steps = []
        self.logger.info(f"Starting document analysis for: {file_path}")

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

        # For complex/rare questions, check PDF first, then web if not found
        # Step 1: Extract text from PDF
        text = ""
        try:
            self.logger.info("Extracting text from PDF using PyPDF2...")
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text() or ""
                    self.logger.debug(f"Extracted page text: {page_text[:100]}...")
                    text += page_text
            if text.strip():
                reasoning_steps.append("Extracted text from PDF.")
                self.logger.info("Successfully extracted text from PDF.")
            else:
                raise ValueError("No text extracted with PyPDF2.")
        except Exception as e:
            self.logger.warning(f"PyPDF2 extraction failed or empty: {e}. Trying OCR...")
            try:
                from pdf2image import convert_from_path
                import pytesseract
                from PIL import Image
                self.logger.info("Converting PDF pages to images for OCR...")
                images = convert_from_path(file_path)
                ocr_text = ""
                for i, img in enumerate(images):
                    page_ocr = pytesseract.image_to_string(img)
                    self.logger.debug(f"OCR page {i+1} text: {page_ocr[:100]}...")
                    ocr_text += page_ocr + "\n"
                if ocr_text.strip():
                    text = ocr_text
                    reasoning_steps.append("Extracted text from PDF using OCR.")
                    self.logger.info("Successfully extracted text from PDF using OCR.")
                else:
                    raise ValueError("No text extracted with OCR.")
            except Exception as ocr_e:
                self.logger.error(f"Failed to extract text with OCR: {ocr_e}")
                return {
                    "reasoning_steps": reasoning_steps + [f"Failed to extract text: {e}; OCR error: {ocr_e}"],
                    "linkup_sources": [],
                    "result": "Error during PDF extraction (PyPDF2 and OCR failed)."
                }

        # Step 2: Use LLM to identify the most relevant passage/section
        prompt_passage = (
            f"You are an expert teaching assistant. Given the following document text, extract and summarize ALL detailed lecture concepts, explanations, and key points relevant to the user's question."
            f"\n\nDocument Text:\n{text}\n\n"
            f"User Question: {question}\n"
            f"Return a comprehensive, structured summary of all relevant concepts, including definitions, formulas, examples, and explanations. If not found, say 'Not found in document'."
        )
        self.logger.info("Sending prompt to LLM to identify relevant passage/section in PDF...")
        passage = self.groq_client.ask(prompt_passage)
        self.logger.info(f"LLM identified passage/section: {passage}")
        reasoning_steps.append("Identified relevant passage/section using LLM.")

        if 'not found' in str(passage).lower():
            # If not found in document, fallback to web search
            self.logger.info("Passage not found in document, searching web instead.")
            search_query = f"2025 information or standards for: {question.strip()}"
            linkup_results = self.linkup_wrapper.search(search_query)
            sources = linkup_results.get("sources", []) if isinstance(linkup_results, dict) else linkup_results
            self.logger.info(f"Linkup returned {len(sources) if sources else 0} sources.")
            reasoning_steps.append("Searched for 2025 information or standards using Linkup.")
            standards_text = "\n".join([src.get("snippet", "") for src in sources]) if sources else ""
            prompt_answer = (
                f"Based on the following web information, answer the user's question as best as possible.\n\n"
                f"Question: {question}\n\n"
                f"2025 Information/Standards:\n{standards_text}\n\n"
                f"Provide a concise answer."
            )
            self.logger.info("Sending prompt to LLM to answer using web information only...")
            answer = self.groq_client.ask(prompt_answer)
            self.logger.info(f"LLM answer: {answer}")
            reasoning_steps.append("Answered using web information only.")
            self.logger.info("Document analysis complete (web fallback).")
            return {
                "reasoning_steps": reasoning_steps,
                "linkup_sources": sources,
                "result": answer
            }

        # If found in document, answer directly and skip Linkup
        self.logger.info("Answer found in user PDF. Returning answer without web search.")
        reasoning_steps.append("Answered using PDF only. No web or directory search needed.")
        return {
            "reasoning_steps": reasoning_steps,
            "linkup_sources": [],
            "result": passage
        }
