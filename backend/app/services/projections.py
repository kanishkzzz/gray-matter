"""
Store record -> wire payload.

One place where internal records become contract shapes, so a field the API
must not expose (keywords, assertion terms, rationale on a summary) cannot
leak by being forgotten in one endpoint and stripped in another.
"""

from __future__ import annotations

from ..graph.records import (
    DecisionRecord,
    EntityRecord,
    SourceRecord,
    TicketRecord,
)


def source_payload(record: SourceRecord) -> dict:
    return {
        "id": record.id,
        "type": record.type,
        "title": record.title,
        "date": record.date,
        "snippet": record.snippet,
    }


def entity_payload(record: EntityRecord) -> dict:
    return {"id": record.id, "type": record.type, "name": record.name}


def ticket_payload(record: TicketRecord) -> dict:
    return {
        "id": record.id,
        "key": record.key,
        "title": record.title,
        "status": record.status,
    }


def decision_summary(record: DecisionRecord) -> dict:
    return {
        "id": record.id,
        "title": record.title,
        "date": record.date,
        "status": record.status,
    }
