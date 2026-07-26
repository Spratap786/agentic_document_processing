"""
AGENTS/VALIDATOR.PY — Final check before the graph ends.
"""

from state import DocumentState


def validator_node(state: DocumentState) -> dict:
    print("✔️  [VALIDATOR] Checking result...")
    inv = state.get("invoice_number", "")
    is_valid = bool(inv) and inv != "NOT_FOUND"
    print(f"{'✅ Passed' if is_valid else '❌ Failed'}")
    return {"validated": is_valid}
