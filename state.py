"""
STATE.PY — The shared state that flows through every LangGraph node.
Each agent reads from it and returns updates to it.
"""

from typing import TypedDict


class DocumentState(TypedDict):
    pdf_path: str        # Path to the PDF being processed
    text: str            # Text from PDF reader or OCR
    needs_ocr: bool      # Planner's decision
    invoice_number: str  # Extracted by the LLM
    document_type: str   # e.g. "invoice"
    validated: bool      # Did extraction pass validation?
