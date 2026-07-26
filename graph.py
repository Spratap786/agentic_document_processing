"""
GRAPH.PY — Assembles the LangGraph (same graph as before).

    planner ──(needs_ocr?)──> ocr ──> extract ──> validate ──> END
                    └──────────────────^
"""

from langgraph.graph import END, StateGraph

from agents.extractor import extractor_node
from agents.ocr import ocr_node
from agents.planner import planner_node, should_ocr
from agents.validator import validator_node
from state import DocumentState


def build_graph():
    graph = StateGraph(DocumentState)

    graph.add_node("planner", planner_node)
    graph.add_node("ocr", ocr_node)
    graph.add_node("extract", extractor_node)
    graph.add_node("validate", validator_node)

    graph.set_entry_point("planner")

    graph.add_conditional_edges(
        "planner",
        should_ocr,
        {"ocr": "ocr", "extract": "extract"},
    )
    graph.add_edge("ocr", "extract")
    graph.add_edge("extract", "validate")
    graph.add_edge("validate", END)

    return graph.compile()
