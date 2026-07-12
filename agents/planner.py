"""
AGENTS/PLANNER.PY — The first agent. Reads the PDF and decides what to do next.

Two things live here:
  1. planner_node   → the actual agent function (a LangGraph node)
  2. should_ocr     → a routing function (a LangGraph conditional edge)

What is a node?
  A node is just a Python function that:
    - takes the current state as input
    - does some work
    - returns a dict of fields to update in the state

What is a conditional edge?
  After a node runs, LangGraph needs to know which node to go to next.
  A conditional edge is a function that looks at the state and returns
  a string like "ocr" or "extract" — LangGraph uses that to route.
"""

from state import DocumentState
from tools.pdf_reader import read_pdf_text


# ─────────────────────────────────────────
# NODE: Planner
# ─────────────────────────────────────────

def planner_node(state: DocumentState) -> dict:
    """
    Reads the PDF.
    If it has readable text → sets needs_ocr = False
    If it's blank/scanned   → sets needs_ocr = True

    Returns only the fields this node changes.
    LangGraph automatically merges them into the full state.
    """
    print("\n🧠 [PLANNER] Reading PDF to decide next step...")

    text = read_pdf_text(state["pdf_path"])

    if len(text) > 50:
        # PDF has real text — no need to OCR
        print(f"✅ [PLANNER] Found {len(text)} characters. Skipping OCR.")
        return {
            "text": text,
            "needs_ocr": False
        }
    else:
        # PDF has no text — probably a scanned image, route to OCR
        print("⚠️  [PLANNER] No text found. Routing to OCR.")
        return {
            "text": "",
            "needs_ocr": True
        }


# ─────────────────────────────────────────
# CONDITIONAL EDGE: should_ocr
# ─────────────────────────────────────────

def should_ocr(state: DocumentState) -> str:
    """
    Called by LangGraph after the planner node finishes.
    Looks at state["needs_ocr"] and returns a routing string.

    "ocr"     → LangGraph sends execution to the "ocr" node
    "extract" → LangGraph sends execution to the "extract" node (skip OCR)

    In graph.py you'll map these strings to actual node names like:
        { "ocr": "ocr", "extract": "extract" }
    """
    if state["needs_ocr"]:
        return "ocr"
    else:
        return "extract"
