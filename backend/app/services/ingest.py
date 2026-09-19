"""
Ingestion.

Carries over the four input kinds from the Streamlit Data Ingestion page -
spreadsheet, document, form, voice - but writes to both stores: the relational
`GraphStore` (so the new source is citable, linkable and countable
immediately) and Cognee (so it is semantically recallable, when configured).

The graph write is the one that must succeed. Cognee is best-effort, and the
response says which of the two happened rather than claiming success for both.
"""

from __future__ import annotations

import datetime as dt
import logging

from .. import cognee_engine
from ..graph.store import GraphStore

log = logging.getLogger("graymatter.ingest")


def rows_to_text(rows: list[dict]) -> str:
    """
    Flatten tabular rows into one line each.

    Same shape the Streamlit page produced - "column: value, column: value" -
    because it reads as a sentence to an embedding model, which a CSV dump
    does not.
    """
    lines: list[str] = []
    for row in rows:
        rendered = ", ".join(f"{key}: {value}" for key, value in row.items())
        if rendered:
            lines.append(rendered)
    return "\n".join(lines)


def form_to_text(fields: dict) -> str:
    return "\n".join(f"{key}: {value}" for key, value in fields.items() if value)


async def ingest_text(
    store: GraphStore,
    *,
    text: str,
    title: str,
    source_type: str = "document",
    date: str | None = None,
) -> dict:
    text = text.strip()
    if not text:
        raise ValueError("Nothing to ingest: the text is empty.")

    record = store.add_source(
        title=title.strip() or "Untitled source",
        text=text,
        source_type=source_type,
        date=date or dt.date.today().isoformat(),
    )

    linked = len(store.neighbours(record.id))

    cognified = False
    try:
        cognified = await cognee_engine.ingest(f"{title}\n\n{text}")
    except Exception as error:  # pragma: no cover - engine is best-effort
        log.warning("Cognee ingestion failed for %s: %s", record.id, error)

    detail = (
        f"Stored as {record.id} and linked to {linked} "
        f"{'entity' if linked == 1 else 'entities'}."
    )
    detail += (
        " Also added to the Cognee graph."
        if cognified
        else " Cognee is not configured, so this source is searchable in the"
        " relational graph only."
    )

    return {
        "ok": True,
        "source_id": record.id,
        "title": record.title,
        "cognified": cognified,
        "detail": detail,
    }
