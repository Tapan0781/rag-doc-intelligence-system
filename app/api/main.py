from fastapi import FastAPI

app = FastAPI(title="RAG Doc Intelligence")


@app.get("/health")
def health():
    return {"status": "ok"}
