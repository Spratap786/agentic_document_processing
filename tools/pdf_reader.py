"""
TOOLS/PDF_READER.PY — Extracts text directly from a PDF.

Two kinds of PDFs exist:
  1. Digital PDF  → has real text you can select/copy → PyMuPDF can grab it directly
  2. Scanned PDF  → just images of pages → no selectable text → needs OCR

This tool handles case 1.
If it returns empty text, the Planner will route to the OCR agent for case 2.
"""

import fitz  # PyMuPDF — installed as `pymupdf`


def read_pdf_text(pdf_path: str) -> str:
    """
    Open the PDF and pull out all text from every page.
    Returns an empty string if the PDF has no embedded text (i.e., it's scanned).
    """
    doc = fitz.open(pdf_path)
    full_text = ""

    for page_num in range(len(doc)):
        page = doc[page_num]
        full_text += page.get_text()   # get_text() returns "" for image-only pages

    doc.close()
    return full_text.strip()
