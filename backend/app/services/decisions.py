"""
`GET /decisions` and `GET /decisions/{id}`.

The detail response assembles a decision's full trace: its evidence, the
lineage path through the graph, the tickets implementing it and the entities
it affects - each derived from the edge list rather than stored alongside the
decision, so adding an edge updates every view of it at once.
"""

from __future__ import annotations

from ..graph.records import Edge
from ..graph.store import GraphStore
from .projections import (
    decision_summary,
    entity_payload,
    source_payload,
    ticket_payload,
)


class DecisionNotFound(LookupError):
    """Raised for an id the graph does not hold. The route turns it into a 404."""


def list_decisions(store: GraphStore) -> dict:
    return {
        "decisions": [decision_summary(d) for d in store.decisions_newest_first()]
    }


def _trace_edges(store: GraphStore, decision_id: str) -> list[Edge]:
    """
    Lineage for one decision, ordered so it reads left to right: what led to
    it first, then what it led to.

    Incoming edges are what came before ("MTG-004 resulted in DEC-004");
    outgoing edges are consequences. Second-hop edges are appended so a ticket
    reaches the entity it changes.
    """
    incoming = [e for e in store.edges if e.target == decision_id]
    outgoing = [e for e in store.edges if e.source == decision_id]

    ordered: list[Edge] = [*incoming, *outgoing]
    chosen = {(e.source, e.target) for e in ordered}

    for edge in list(outgoing):
        far = edge.target
        if store.node_type(far) in {"ticket", "entity"}:
            for second in store.edges:
                if second.source != far:
                    continue
                key = (second.source, second.target)
                if key not in chosen and len(ordered) < 10:
                    chosen.add(key)
                    ordered.append(second)

    return ordered


def get_decision(store: GraphStore, decision_id: str) -> dict:
    record = store.decisions.get(decision_id.upper())
    if record is None:
        raise DecisionNotFound(decision_id)

    edges = _trace_edges(store, record.id)
    neighbours = store.neighbours(record.id)

    implemented_by = [
        store.tickets[n] for n in neighbours if n in store.tickets
    ]
    implemented_by.sort(key=lambda t: t.key)

    # Entities the decision touches directly, plus those reached through a
    # ticket it spawned.
    affected_ids: list[str] = []
    for candidate in neighbours:
        if candidate in store.entities and candidate not in affected_ids:
            affected_ids.append(candidate)
    for ticket in implemented_by:
        for candidate in store.neighbours(ticket.id):
            if candidate in store.entities and candidate not in affected_ids:
                affected_ids.append(candidate)

    evidence = [
        source_payload(store.sources[s])
        for s in record.evidence
        if s in store.sources
    ]

    return {
        **decision_summary(record),
        "rationale": record.rationale,
        "decided_by": record.decided_by,
        "evidence": evidence,
        "path": store.build_path(edges),
        "implemented_by": [ticket_payload(t) for t in implemented_by],
        "affects": [entity_payload(store.entities[e]) for e in affected_ids],
    }
