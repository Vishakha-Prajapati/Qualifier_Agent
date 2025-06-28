from langchain_community.document_loaders import PyPDFLoader
import os

def extract_pdf_text():
    pdf_path = os.path.join(os.path.dirname(__file__), 'pdf', 'assessment.pdf')
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    return "\n".join([page.page_content for page in pages])

if __name__ == "__main__":
    print(extract_pdf_text())