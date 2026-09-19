"""
Cognee integration.

This is the piece the Streamlit prototype was built around: `cognee.add` ->
`cognee.cognify` -> `cognee.search`. It is kept, but demoted from "the engine"
to "one of two engines", because Cognee returns prose and the frontend
contract in `src/types/index.ts` requires structured records - evidence with
ids and dates, typed nodes, typed edges. Prose cannot be cast into that shape
without inventing the ids.

So the division of labour is:

  * `GraphStore` decides *which* records answer a question. Deterministic,
    reproducible, always available.
  * Cognee, when configured, phrases the answer over those records and holds
    ingested documents for semantic recall.

Every entry point here degrades to `None` rather than raising, so a missing
package, a missing key or a slow call never takes an endpoint down.
"""

from __future__ import annotations

import asyncio
import logging
import os
import threading

from .config import settings

log = logging.getLogger("graymatter.cognee")

_import_lock = threading.Lock()
_cognee = None
_import_failed = False
_configured = False

#: Consecutive search failures before the engine stops being consulted.
#: Cognee raises a 422 SearchPreconditionError until something has been
#: cognified, and re-learning that on every request costs seconds per answer
#: for a result that is thrown away. The seeded graph answers either way, so
#: the breaker trades a stale-by-one-request retry for a fast response.
_FAILURE_LIMIT = 2
_search_failures = 0
_search_disabled = False


def _apply_env() -> None:
    """
    Cognee reads its configuration from the process environment at import
    time, which is why these are set rather than passed.
    """
    os.environ.setdefault("LLM_API_KEY", settings.llm_api_key)
    os.environ.setdefault("LLM_PROVIDER", settings.llm_provider)
    os.environ.setdefault("LLM_MODEL", settings.llm_model)
    os.environ.setdefault("EMBEDDING_PROVIDER", settings.embedding_provider)
    os.environ.setdefault("EMBEDDING_MODEL", settings.embedding_model)
    os.environ.setdefault(
        "EMBEDDING_DIMENSIONS", str(settings.embedding_dimensions)
    )


def get_cognee():
    """
    Import Cognee lazily. It pulls in a large dependency tree and, on a cold
    start, downloads the embedding model - neither belongs in the import path
    of a service whose seeded graph works without it.
    """
    global _cognee, _import_failed, _configured

    if _import_failed or not settings.cognee_enabled:
        return None
    if _cognee is not None:
        return _cognee

    with _import_lock:
        if _cognee is not None:
            return _cognee
        if _import_failed:
            return None

        try:
            _apply_env()
            import cognee  # noqa: PLC0415 - deliberately deferred

            _cognee = cognee
            _configured = True
            log.info("Cognee ready (provider=%s model=%s)", settings.llm_provider, settings.llm_model)
        except Exception as error:  # pragma: no cover - environment dependent
            _import_failed = True
            log.warning("Cognee unavailable, using the seeded graph only: %s", error)
            return None

    return _cognee


def available() -> bool:
    return get_cognee() is not None


def status() -> dict:
    """Reported by `GET /health/detail` so the console can show what is live."""
    return {
        "cognee_enabled": settings.cognee_enabled,
        "cognee_loaded": _cognee is not None,
        "llm_configured": settings.llm_configured,
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model,
        "embedding_provider": settings.embedding_provider,
        "embedding_model": settings.embedding_model,
        "llm_answers": (
            settings.use_llm_answers
            and settings.llm_configured
            and not _search_disabled
        ),
        "search_disabled": _search_disabled,
    }


async def _call(coro, label: str) -> tuple[bool, object]:
    """
    Run a Cognee coroutine under a timeout.

    Returns `(ok, value)` rather than just the value: `cognee.add()` returns
    None on success, so None cannot be used to signal failure.
    """
    try:
        value = await asyncio.wait_for(coro, timeout=settings.cognee_timeout_s)
        return True, value
    except asyncio.TimeoutError:
        log.warning("Cognee %s timed out after %ss", label, settings.cognee_timeout_s)
    except Exception as error:
        log.warning("Cognee %s failed: %s", label, error)
    return False, None


async def add_text(text: str) -> bool:
    """Add raw text to the Cognee corpus. Returns whether it landed."""
    cognee = get_cognee()
    if cognee is None:
        return False
    ok, _ = await _call(cognee.add(text), "add")
    return ok


async def cognify() -> bool:
    """Build the knowledge graph over everything added so far."""
    cognee = get_cognee()
    if cognee is None:
        return False
    ok, _ = await _call(cognee.cognify(), "cognify")
    return ok


async def ingest(text: str) -> bool:
    """`add` then `cognify`, the pairing the Streamlit pages always used."""
    cognee = get_cognee()
    if cognee is None:
        return False

    added, _ = await _call(cognee.add(text), "add")
    if not added:
        return False
    built, _ = await _call(cognee.cognify(), "cognify")
    return built


async def search(query: str) -> list[str]:
    """
    Free-text recall over the Cognee graph.

    Cognee has returned several result shapes across versions - bare strings,
    dicts with a `search_result` list, objects with a `.text`. All of them are
    flattened to strings here so callers never branch on the version.
    """
    global _search_failures, _search_disabled

    if _search_disabled:
        return []

    cognee = get_cognee()
    if cognee is None:
        return []

    ok, results = await _call(cognee.search(query_text=query), "search")

    if not ok:
        _search_failures += 1
        if _search_failures >= _FAILURE_LIMIT:
            _search_disabled = True
            log.warning(
                "Cognee search failed %s times; falling back to the seeded "
                "graph for the rest of this process. Run "
                "`python scripts/cognify.py` to build the Cognee graph, then "
                "restart.",
                _search_failures,
            )
        return []

    _search_failures = 0

    if not results:
        return []

    flattened: list[str] = []

    def absorb(value) -> None:
        if value is None:
            return
        if isinstance(value, str):
            text = value.strip()
            if text:
                flattened.append(text)
        elif isinstance(value, dict):
            if "search_result" in value:
                absorb(value["search_result"])
            elif "text" in value:
                absorb(value["text"])
            else:
                for nested in value.values():
                    absorb(nested)
        elif isinstance(value, (list, tuple, set)):
            for nested in value:
                absorb(nested)
        else:
            text = getattr(value, "text", None)
            absorb(text if isinstance(text, str) else str(value))

    absorb(results)
    return flattened
