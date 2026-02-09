
import os
import tempfile
import PyPDF2
import logging
from unittest.mock import MagicMock
from src.agents.document_agent import DocumentAgent

# Configure logging for tests
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

def create_sample_pdf(text, file_path):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    c = canvas.Canvas(file_path, pagesize=letter)
    c.drawString(100, 750, text)
    c.save()

def test_process_success():
    # Create a temp PDF
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        create_sample_pdf("This is a test contract. Key Clause: Payment must be made within 30 days.", tmp.name)
        pdf_path = tmp.name
    # Mock GroqClient and LinkupWrapper
    groq_client = MagicMock()
    # 1. classify (complex), 2. passage extraction, 3. comparison
    groq_client.ask.side_effect = [
        "complex",  # classify
        "Payment must be made within 30 days.",  # passage extraction
        "Comparison result"  # comparison
    ]
    linkup_wrapper = MagicMock()
    linkup_wrapper.search.return_value = {"sources": [{"snippet": "Industry standard: Payment within 30 days."}]}
    agent = DocumentAgent(groq_client, linkup_wrapper)
    print("\n--- test_process_success ---")
    print(f"Input PDF Path: {pdf_path}")
    print(f"Input Question: What is the payment clause?")
    result = agent.process(pdf_path, "What is the payment clause?")
    print("Reasoning Steps:")
    for step in result["reasoning_steps"]:
        print(f"  - {step}")
    print("Linkup Sources:")
    for src in result["linkup_sources"]:
        print(f"  - {src}")
    print(f"Result: {result['result']}")
    assert "Extracted text from PDF." in result["reasoning_steps"]
    assert "Identified relevant passage/section" in result["reasoning_steps"][2]
    assert "Searched for 2025 information or standards" in result["reasoning_steps"][3]
    assert result["result"] == "Comparison result"
    os.remove(pdf_path)

def test_process_pdf_error():
    groq_client = MagicMock()
    linkup_wrapper = MagicMock()
    agent = DocumentAgent(groq_client, linkup_wrapper)
    print("\n--- test_process_pdf_error ---")
    print(f"Input PDF Path: nonexistent.pdf")
    print(f"Input Question: Any question?")
    result = agent.process("nonexistent.pdf", "Any question?")
    print("Reasoning Steps:")
    for step in result["reasoning_steps"]:
        print(f"  - {step}")
    print("Linkup Sources:")
    for src in result["linkup_sources"]:
        print(f"  - {src}")
    print(f"Result: {result['result']}")
    assert "Failed to extract text" in result["reasoning_steps"][-1]
    assert result["result"].startswith("Error during PDF extraction")


def test_process_homework_pdf():
    print("\n--- test_process_homework_pdf ---")
    pdf_path = os.path.join(os.path.dirname(__file__), "sample_homework.pdf")
    question = "What are Newton's Laws?"
    groq_client = MagicMock()
    # 1. classify (complex), 2. passage extraction, 3. comparison
    groq_client.ask.side_effect = [
        "complex",  # classify
        "Newton's Laws are explained in the passage.",  # passage extraction
        "Comparison: The passage provides a basic explanation of Newton's Laws."
    ]
    linkup_wrapper = MagicMock()
    linkup_wrapper.search.return_value = {"sources": [{"snippet": "Newton's Laws: 1st, 2nd, 3rd law."}]}
    agent = DocumentAgent(groq_client, linkup_wrapper)
    result = agent.process(pdf_path, question)
    print(f"Input PDF Path: {pdf_path}")
    print(f"Input Question: {question}")
    print("Reasoning Steps:")
    for step in result["reasoning_steps"]:
        print(f"  - {step}")
    print("Linkup Sources:")
    for src in result["linkup_sources"]:
        print(f"  - {src}")
    print(f"Result: {result['result']}")
    assert "Extracted text from PDF." in result["reasoning_steps"]
    assert result["result"].startswith("Comparison:")


def test_process_general_pdf():
    print("\n--- test_process_general_pdf ---")
    pdf_path = os.path.join(os.path.dirname(__file__), "sample_general.pdf")
    question = "What does the document say about the sky?"
    groq_client = MagicMock()
    # 1. classify (complex), 2. passage extraction, 3. comparison
    groq_client.ask.side_effect = [
        "complex",  # classify
        "The passage states: The sky is blue.",  # passage extraction
        "Comparison: The statement matches common knowledge."
    ]
    linkup_wrapper = MagicMock()
    linkup_wrapper.search.return_value = {"sources": [{"snippet": "The sky is blue due to Rayleigh scattering."}]}
    agent = DocumentAgent(groq_client, linkup_wrapper)
    result = agent.process(pdf_path, question)
    print(f"Input PDF Path: {pdf_path}")
    print(f"Input Question: {question}")
    print("Reasoning Steps:")
    for step in result["reasoning_steps"]:
        print(f"  - {step}")
    print("Linkup Sources:")
    for src in result["linkup_sources"]:
        print(f"  - {src}")
    print(f"Result: {result['result']}")
    assert "Extracted text from PDF." in result["reasoning_steps"]
    assert result["result"].startswith("Comparison:")
