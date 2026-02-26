from __future__ import annotations

from fastapi import FastAPI

from .api.v1.routes.ingest import router as ingest_router
from .api.v1.routes.query import router as query_router
from .core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="RAG Doc Intelligence", version="1.0.0")

    app.include_router(ingest_router, prefix="/api/v1", tags=["ingest"])
    app.include_router(query_router, prefix="/api/v1", tags=["query"])

    return app


app = create_app()
