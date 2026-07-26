"""
AGENTS/OCR.PY — Runs only when the planner routes here (scanned PDFs).
"""

from state import DocumentState
from tools.tesseract_tool import ocr_pdf


def ocr_node(state: DocumentState) -> dict:
    print("🔍 [OCR] Running Tesseract...")
    text = ocr_pdf(state["pdf_path"])
    print(f"✅ [OCR] Extracted {len(text)} chars")
    return {"text": text}
