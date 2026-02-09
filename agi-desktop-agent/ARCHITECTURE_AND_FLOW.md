# AGI Intelligence Agent: Architecture & Flow (STAR Method)

## Overview
This document explains the architecture and feature flows of the AGI Intelligence Agent, using the STAR (Situation, Task, Action, Result) method for each major feature.

---


## 1. Document Analysis Agent (General PDF Analysis)

**Situation:**
- Users need to analyze any kind of PDF (contracts, homework, general info, etc.) and answer questions using both document content and up-to-date web information.

**Task:**
- For simple/common questions, answer using the LLM only (no file or web search needed).
- For complex/document-specific questions, check the user's PDF for the answer first; if not found, then search the web.
- If found in the PDF, compare the answer with up-to-date web information.

**Action:**
- User uploads a PDF via the web UI or selects a file via CLI.
- The agent uses the LLM to classify the question as 'simple' (LLM only) or 'complex' (file/web).
- For simple questions, the agent asks the LLM directly and returns the answer.
- For complex questions, the agent extracts text using PyPDF2, uses the LLM to find the most relevant passage in the PDF, and:
   - If found, compares it with web information using the LLM.
   - If not found, performs a web search and answers using only web results.
- All steps are logged for traceability.

**Result:**
- The user receives a detailed analysis, including reasoning steps, sources, and a report tailored to the complexity of their question, with the most efficient and relevant information source used.

---

## 2. File Upload & Selection (User Experience)

**Situation:**
- Users may have contracts on their local system or want to upload them via a web interface.

**Task:**
- Provide both a web upload and a CLI file selection experience.

**Action:**
- Web: Flask API endpoint `/upload` accepts PDF files and stores them for analysis.
- CLI: User can enter a file path or scan their Documents folder for PDFs, then select one interactively.

**Result:**
- Flexible user experience: works for both web and CLI users.

---

## 3. LLM Integration (GroqClient)

**Situation:**
- Need to perform advanced language understanding and comparison.

**Task:**
- Use a powerful LLM (Llama 3.3 70B) for clause extraction and compliance analysis.

**Action:**
- GroqClient loads API keys from `.env` and sends prompts to the LLM for both clause extraction and comparison.
- Handles errors and logs all LLM interactions.

**Result:**
- Accurate, context-aware clause identification and compliance analysis.

---

## 4. Web Search Integration (LinkupWrapper)

**Situation:**
- Industry standards change frequently; up-to-date information is required.

**Task:**
- Retrieve current (2025) industry standards for any contract clause.

**Action:**
- LinkupWrapper loads API keys from `.env` and performs targeted web searches.
- Returns sources and snippets for LLM comparison.

**Result:**
- The agent always uses the latest standards for analysis.

---

## 5. Logging & Traceability

**Situation:**
- Users and developers need to understand and debug the agent's reasoning.

**Task:**
- Provide detailed logs for every step of the document analysis process.

**Action:**
- The agent uses Python's logging module to log info and debug messages at each step (file extraction, LLM prompts, web search, comparison, errors).
- Test cases also print all reasoning steps and results.

**Result:**
- Transparent, auditable, and debuggable analysis pipeline.

---

## 6. Testing & Quality Assurance

**Situation:**
- The agent must be robust and reliable.

**Task:**
- Provide automated tests for all core features.

**Action:**
- Pytest-based test cases for both successful and error scenarios.
- Tests print all intermediate and final results for easy review.

**Result:**
- High confidence in correctness and reliability of the agent.

---

## 7. Environment & Dependency Management

**Situation:**
- Consistent setup is required for all contributors and deployments.

**Task:**
- Track all dependencies in a requirements.txt file.

**Action:**
- All installed packages are exported to `requirements.txt` after setup or changes.

**Result:**
- Easy, reproducible environment setup for all users.

---

## Diagram (High-Level)

```
[User] --(PDF Upload/Select)--> [DocumentAgent]
   |                                 |
   |--(Web UI/CLI)-------------------|
   |                                 |
   |--(LLM: GroqClient)--------------|
   |--(Web Search: LinkupWrapper)----|
   |                                 |
   |<--(Analysis Report, Reasoning)--|
```

---

For further details, see the code and test cases in the repository.
