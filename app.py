"""
APP.PY — Entry point. Run this file to process a document.

Usage:
    python app.py

Make sure you have:
  1. A .env file with OPENAI_API_KEY=sk-...
  2. A PDF at documents/invoice.pdf  (or change the path below)
"""

from dotenv import load_dotenv

# Load OPENAI_API_KEY from .env file into environment variables
# Must be called before importing anything that uses the API key
load_dotenv()

from graph import build_graph
from state import DocumentState


def main():
    print("=" * 55)
    print("   🤖  AI Agentic Document Processing")
    print("=" * 55)

    # Build the compiled LangGraph
    app = build_graph()

    # ── Initial State ────────────────────────────────────────
    # This is the starting state of the graph.
    # Only pdf_path is meaningful at this point.
    # All other fields will be filled in by the agents as they run.
    # ──────────────────────────────────────────────────────────
    initial_state: DocumentState = {
        "pdf_path":      "documents/invoice.pdf",  # ← change this to your PDF
        "text":          "",
        "needs_ocr":     False,
        "invoice_number": "",
        "document_type": "",
        "validated":     False,
    }

    print(f"\n📂 Processing: {initial_state['pdf_path']}\n")

    # ── Run the Graph ────────────────────────────────────────
    # .invoke() starts at the entry point (planner) and runs
    # through the graph until it hits END.
    # Returns the FINAL state after all nodes have run.
    # ──────────────────────────────────────────────────────────
    final_state = app.invoke(initial_state)

    # ── Print Results ─────────────────────────────────────────
    print("\n" + "=" * 55)
    print("   📋  FINAL RESULT")
    print("=" * 55)
    print(f"  Document Type  : {final_state['document_type']}")
    print(f"  Invoice Number : {final_state['invoice_number']}")
    print(f"  OCR Used       : {final_state['needs_ocr']}")
    print(f"  Validated      : {final_state['validated']}")
    print("=" * 55)


if __name__ == "__main__":
    main()
