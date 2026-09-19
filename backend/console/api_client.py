"""
HTTP client for the console.

The console talks to the API over HTTP rather than importing `app` directly.
That keeps one process owning the graph: if the console mutated its own
in-process copy, ingesting a document here would not show up in the Next.js
app, and the two would drift the way the Streamlit prototype and the frontend
already had.
"""

from __future__ import annotations

import os

import requests

BASE_URL = os.environ.get("GRAYMATTER_API", "http://127.0.0.1:8000")
TIMEOUT = 60


class ApiError(RuntimeError):
    """Any failure reaching or reading the API."""


def _request(method: str, path: str, **kwargs):
    try:
        response = requests.request(
            method, f"{BASE_URL}{path}", timeout=TIMEOUT, **kwargs
        )
    except requests.RequestException as error:
        raise ApiError(
            f"Could not reach the Gray Matter API at {BASE_URL}. "
            "Start it with: uvicorn app.main:app --reload --port 8000"
        ) from error

    if not response.ok:
        detail = ""
        try:
            detail = response.json().get("detail", "")
        except ValueError:
            detail = response.text[:200]
        raise ApiError(f"{method} {path} returned {response.status_code}. {detail}")

    try:
        return response.json()
    except ValueError as error:
        raise ApiError(f"{method} {path} did not return JSON.") from error


def health() -> dict:
    return _request("GET", "/health/detail")


def ask(question: str) -> dict:
    return _request("POST", "/ask", json={"question": question})


def analyze(change: str) -> dict:
    return _request("POST", "/analyze", json={"change": change})


def decisions() -> list[dict]:
    return _request("GET", "/decisions")["decisions"]


def decision(decision_id: str) -> dict:
    return _request("GET", f"/decisions/{decision_id}")


def sources() -> list[dict]:
    return _request("GET", "/sources")["sources"]


def entities() -> list[dict]:
    return _request("GET", "/entities")["entities"]


def conflicts() -> list[dict]:
    return _request("GET", "/conflicts")["conflicts"]


def ingest_text(
    text: str,
    title: str,
    source_type: str = "document",
    date: str | None = None,
) -> dict:
    return _request(
        "POST",
        "/ingest/text",
        json={
            "text": text,
            "title": title,
            "source_type": source_type,
            "date": date,
        },
    )
