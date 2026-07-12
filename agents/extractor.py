"""
AGENTS/EXTRACTOR.PY — LLM Extraction Node.

THIS is where LangChain comes in.

What is LangChain here?
  LangChain is a library that makes it easy to talk to LLMs.
  Without it you'd write raw HTTP requests to the model.
  With LangChain you just do:
    llm = ChatOllama(...)
    response = llm.invoke([messages])

  The HUGE benefit: SystemMessage, HumanMessage, llm.invoke(), response.content
  all work IDENTICALLY no matter which LLM you use (Ollama, OpenAI, Gemini...).
  Swapping the model = changing 2 lines.

Key LangChain concepts used here:

  ChatOllama    → LangChain wrapper that talks to your local Ollama server
                  Ollama runs on localhost:11434 — no API key, no internet needed

  SystemMessage → The "instructions" you give the LLM before the conversation
                  (who it is, what to do, how to format the answer)

  HumanMessage  → The actual user input — in our case, the document text

  llm.invoke()  → Sends the messages to the LLM and returns the response
  response.content → The text the LLM replied with

Available lightweight models (pick one):
  phi3.5       — Microsoft, ~2GB, great at following instructions
  llama3.2:3b  — Meta 3B, fast and capable
  gemma2:2b    — Google 2B, very small footprint
  mistral      — Mistral 7B, best quality but heavier (~4GB)

Pull a model first:  ollama pull phi3.5
Start Ollama server: ollama serve
"""

from state import DocumentState

# ── LangChain + Ollama ─────────────────────────────────────────────────
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

# ── Want to switch back to OpenAI? Comment the two lines above and use:
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
#
# Want Gemini?
# from langchain_google_genai import ChatGoogleGenerativeAI
# llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
# ──────────────────────────────────────────────────────────────────────

# Initialize the LLM — points to your local Ollama server, no API key needed
llm = ChatOllama(
    model="phi3.5",  # Change to "llama3.2:3b" or any model you've pulled
    temperature=0    # 0 = no randomness, we want consistent structured output
)


def extractor_node(state: DocumentState) -> dict:
    """
    Sends the document text to the LLM and asks it to find the invoice number.

    State in:  text (the full document text from PDF reader or OCR)
    State out: invoice_number, document_type
    """
    print("\n📄 [EXTRACTOR] Asking LLM to extract invoice number...")

    text = state["text"]

    if not text:
        print("❌ [EXTRACTOR] No text to extract from.")
        return {
            "invoice_number": "NOT_FOUND",
            "document_type": "unknown"
        }

    # Build the messages to send to the LLM
    # SystemMessage = role instructions (background, format rules)
    # HumanMessage  = the actual input data (document text)
    messages = [
        SystemMessage(content="""You are a document extraction assistant.
Your job is to find the invoice number in the given document text.

Rules:
- Reply with ONLY the invoice number (e.g. INV-1042 or 2024-00891)
- Do not include any explanation, labels, or extra words
- If you cannot find an invoice number, reply with exactly: NOT_FOUND
"""),
        HumanMessage(content=f"Document text:\n\n{text}")
    ]

    # Call the LLM and get back a response object
    response = llm.invoke(messages)

    # response.content is the raw string the LLM returned
    invoice_number = response.content.strip()

    print(f"✅ [EXTRACTOR] Invoice number found: {invoice_number}")

    return {
        "invoice_number": invoice_number,
        "document_type": "invoice"
    }
