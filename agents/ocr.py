"""
AGENTS/OCR.PY — OCR Node.

Only runs when the Planner decides the PDF needs OCR.
If the PDF already had text, this node is skipped entirely.

This node just calls our tesseract_tool and updates state["text"].
"""

from state import DocumentState
from tools.tesseract_tool import ocr_pdf


def ocr_node(state: DocumentState) -> dict:
    """
    Runs Tesseract OCR on the PDF.
    Returns the extracted text to update the state.
    """
    print("\n🔍 [OCR] Running OCR on scanned PDF...")

    text = ocr_pdf(state["pdf_path"])

    print(f"✅ [OCR] OCR complete. Extracted {len(text)} characters.")

    # Only return the field we're updating
    # LangGraph merges this into the existing state automatically
    return {
        "text": text
    }
