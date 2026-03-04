from __future__ import annotations

import os

import os
import socket
import threading
import time
import sys

import requests
import streamlit as st
import uvicorn

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

DEFAULT_API_URL = "http://127.0.0.1:8000/api/v1"


def _port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) != 0


@st.cache_resource
def _start_backend() -> tuple[str, bool, str | None]:
    host = "127.0.0.1"
    port = 8000 if _port_available(host, 8000) else 8502
    base_url = f"http://{host}:{port}/api/v1"

    from backend.app.main import app as fastapi_app

    thread = threading.Thread(
        target=uvicorn.run,
        kwargs={"app": fastapi_app, "host": host, "port": port, "log_level": "info"},
        daemon=True,
    )
    thread.start()

    health_url = f"{base_url}/health"
    deadline = time.time() + 30
    last_error: str | None = None
    while time.time() < deadline:
        try:
            resp = requests.get(health_url, timeout=2)
            if resp.status_code == 200:
                return base_url, True, None
        except Exception as exc:
            last_error = str(exc)
        time.sleep(0.5)
    return base_url, False, last_error or "Backend did not become ready."


API_URL, backend_ok, backend_error = _start_backend()
if not backend_ok:
    st.error(f"FastAPI backend failed to start: {backend_error}")

st.set_page_config(page_title="RAG Doc Intelligence", page_icon="🧠", layout="wide")

if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = ""
if "model" not in st.session_state:
    st.session_state.model = "gpt-4o-mini"
if "models" not in st.session_state:
    st.session_state.models = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4.1",
        "gpt-4.1-mini",
        "gpt-4.1-nano",
        "o3-mini",
        "o1-mini",
    ]
if "ingest_document_id" not in st.session_state:
    st.session_state.ingest_document_id = ""
if "ingest_status" not in st.session_state:
    st.session_state.ingest_status = None
if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""
if "last_sources" not in st.session_state:
    st.session_state.last_sources = []
if "last_source_ids" not in st.session_state:
    st.session_state.last_source_ids = []

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
:root {
  --bg: #0b0f14;
  --panel: #121923;
  --panel-2: #0f1622;
  --ink: #e9f0ff;
  --muted: #9bb0c6;
  --accent: #5eead4;
  --accent-2: #a78bfa;
  --danger: #f97316;
}
html, body, [class*="stApp"] {
  background: radial-gradient(1200px 800px at 10% -10%, #1e293b 0%, rgba(30,41,59,0) 60%),
              radial-gradient(900px 600px at 90% -20%, #0ea5e9 0%, rgba(14,165,233,0) 55%),
              var(--bg);
  color: var(--ink);
  font-family: "Space Grotesk", system-ui, sans-serif;
}
header, footer { visibility: hidden; }
section[data-testid="stSidebar"] > div { background: #0b111a; }
.title {
  font-size: 38px;
  font-weight: 700;
  letter-spacing: 0.2px;
  margin-bottom: 6px;
}
.subtitle {
  color: var(--muted);
  font-size: 16px;
  margin-bottom: 20px;
}
.card {
  background: linear-gradient(135deg, rgba(18,25,35,0.95), rgba(15,22,34,0.95));
  border: 1px solid rgba(148,163,184,0.15);
  border-radius: 18px;
  padding: 18px;
  box-shadow: 0 10px 30px rgba(2,6,23,0.35);
}
.badge {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(94,234,212,0.15);
  color: var(--accent);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.3px;
}
.pill {
  font-family: "JetBrains Mono", monospace;
  font-size: 12px;
  padding: 4px 8px;
  border: 1px solid rgba(148,163,184,0.2);
  border-radius: 8px;
  color: var(--muted);
}
.stTextInput > div > div > input,
.stFileUploader > div,
.stSelectbox > div > div {
  background: var(--panel-2) !important;
  border-radius: 10px !important;
  border: 1px solid rgba(148,163,184,0.2) !important;
  color: var(--ink) !important;
}
.stButton > button {
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  color: #0b0f14;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  padding: 10px 18px;
}
.stButton > button:disabled {
  background: #1f2937;
  color: #6b7280;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="title">RAG Doc Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ingest PDFs, retrieve evidence, and answer with citations.</div>', unsafe_allow_html=True)

left, right = st.columns([1.05, 1])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<span class="badge">OpenAI Access</span>', unsafe_allow_html=True)
    st.text_input(
        "OpenAI API Key",
        type="password",
        key="openai_api_key",
        help="Stored only in this browser session.",
    )

    cols = st.columns([1, 1])
    with cols[0]:
        if st.button("Load Models"):
            if not st.session_state.openai_api_key:
                st.warning("Enter an OpenAI API key first.")
            else:
                try:
                    resp = requests.get(
                        "https://api.openai.com/v1/models",
                        headers={"Authorization": f"Bearer {st.session_state.openai_api_key}"},
                        timeout=30,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    model_ids = sorted({m["id"] for m in data.get("data", []) if "id" in m})
                    if model_ids:
                        st.session_state.models = model_ids
                        st.success(f"Loaded {len(model_ids)} models.")
                    else:
                        st.warning("No models returned.")
                except Exception as exc:
                    st.error(f"Failed to load models: {exc}")

    with cols[1]:
        st.caption("Pick from the list or type a custom model below.")

    st.selectbox(
        "Model",
        options=st.session_state.models,
        key="model",
    )
    custom_model = st.text_input("Custom model (optional)")
    if custom_model.strip():
        st.session_state.model = custom_model.strip()

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<span class="badge">Quick Status</span>', unsafe_allow_html=True)
    st.write("API URL")
    st.markdown(f'<span class="pill">{API_URL}</span>', unsafe_allow_html=True)
    st.write("Active model")
    st.markdown(f'<span class="pill">{st.session_state.model}</span>', unsafe_allow_html=True)
    if st.session_state.openai_api_key:
        st.success("API key set for this session.")
    else:
        st.warning("API key required to ingest or query.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("")
ingest_col, query_col = st.columns([1, 1])

with ingest_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<span class="badge">Ingest</span>', unsafe_allow_html=True)
    file = st.file_uploader("Upload a PDF", type=["pdf"])
    can_run = bool(st.session_state.openai_api_key)
    if st.button("Ingest", disabled=not can_run) and file:
        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        resp = requests.post(f"{API_URL}/ingest/async", files=files, timeout=60)
        data = resp.json()
        st.session_state.ingest_document_id = data.get("document_id", "")
        st.session_state.ingest_status = data
        st.write(data)

    if st.session_state.ingest_document_id:
        st.markdown("**Ingestion Status**")
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        cols = st.columns([1, 1, 1])
        with cols[0]:
            st.markdown(f'<span class="pill">{st.session_state.ingest_document_id}</span>', unsafe_allow_html=True)
        with cols[1]:
            if st.button("Check Status"):
                status_resp = requests.get(
                    f"{API_URL}/ingest/status/{st.session_state.ingest_document_id}",
                    timeout=30,
                )
                st.session_state.ingest_status = status_resp.json()
        with cols[2]:
            if st.button("Clear"):
                st.session_state.ingest_document_id = ""
                st.session_state.ingest_status = None

        if st.session_state.ingest_status:
            st.write(st.session_state.ingest_status)

        if st.session_state.ingest_status and st.session_state.ingest_status.get("status") in {"pending", "processing"}:
            while True:
                status_resp = requests.get(
                    f"{API_URL}/ingest/status/{st.session_state.ingest_document_id}",
                    timeout=30,
                )
                status = status_resp.json()
                st.session_state.ingest_status = status
                percent = int(status.get("percent") or 0)
                progress_bar.progress(min(100, max(0, percent)))
                status_placeholder.write(f'Ingesting... {percent}% ({status.get("current", 0)}/{status.get("total", 0)})')
                if status.get("status") in {"completed", "failed"}:
                    break
                time.sleep(0.7)
            final_status = st.session_state.ingest_status
            progress_bar.progress(100 if final_status.get("status") == "completed" else percent)
            status_placeholder.write(f'Status: {final_status.get("status")}')
    st.markdown("</div>", unsafe_allow_html=True)

with query_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<span class="badge">Query</span>', unsafe_allow_html=True)
    question = st.text_input("Ask a question")
    can_run = bool(st.session_state.openai_api_key)
    if st.button("Query", disabled=not can_run) and question:
        payload = {"question": question, "model": st.session_state.model}
        if st.session_state.openai_api_key:
            payload["api_key"] = st.session_state.openai_api_key
        resp = requests.post(f"{API_URL}/query", json=payload, timeout=60)
        data = resp.json()
        st.session_state.last_answer = data.get("answer", "")
        st.session_state.last_sources = data.get("sources", [])
        st.session_state.last_source_ids = data.get("source_ids", [])

    if st.session_state.last_answer:
        st.subheader("Answer")
        st.write(st.session_state.last_answer)

        with st.expander("Sources and Details"):
            if st.session_state.last_source_ids:
                st.markdown("**Source IDs**")
                st.write(st.session_state.last_source_ids)
            if st.session_state.last_sources:
                st.markdown("**Sources**")
                for s in st.session_state.last_sources:
                    st.markdown(f"- `{s.get('source_id','')}` — {s.get('label','')}")
                    st.write(s.get("snippet", ""))
    st.markdown("</div>", unsafe_allow_html=True)
