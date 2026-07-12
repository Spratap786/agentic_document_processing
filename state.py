"""
STATE.PY — The shared "backpack" that flows through every node.

What is State?
  Every agent in the graph receives this dict as input and returns updates to it.
  Think of it like a form being passed down an assembly line — each worker
  fills in their section and passes it forward.

TypedDict = a regular Python dict, but with type hints so your editor helps you.
"""

from typing import TypedDict


class DocumentState(TypedDict):
    pdf_path: str        # Path to the PDF file (set once at the start, never changes)
    text: str            # Raw text from the PDF (filled by PDF reader or OCR)
    needs_ocr: bool      # Planner's decision: True = run OCR, False = skip it
    invoice_number: str  # Extracted by the LLM extractor agent
    document_type: str   # e.g. "invoice", "receipt", etc.
    validated: bool      # True if extraction passed validation
