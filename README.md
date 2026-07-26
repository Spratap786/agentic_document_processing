# Agentic Document Processing — v1

Upload a PDF → agent pipeline (LangGraph + local LLM) extracts the invoice
number → results stored across Postgres/Mongo/Redis → viewed in Streamlit.

Everything is open source. No API keys. Runs fully on your machine.

## Architecture

```
Streamlit UI (8501)
      │  HTTP
      ▼
FastAPI (8000) ──── Postgres (job records)
      │
      │ publish job_id
      ▼
RabbitMQ queue ──► Worker ──► LangGraph ──► Ollama (local LLM)
   (5672)            │
                     ├──► MongoDB (extraction results)
                     ├──► Redis   (cache by file hash ONLY)
                     └──► Postgres (status updates)

RabbitMQ dashboard: http://localhost:15672  (guest / guest)
```

## Prerequisites

1. **Python 3.11+**
2. **Docker Desktop** (for the databases)
3. **Ollama** — install from https://ollama.com then:
   ```
   ollama pull llama3.2:3b
   ```
4. **Tesseract** (only needed for scanned PDFs):
   - Ubuntu: `sudo apt install tesseract-ocr`
   - Mac: `brew install tesseract`
   - Windows: https://github.com/UB-Mannheim/tesseract/wiki

## Setup (once)

```bash
# 1. Virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install Python deps
pip install -r requirements.txt

# 3. Env file
cp .env.example .env            # Windows: copy .env.example .env

# 4. Start the databases + RabbitMQ
docker compose up -d
docker compose ps               # all 4 should say "running"

# 5. Create a test PDF
python create_sample_invoice.py
```

## Run (3 terminals + Ollama)

Make sure Ollama is running (`ollama serve`, or the desktop app).

**Terminal 1 — API**
```bash
uvicorn api:app --reload --port 8000
```

**Terminal 2 — Worker**
```bash
python worker.py
```

**Terminal 3 — UI**
```bash
streamlit run ui.py
```

Open http://localhost:8501 → upload `documents/invoice.pdf` → watch
the worker terminal process it → result appears in the UI.

## Things to try

- Upload the SAME file twice → second time is instant (Redis cache hit —
  watch the worker log say "Cache hit!")
- Open http://localhost:8000/docs → FastAPI's auto-generated Swagger UI,
  try the endpoints directly
- Kill the worker mid-processing (Ctrl+C during the LLM step), restart it
  → the unacked message is RE-DELIVERED and the job completes. This is
  the reliability RabbitMQ buys you over a plain Redis queue.
- Open http://localhost:15672 (guest/guest) → watch the doc_jobs queue:
  upload with the worker STOPPED and see messages pile up, then start
  the worker and watch them drain.
- Run TWO workers in two terminals → RabbitMQ round-robins jobs between
  them (prefetch_count=1 = fair dispatch)

## Inspect the databases directly

```bash
# Postgres — see job records
docker compose exec postgres psql -U docuser -d docdb -c "SELECT id, filename, status FROM jobs;"

# Mongo — see extraction results
docker compose exec mongo mongosh docdb --eval "db.extractions.find().pretty()"

# Redis — see cached results and queue
docker compose exec redis redis-cli KEYS '*'
```

## What's NOT in v1 (on purpose)

- MCP servers        → Phase 5 (after architecture is stable)
- Vector DB          → added when we build "search similar documents"
- Docker for the app → Phase 3 (deployment)
- Grafana/Prometheus → Phase 4 (monitoring)
- LLM-driven planner → currently rule-based; upgrading it is Phase 2
