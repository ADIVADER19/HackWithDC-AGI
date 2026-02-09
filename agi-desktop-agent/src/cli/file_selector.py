import os

def scan_for_pdfs(directory):
    pdfs = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdfs.append(os.path.join(root, file))
    return pdfs

def select_pdf():
    user_input = input("Enter PDF file path or type 'scan' to search your Documents folder: ").strip()
    if user_input.lower() == 'scan':
        docs_dir = os.path.expanduser("~/Documents")
        pdfs = scan_for_pdfs(docs_dir)
        if not pdfs:
            print("No PDF files found in Documents.")
            return None
        print("Found PDF files:")
        for idx, pdf in enumerate(pdfs):
            print(f"{idx + 1}: {pdf}")
        choice = int(input("Select a file by number: ")) - 1
        if 0 <= choice < len(pdfs):
            return pdfs[choice]
        else:
            print("Invalid selection.")
            return None
    else:
        if os.path.isfile(user_input) and user_input.lower().endswith('.pdf'):
            return user_input
        else:
            print("Invalid file path.")
            return None

# Usage:
# file_path = select_pdf()
# if file_path:
#     result = document_agent.process(file_path, question)
