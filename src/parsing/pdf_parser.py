import pdfplumber
import chardet
import os
from datetime import datetime
 
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
 
from storage.mongo import save_to_mongo
from utils.logger import logging
 
 
def detect_encoding(file_path):
    """Detect file encoding using chardet."""
    with open(file_path, "rb") as f:
        raw = f.read()
    result = chardet.detect(raw)
    encoding = result.get("encoding", "utf-8") or "utf-8"
    logging.info(f"Detected encoding for {file_path}: {encoding}")
    return encoding
 
 
def extract_text_from_pdf(file_path):
    """Extract text page by page from a PDF file."""
    pages_data = []
 
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
 
                # Multi-column layout: try splitting page into two halves
                if text.count("\n") < 5 and page.width:
                    left = page.crop((0, 0, page.width / 2, page.height))
                    right = page.crop((page.width / 2, 0, page.width, page.height))
                    text = (left.extract_text() or "") + "\n" + (right.extract_text() or "")
 
                tables = page.extract_tables()
                structured_tables = []
                for table in tables:
                    structured_tables.append([
                        [cell if cell is not None else "" for cell in row]
                        for row in table
                    ])
 
                pages_data.append({
                    "page_number": page_num,
                    "text": text.strip(),
                    "tables": structured_tables
                })
 
        logging.info(f"Successfully extracted {len(pages_data)} pages from PDF: {file_path}")
 
    except Exception as e:
        logging.error(f"Failed to extract PDF {file_path}: {e}")
 
    return pages_data
 
 
def process_pdf(file_path):
    """Extract, structure, and store PDF content in MongoDB."""
    file_name = os.path.basename(file_path)
    logging.info(f"Processing PDF: {file_name}")
 
    pages = extract_text_from_pdf(file_path)
 
    for page in pages:
        document = {
            "content": {
                "text": page["text"],
                "tables": page["tables"],
                "page_number": page["page_number"]
            },
            "metadata": {
                "file_name": file_name,
                "document_type": "pdf",
                "extraction_timestamp": datetime.utcnow(),
                "source": file_path,
                "extraction_library": "pdfplumber",
                "page_number": page["page_number"]
            }
        }
 
        save_to_mongo(document, source_url=file_path)
        logging.info(f"Stored page {page['page_number']} of {file_name} in MongoDB")
 
 
def process_all_pdfs(folder_path="data/raw/pdf"):
    """Process all PDF files in a folder."""
    if not os.path.exists(folder_path):
        logging.warning(f"PDF folder not found: {folder_path}")
        return
 
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]
    if not pdf_files:
        logging.warning(f"No PDF files found in {folder_path}")
        return
 
    for filename in pdf_files:
        file_path = os.path.join(folder_path, filename)
        process_pdf(file_path)
 
 
if __name__ == "__main__":
    process_all_pdfs()