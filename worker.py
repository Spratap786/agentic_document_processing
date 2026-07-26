"""
WORKER.PY — The background worker. This is where everything connects.

For every message RabbitMQ delivers:
  1. Load the job from Postgres → mark status 'processing'
  2. CACHE CHECK (Redis): seen this file hash before? → reuse result
  3. Otherwise run the LangGraph (planner → ocr? → extract → validate)
  4. Save result to MongoDB + cache it in Redis
  5. Mark job 'done' (or 'failed' with the error) in Postgres
  6. The rabbitmq_client then ACKs the message → RabbitMQ deletes it

RELIABILITY WIN vs the old Redis queue: if this worker crashes
mid-job, the message was never acked — RabbitMQ re-delivers it
to another worker automatically. No lost jobs.

Run:  python worker.py
Multiple workers in parallel still works: prefetch_count=1 makes
RabbitMQ hand each worker one job at a time, round-robin.
"""

import os
import traceback
from pathlib import Path

from db import mongo, postgres, rabbitmq_client, redis_client
from graph import build_graph

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))

app_graph = build_graph()   # compile once, reuse for every job


def process_job(job_id: str):
    job = postgres.get_job(job_id)
    if not job:
        print(f"⚠️  Job {job_id} not found in Postgres, skipping")
        return

    print(f"\n{'=' * 50}\n🏗️  Processing job {job_id} ({job['filename']})")
    postgres.update_status(job_id, "processing")

    try:
        file_hash = job["file_hash"]

        # ── CACHE CHECK (Redis) ─────────────────────────
        cached = redis_client.get_cached_result(file_hash)
        if cached:
            print("⚡ Cache hit! Reusing previous result — no OCR, no LLM.")
            mongo.save_extraction(job_id, cached)
            postgres.update_status(job_id, "done")
            return

        # ── RUN THE LANGGRAPH ───────────────────────────
        pdf_path = UPLOAD_DIR / f"{file_hash}.pdf"
        initial_state = {
            "pdf_path": str(pdf_path),
            "text": "",
            "needs_ocr": False,
            "invoice_number": "",
            "document_type": "",
            "validated": False,
        }
        final_state = app_graph.invoke(initial_state)

        result = {
            "invoice_number": final_state["invoice_number"],
            "document_type": final_state["document_type"],
            "validated": final_state["validated"],
            "ocr_used": final_state["needs_ocr"],
            "text_length": len(final_state["text"]),
        }

        # ── STORE ───────────────────────────────────────
        mongo.save_extraction(job_id, result)          # full result → Mongo
        redis_client.cache_result(file_hash, result)   # cache → Redis
        postgres.update_status(job_id, "done")         # status  → Postgres

        print(f"✅ Job {job_id} done: {result['invoice_number']}")

    except Exception as e:
        print(f"❌ Job {job_id} failed: {e}")
        traceback.print_exc()
        postgres.update_status(job_id, "failed", error=str(e))


def main():
    print("👷 Worker started. (Ctrl+C to stop)")
    postgres.init_db()

    # Hand our process_job function to RabbitMQ as the callback.
    # RabbitMQ PUSHES each message to it, one at a time (prefetch=1),
    # and acks/nacks based on whether it raised. Blocks forever.
    rabbitmq_client.consume_jobs(process_job)


if __name__ == "__main__":
    main()
