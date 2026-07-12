"""
AGENTS/VALIDATOR.PY — Validation Node.

The last node before the graph ends.
Checks if the extraction produced a usable result.

Keep it simple for now. Later you can add:
  - Regex checks (e.g., INV-\d{4} format)
  - Confidence scoring
  - Human-in-the-loop approval
  - Auto-retry if validation fails
"""

from state import DocumentState


def validator_node(state: DocumentState) -> dict:
    """
    Simple validation: did we find an invoice number or not?

    State in:  invoice_number
    State out: validated (True/False)
    """
    print("\n✔️  [VALIDATOR] Checking extraction result...")

    invoice_number = state.get("invoice_number", "")

    # Basic check: not empty and not the "failed" sentinel value
    if invoice_number and invoice_number != "NOT_FOUND":
        print(f"✅ [VALIDATOR] Passed! Invoice number: {invoice_number}")
        is_valid = True
    else:
        print("❌ [VALIDATOR] Failed. No invoice number was found.")
        is_valid = False

    return {
        "validated": is_valid
    }
