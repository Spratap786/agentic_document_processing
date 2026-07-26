"""
UI.PY — Streamlit frontend. Pure Python, zero HTML/CSS/JS.

The UI talks ONLY to the FastAPI backend over HTTP — it never touches
the databases directly. This separation matters: later you can replace
Streamlit with React (or anything) without changing the backend at all.

Run:  streamlit run ui.py
Open: http://localhost:8501
"""

import os
import time

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Document Processor", page_icon="📄")
st.title("📄 Agentic Document Processing")
st.caption("Upload a PDF → the agent pipeline extracts the invoice number")

# ── Upload section ───────────────────────────────────────
uploaded = st.file_uploader("Upload an invoice PDF", type=["pdf"])

if uploaded and st.button("Process document", type="primary"):
    with st.spinner("Uploading..."):
        resp = requests.post(
            f"{API_URL}/upload",
            files={"file": (uploaded.name, uploaded.getvalue(), "application/pdf")},
            timeout=30,
        )

    if resp.status_code != 200:
        st.error(f"Upload failed: {resp.text}")
    else:
        job_id = resp.json()["job_id"]
        st.success(f"Queued! Job ID: `{job_id}`")

        # Poll the job status every 2 seconds until done/failed
        placeholder = st.empty()
        for _ in range(60):  # max ~2 minutes
            job_resp = requests.get(f"{API_URL}/jobs/{job_id}", timeout=10).json()
            status = job_resp["job"]["status"]

            if status == "done":
                placeholder.success("✅ Done!")
                st.subheader("Extraction result")
                st.json(job_resp["result"])
                break
            elif status == "failed":
                placeholder.error(f"❌ Failed: {job_resp['job']['error']}")
                break
            else:
                placeholder.info(f"⏳ Status: {status} ...")
                time.sleep(2)

st.divider()

# ── Job history section ──────────────────────────────────
st.subheader("Recent jobs")
if st.button("Refresh"):
    pass  # clicking any button reruns the script, refreshing the table below

try:
    jobs = requests.get(f"{API_URL}/jobs", timeout=10).json()
    if jobs:
        st.dataframe(
            [
                {
                    "Job ID": j["id"][:8],
                    "File": j["filename"],
                    "Status": j["status"],
                    "Created": j["created_at"],
                }
                for j in jobs
            ],
            use_container_width=True,
        )
    else:
        st.info("No jobs yet. Upload a PDF above!")
except requests.ConnectionError:
    st.error(f"Cannot reach the API at {API_URL}. Is `uvicorn api:app` running?")
