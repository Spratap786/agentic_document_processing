"""
DB/RABBITMQ_CLIENT.PY — The message queue (replaces Redis's queue role).

WHY RABBITMQ OVER A REDIS LIST?
  Redis BLPOP hands you the message and forgets it. If your worker
  crashes mid-job, that job is GONE.
  RabbitMQ requires the consumer to ACKNOWLEDGE each message after
  processing. Crash before the ack? RabbitMQ re-delivers the message
  to another worker. That's real reliability.

KEY RABBITMQ CONCEPTS (you'll see these in the code):

  Connection  → a TCP connection to the RabbitMQ server
  Channel     → a lightweight "session" inside the connection.
                All operations happen on a channel.
  Queue       → a named mailbox. We declare it durable=True so it
                survives RabbitMQ restarts.
  Publish     → send a message to a queue (the API does this)
  Consume     → subscribe to a queue and get messages pushed to a
                callback function (the worker does this)
  Ack         → "I finished this message, you can delete it."
  Nack        → "I failed — requeue it (or discard it)."
  Prefetch    → how many unacked messages a worker may hold at once.
                We set 1: a worker takes ONE job, finishes it, acks,
                then gets the next. This is what spreads jobs fairly
                across multiple workers.

Library: pika — the standard Python client for RabbitMQ (open source).
"""

import os

import pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

QUEUE_NAME = "doc_jobs"


def _connect():
    """Open a connection + channel and make sure our queue exists."""
    conn = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = conn.channel()

    # durable=True → the queue definition survives a RabbitMQ restart.
    # (Messages also need delivery_mode=Persistent to survive — see publish.)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    return conn, channel


# ── PRODUCER SIDE (used by api.py) ───────────────────────────

def enqueue_job(job_id: str):
    """
    Publish a job_id to the queue. Opens a fresh connection per call —
    fine for our volume; a high-traffic API would keep one open.
    """
    conn, channel = _connect()
    channel.basic_publish(
        exchange="",              # "" = default exchange → routes by queue name
        routing_key=QUEUE_NAME,   # which queue to deliver to
        body=job_id,
        properties=pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent,  # write msg to disk
        ),
    )
    conn.close()


# ── CONSUMER SIDE (used by worker.py) ────────────────────────

def consume_jobs(process_fn):
    """
    Blocking consume loop. For every message:
      1. call process_fn(job_id)
      2. if it returns normally  → ACK  (message deleted)
      3. if it raises            → NACK without requeue
         (the job is already marked 'failed' in Postgres by the worker,
          so requeueing would just fail again in a loop)

    This function never returns — it runs until Ctrl+C.
    """
    conn, channel = _connect()

    # One unacked message per worker at a time → fair distribution
    channel.basic_qos(prefetch_count=1)

    def _callback(ch, method, properties, body):
        job_id = body.decode()
        try:
            process_fn(job_id)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            # process_fn should catch its own errors; this is a safety net
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=_callback)

    print(f"👂 Listening on RabbitMQ queue '{QUEUE_NAME}'...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
        conn.close()
