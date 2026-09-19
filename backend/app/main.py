"""
Gray Matter API.

The FastAPI service the Next.js frontend was written against. Every route
returns exactly the shape declared in `src/types/index.ts`; `src/api/client.ts`
is the client for it, and `src/api/mock/transport.ts` is the in-memory stand-in
that these routes replace.

Run it with:

    uvicorn app.main:app --reload --port 8000     (from backend/)
"""

from __future__ import annotations

import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .cognee_engine import status as engine_status
from .config import settings
from .graph.store import store
from .schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    AskRequest,
    AskResponse,
    DecisionDetail,
    DecisionsResponse,
    HealthResponse,
    IngestResponse,
    IngestTextRequest,
)
from .services import ask as ask_service
from .services import analyze as analyze_service
from .services import decisions as decisions_service
from .services import ingest as ingest_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("graymatter")

@asynccontextmanager
async def lifespan(_: FastAPI):
    counts = store.counts()
    log.info(
        "Graph ready: %(sources)s sources, %(entities)s entities, "
        "%(relationships)s relationships, %(decisions)s decisions, "
        "%(conflicts)s conflicts",
        counts,
    )
    if not settings.llm_configured:
        log.info(
            "No LLM_API_KEY set. Answers are composed from retrieved evidence; "
            "structured responses are unaffected."
        )
    yield


app = FastAPI(
    title="Gray Matter API",
    version="1.0.0",
    description=(
        "Decision provenance over a company knowledge graph. Serves the "
        "contract in src/types/index.ts."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Contract routes - these five are what the frontend calls
# ---------------------------------------------------------------------------


@app.get("/health", response_model=HealthResponse)
async def health() -> dict:
    return {"status": "ok", **store.counts()}


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> dict:
    return await ask_service.ask(store, request.question)


@app.get("/decisions", response_model=DecisionsResponse)
async def list_decisions() -> dict:
    return decisions_service.list_decisions(store)


@app.get("/decisions/{decision_id}", response_model=DecisionDetail)
async def get_decision(decision_id: str) -> dict:
    try:
        return decisions_service.get_decision(store, decision_id)
    except decisions_service.DecisionNotFound:
        # The frontend maps 404 to its own "not in the knowledge graph" copy.
        raise HTTPException(
            status_code=404, detail=f"No decision {decision_id}."
        ) from None


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> dict:
    return analyze_service.analyze(store, request.change)


# ---------------------------------------------------------------------------
# Operator routes - used by the Streamlit console, not by the Next.js app
# ---------------------------------------------------------------------------


@app.get("/health/detail")
async def health_detail() -> dict:
    return {"status": "ok", **store.counts(), "engine": engine_status()}


@app.post("/ingest/text", response_model=IngestResponse)
async def ingest_text(request: IngestTextRequest) -> dict:
    try:
        return await ingest_service.ingest_text(
            store,
            text=request.text,
            title=request.title,
            source_type=request.source_type,
            date=request.date,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/sources")
async def list_sources() -> dict:
    """Backs the console's Knowledge Explorer."""
    return {
        "sources": [
            {
                "id": s.id,
                "type": s.type,
                "title": s.title,
                "date": s.date,
                "snippet": s.snippet,
                "linked_entities": sorted(
                    store.entities[n].name
                    for n in store.neighbours(s.id)
                    if n in store.entities
                ),
            }
            for s in sorted(
                store.sources.values(), key=lambda r: r.date, reverse=True
            )
        ]
    }


@app.get("/entities")
async def list_entities() -> dict:
    return {
        "entities": [
            {"id": e.id, "type": e.type, "name": e.name}
            for e in store.entities.values()
        ]
    }


@app.get("/conflicts")
async def list_conflicts() -> dict:
    """Standing disagreements in the graph, independent of any proposed change."""
    out = []
    for index, (left, right) in enumerate(store.standing_conflicts(), start=1):
        entity = store.entities[left.entity_id]
        out.append(
            {
                "id": f"CFL-{index:03d}",
                "entity": entity.name,
                "attribute": left.attribute,
                "values": [
                    {"value": left.value, "asserted_by": left.asserted_by},
                    {"value": right.value, "asserted_by": right.asserted_by},
                ],
            }
        )
    return {"conflicts": out}
