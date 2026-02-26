from __future__ import annotations

import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

st.title("RAG Doc Intelligence")

st.header("Ingest PDF")
file = st.file_uploader("Upload a PDF", type=["pdf"])
if st.button("Ingest") and file:
    files = {"file": (file.name, file.getvalue(), "application/pdf")}
    resp = requests.post(f"{API_URL}/ingest", files=files, timeout=60)
    st.write(resp.json())

st.header("Ask a question")
question = st.text_input("Question")
if st.button("Query") and question:
    resp = requests.post(f"{API_URL}/query", json={"question": question}, timeout=60)
    st.write(resp.json())
