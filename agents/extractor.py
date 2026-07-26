"""
AGENTS/EXTRACTOR.PY — LLM extraction via local Ollama (fully open source).

Model comes from the OLLAMA_MODEL env var so you can switch without
touching code. Defaults to llama3.2:3b (~2GB, fast).

Pull it once:   ollama pull llama3.2:3b
"""

import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from state import DocumentState

llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
    base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
    temperature=0,
)


def extractor_node(state: DocumentState) -> dict:
    print("📄 [EXTRACTOR] Asking LLM for invoice number...")

    text = state["text"]
    if not text:
        return {"invoice_number": "NOT_FOUND", "document_type": "unknown"}

    messages = [
        SystemMessage(content=(
            "You are a document extraction assistant. "
            "Find the invoice number in the document text. "
            "Reply with ONLY the invoice number, nothing else. "
            "If none exists reply exactly: NOT_FOUND"
        )),
        HumanMessage(content=f"Document text:\n\n{text[:4000]}"),
    ]

    response = llm.invoke(messages)
    invoice_number = response.content.strip()

    print(f"✅ [EXTRACTOR] Result: {invoice_number}")
    return {"invoice_number": invoice_number, "document_type": "invoice"}
