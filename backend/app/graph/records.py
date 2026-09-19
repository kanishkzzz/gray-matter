"""
Internal record types for the graph store.

These are deliberately *not* the API schemas. The store holds a few fields the
wire contract does not expose — keywords, assertions, rationale — and the
service layer projects store records onto `app.schemas` on the way out.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SourceRecord:
    id: str
    type: str
    title: str
    date: str
    snippet: str
    #: Extra retrieval terms that do not appear verbatim in the snippet.
    keywords: tuple[str, ...] = ()


@dataclass(frozen=True)
class EntityRecord:
    id: str
    type: str
    name: str
    #: Names the entity is also known by, matched when parsing a question.
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class TicketRecord:
    id: str
    key: str
    title: str
    status: str


@dataclass(frozen=True)
class DecisionRecord:
    id: str
    title: str
    date: str
    status: str
    rationale: str
    decided_by: str
    #: Source ids, in the order the decision record cites them.
    evidence: tuple[str, ...] = ()
    keywords: tuple[str, ...] = ()


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    label: str


@dataclass(frozen=True)
class Assertion:
    """
    A claim some source makes about one attribute of one entity.

    This is what makes conflict detection real rather than scripted: two
    assertions about the same (entity, attribute) with different values are a
    conflict, and each one carries the source that said it.
    """

    entity_id: str
    attribute: str
    value: str
    #: Id of the source or decision asserting it.
    asserted_by: str
    #: Terms that select this attribute out of a free-text change request.
    attribute_terms: tuple[str, ...] = field(default=())
