"""
AGENTS/PLANNER.PY — First node. Reads the PDF, decides if OCR is needed.
(Rule-based for now — will become LLM-driven in a later phase.)
"""

from state import DocumentState
from tools.pdf_reader import read_pdf_text


def planner_node(state: DocumentState) -> dict:
    print("🧠 [PLANNER] Reading PDF...")
    text = read_pdf_text(state["pdf_path"])

    if len(text) > 50:
        print(f"✅ [PLANNER] Found {len(text)} chars — skipping OCR")
        return {"text": text, "needs_ocr": False}
    else:
        print("⚠️  [PLANNER] No text — routing to OCR")
        return {"text": "", "needs_ocr": True}


def should_ocr(state: DocumentState) -> str:
    """Conditional edge: routes to 'ocr' or 'extract' based on planner's decision."""
    return "ocr" if state["needs_ocr"] else "extract"
