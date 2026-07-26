"""
DB/REDIS_CLIENT.PY — Redis now does ONE job: caching.
(The queue moved to RabbitMQ — see rabbitmq_client.py.)

Before processing, the worker asks: "have I seen this exact file
before?" (keyed by SHA256 of the file bytes). Cache hit = skip
OCR + LLM entirely and reuse the stored result.
"""

import json
import os

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

r = redis.from_url(REDIS_URL, decode_responses=True)

CACHE_PREFIX = "doc_cache:"      # keys look like: doc_cache:<file_hash>
CACHE_TTL = 60 * 60 * 24         # results expire after 24 hours


def get_cached_result(file_hash: str) -> dict | None:
    raw = r.get(CACHE_PREFIX + file_hash)
    return json.loads(raw) if raw else None


def cache_result(file_hash: str, result: dict):
    r.setex(CACHE_PREFIX + file_hash, CACHE_TTL, json.dumps(result))
