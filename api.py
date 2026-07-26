"""
API.PY — FastAPI backend.

The API's job is deliberately SMALL:
  1. Accept a PDF upload
  2. Save it to disk
  3. Create a job row in Postgres (status = queued)
  4. Push the job_id onto the Redis queue
  5. Return the job_id immediately  ← the request never waits for the LLM

The heavy lifting (OCR, LLM) happens in worker.py.
This is what makes the system feel instant no matter how slow the model is.

Run:  uvicorn api:app --reload --port 8000
Docs: http://localhost:8000/docs   (auto-generated Swagger UI — try it!)
"""

import hashlib
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile

from db import mongo, postgres, rabbitmq_client

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Agentic Document Processing API", version="0.1.0")


@app.on_event("startup")
def startup():
    postgres.init_db()   # create tables if missing


@app.get("/health")
def health():
    """Quick check that the API is alive. Later: check DB connections too."""
    return {"status": "ok"}


@app.post("/upload")
async def upload(file: UploadFile):
    """
    Accept a PDF → queue it for processing → return job_id instantly.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted")

    content = await file.read()

    # Hash the file bytes — used as the cache key so identical
    # files are never processed twice
    file_hash = hashlib.sha256(content).hexdigest()

    # Save to disk under the hash (avoids filename collisions)
    pdf_path = UPLOAD_DIR / f"{file_hash}.pdf"
    pdf_path.write_bytes(content)

    # 1. Record the job in Postgres
    job_id = postgres.create_job(file.filename, file_hash)

    # 2. Publish onto the RabbitMQ queue for the worker
    rabbitmq_client.enqueue_job(job_id)

    return {"job_id": job_id, "status": "queued"}


@app.get("/jobs")
def jobs():
    """List recent jobs (from Postgres)."""
    return postgres.list_jobs()


@app.get("/jobs/{job_id}")
def job_status(job_id: str):
    """Status of one job (Postgres) + its result if done (MongoDB)."""
    job = postgres.get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    result = None
    if job["status"] == "done":
        extraction = mongo.get_extraction(job_id)
        result = extraction["result"] if extraction else None

    return {"job": job, "result": result}
