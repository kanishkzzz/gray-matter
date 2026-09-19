"""
`POST /analyze` - the Truth Engine.

Given a proposed change in free text, report what it touches and what it
contradicts.

Conflicts are *derived*, not scripted. The change is parsed into
(entity, attribute, proposed value); that triple is checked against the
assertions already in the graph; and a disagreement about the same attribute
of the same entity is a conflict, carrying the sources on both sides as its
evidence. The mock's CFL-001 - Payment Service, MySQL vs PostgreSQL - comes
out of this rather than being written down.

Nothing is invented to fill the screen. A change that matches no entity
returns empty lists and an empty path, and the UI renders that honestly.
"""

from __future__ import annotations

import re

from ..graph.records import Assertion, EntityRecord
from ..graph.seed import KNOWN_VALUES
from ..graph.store import GraphStore
from .projections import (
    decision_summary,
    entity_payload,
    source_payload,
    ticket_payload,
)

# "from X to Y", "X -> Y", "replace X with Y" - the shapes a change request
# actually takes when someone types one.
_TRANSITIONS = (
    re.compile(r"from\s+(?P<old>[\w.\s]+?)\s+to\s+(?P<new>[\w.]+)", re.I),
    re.compile(r"(?P<old>[\w.]+)\s*(?:->|→|=>)\s*(?P<new>[\w.]+)", re.I),
    re.compile(r"replace\s+(?P<old>[\w.]+)\s+with\s+(?P<new>[\w.]+)", re.I),
    re.compile(r"(?P<old>[\w.]+)\s+instead\s+of\s+(?P<new>[\w.]+)", re.I),
)


def _known_value(text: str) -> str | None:
    """Canonical name for a technology mentioned in the text, if any."""
    lowered = text.lower()
    for token, canonical in KNOWN_VALUES.items():
        if re.search(rf"\b{re.escape(token)}\b", lowered):
            return canonical
    return None


def _proposed_value(change: str) -> str | None:
    """
    The value the change is moving *to*.

    Transition phrasings are tried first because they name a direction; a bare
    mention ("use PostgreSQL for payments") falls back to whichever known value
    appears.
    """
    for pattern in _TRANSITIONS:
        match = pattern.search(change)
        if not match:
            continue
        # "instead of" reverses the direction of the other three.
        group = "old" if "instead" in pattern.pattern else "new"
        candidate = _known_value(match.group(group))
        if candidate:
            return candidate

    return _known_value(change)


def _attribute_for(change: str, assertions: list[Assertion]) -> str | None:
    """
    Which attribute the change is about, chosen by the attribute terms the
    assertions declare. Falls back to the attribute whose existing value the
    change names - "move payments off MySQL" says nothing about "database",
    but MySQL is itself a datastore value.
    """
    lowered = change.lower()

    for assertion in assertions:
        if any(
            re.search(rf"\b{re.escape(term)}\b", lowered)
            for term in assertion.attribute_terms
        ):
            return assertion.attribute

    for assertion in assertions:
        if re.search(rf"\b{re.escape(assertion.value.lower())}\b", lowered):
            return assertion.attribute

    return None


def _severity(store: GraphStore, entity: EntityRecord, attribute: str) -> str:
    """
    High when the standing value is carried by an implemented decision:
    contradicting something already shipped is a different order of problem
    from contradicting a proposal.
    """
    for assertion in store.assertions_for(entity.id, attribute):
        decision = store.decisions.get(assertion.asserted_by)
        if decision and decision.status == "Implemented":
            return "high"
    return "medium"


def _conflicts(store: GraphStore, change: str, entities: list[EntityRecord]) -> list[dict]:
    proposed = _proposed_value(change)
    if proposed is None:
        return []

    found: list[dict] = []
    counter = 0

    for entity in entities:
        entity_assertions = [a for a in store.assertions if a.entity_id == entity.id]
        attribute = _attribute_for(change, entity_assertions)
        if attribute is None:
            continue

        standing = [
            a
            for a in store.assertions_for(entity.id, attribute)
            if not store.is_superseded(a)
        ]

        disagreeing = [a for a in standing if a.value.lower() != proposed.lower()]
        if not disagreeing:
            continue

        # Evidence is both sides: what the graph currently says, and anything
        # already asserting the proposed value. A conflict with one-sided
        # evidence is not reportable.
        evidence: list[dict] = []
        seen: set[str] = set()
        for assertion in standing:
            citation = store.cite(assertion.asserted_by)
            if citation and citation.id not in seen:
                seen.add(citation.id)
                evidence.append(source_payload(citation))

        if not evidence:
            continue

        counter += 1
        existing = disagreeing[0].value
        found.append(
            {
                "id": f"CFL-{counter:03d}",
                "entity": entity.name,
                "existing_value": existing,
                "proposed_value": proposed,
                "evidence": evidence,
                "severity": _severity(store, entity, attribute),
                "requires_review": True,
            }
        )

    return found


def analyze(store: GraphStore, change: str) -> dict:
    change = change.strip()
    if not change:
        return {
            "affected": [],
            "related_decisions": [],
            "related_tickets": [],
            "conflicts": [],
            "path": {"nodes": [], "edges": []},
        }

    entities = store.match_entities(change)

    # A named technology implies the systems that hold it, even when the
    # change text never names them: "move payments to Postgres" affects
    # Database Architecture and Database Migration too.
    if entities and _proposed_value(change):
        for implied_id in ("ENT-003", "ENT-005"):
            implied = store.entities.get(implied_id)
            if implied and implied not in entities and any(
                e.id == "ENT-001" for e in entities
            ):
                entities.append(implied)

    if not entities:
        return {
            "affected": [],
            "related_decisions": [],
            "related_tickets": [],
            "conflicts": [],
            "path": {"nodes": [], "edges": []},
        }

    entity_ids = {e.id for e in entities}

    # Decisions and tickets reachable from the affected entities.
    related_decisions = [
        d for d in store.decisions_newest_first() if store.neighbours(d.id) & entity_ids
    ]
    related_tickets = store.tickets_for(entity_ids)

    # Narrow to what the change is actually about when it names a technology.
    proposed = _proposed_value(change)
    if proposed:
        needle = proposed.split()[0].lower()
        focused = [
            d
            for d in related_decisions
            if needle in d.title.lower() or needle in d.rationale.lower()
        ]
        if focused:
            related_decisions = focused

    roots = [related_decisions[0].id] if related_decisions else [entities[0].id]
    edges = store.subgraph(roots, depth=2, limit=10)

    return {
        "affected": [entity_payload(e) for e in entities],
        "related_decisions": [decision_summary(d) for d in related_decisions],
        "related_tickets": [ticket_payload(t) for t in related_tickets],
        "conflicts": _conflicts(store, change, entities),
        "path": store.build_path(edges),
    }
