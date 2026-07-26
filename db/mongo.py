"""
DB/MONGO.PY — Extracted results in MongoDB.

WHY MONGO HERE?
  Each document type produces differently-shaped output:
    invoice  → {invoice_number, vendor, total, line_items[]}
    contract → {parties[], effective_date, clauses[]}
  A rigid SQL schema fights this. A document DB stores whatever
  JSON the extractor produces — no migrations needed when you add
  new document types later.
"""

import os
from datetime import datetime, timezone

from pymongo import MongoClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

_client = MongoClient(MONGO_URL)
_collection = _client["docdb"]["extractions"]


def save_extraction(job_id: str, result: dict):
    """Store the full extraction result for a job."""
    _collection.insert_one({
        "job_id": job_id,
        "result": result,
        "created_at": datetime.now(timezone.utc),
    })


def get_extraction(job_id: str) -> dict | None:
    doc = _collection.find_one({"job_id": job_id}, {"_id": 0})
    return doc
