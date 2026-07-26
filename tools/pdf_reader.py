"""
TOOLS/PDF_READER.PY — Extract text from digital PDFs using PyMuPDF.
Returns empty string for scanned (image-only) PDFs → planner routes to OCR.
"""

import fitz  # PyMuPDF


def read_pdf_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text.strip()
