"""
DB/POSTGRES.PY — Job tracking in PostgreSQL.

WHY POSTGRES HERE?
  Job records are structured, relational data with a fixed schema:
  every job has an id, filename, status, timestamps. You'll query them
  with filters ("show me failed jobs today") — exactly what SQL is for.

The `jobs` table is the source of truth for job STATUS.
The extracted CONTENT lives in MongoDB (flexible shape).
"""

import os
import uuid
from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import RealDictCursor

POSTGRES_URL = os.getenv(
    "POSTGRES_URL",
    "postgresql://docuser:docpass@localhost:5432/docdb",
)


def get_conn():
    return psycopg2.connect(POSTGRES_URL, cursor_factory=RealDictCursor)


def init_db():
    """Create the jobs table if it doesn't exist. Called once at startup."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id          UUID PRIMARY KEY,
                filename    TEXT NOT NULL,
                file_hash   TEXT NOT NULL,
                status      TEXT NOT NULL DEFAULT 'queued',
                -- queued → processing → done | failed
                error       TEXT,
                created_at  TIMESTAMPTZ NOT NULL,
                updated_at  TIMESTAMPTZ NOT NULL
            );
        """)
        conn.commit()


def create_job(filename: str, file_hash: str) -> str:
    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO jobs (id, filename, file_hash, status, created_at, updated_at)
               VALUES (%s, %s, %s, 'queued', %s, %s)""",
            (job_id, filename, file_hash, now, now),
        )
        conn.commit()
    return job_id


def update_status(job_id: str, status: str, error: str | None = None):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """UPDATE jobs SET status = %s, error = %s, updated_at = %s
               WHERE id = %s""",
            (status, error, datetime.now(timezone.utc), job_id),
        )
        conn.commit()


def get_job(job_id: str):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
        return cur.fetchone()


def list_jobs(limit: int = 50):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM jobs ORDER BY created_at DESC LIMIT %s", (limit,)
        )
        return cur.fetchall()
