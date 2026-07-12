"""
GRAPH.PY — Assembles the LangGraph.

What is LangGraph?
  LangGraph lets you define a workflow as a graph:
    - Nodes = functions (agents) that do work
    - Edges = arrows that say "after this node, go to that node"
    - Conditional edges = smart arrows: "after this node, go WHERE?"

The graph we're building today:

    ┌──────────────────────┐
    │       PLANNER        │  ← entry point
    └──────────────────────┘
              │
        (needs_ocr?)
         /         \
        Yes         No
        │           │
    ┌───┴───┐       │
    │  OCR  │       │
    └───────┘       │
        │           │
        └─────┬─────┘
              ▼
    ┌──────────────────────┐
    │      EXTRACTOR       │
    └──────────────────────┘
              │
              ▼
    ┌──────────────────────┐
    │      VALIDATOR       │
    └──────────────────────┘
              │
              ▼
            END
"""

from langgraph.graph import StateGraph, END

from state import DocumentState
from agents.planner import planner_node, should_ocr
from agents.ocr import ocr_node
from agents.extractor import extractor_node
from agents.validator import validator_node


def build_graph():
    """
    Build and compile the LangGraph.
    Call this once in app.py to get a runnable app.
    """

    # Step 1: Create the graph
    # Pass DocumentState so LangGraph knows the shape of the state dict
    graph = StateGraph(DocumentState)

    # ─────────────────────────────────────────────────────────────────
    # Step 2: Register nodes
    # Format: graph.add_node("node_name", function)
    # The "node_name" string is what you use when defining edges
    # ─────────────────────────────────────────────────────────────────
    graph.add_node("planner", planner_node)
    graph.add_node("ocr",     ocr_node)
    graph.add_node("extract", extractor_node)
    graph.add_node("validate", validator_node)

    # ─────────────────────────────────────────────────────────────────
    # Step 3: Set the entry point
    # This is the first node that runs when you call app.invoke(state)
    # ─────────────────────────────────────────────────────────────────
    graph.set_entry_point("planner")

    # ─────────────────────────────────────────────────────────────────
    # Step 4: Add edges
    # ─────────────────────────────────────────────────────────────────

    # CONDITIONAL EDGE from planner
    # After "planner" runs, call should_ocr(state)
    # should_ocr returns "ocr" or "extract"
    # The dict maps those strings to node names
    graph.add_conditional_edges(
        "planner",       # From node
        should_ocr,      # Routing function — receives state, returns a string
        {
            "ocr":     "ocr",      # "ocr"     → go to the ocr node
            "extract": "extract",  # "extract" → skip ocr, go to extract
        }
    )

    # REGULAR EDGES (always follow this path, no condition)
    graph.add_edge("ocr",      "extract")   # After OCR → always go to extract
    graph.add_edge("extract",  "validate")  # After extract → always validate
    graph.add_edge("validate", END)         # After validate → we're done

    # ─────────────────────────────────────────────────────────────────
    # Step 5: Compile
    # This locks in the graph structure and returns a runnable object
    # ─────────────────────────────────────────────────────────────────
    return graph.compile()
