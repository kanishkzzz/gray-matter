"""
The knowledge graph store.

One in-memory graph, seeded from `seed.py` and extended by ingestion. It owns
every lookup and every path assembly, so a `RelationshipPath` can never cite a
record that does not exist - the same guarantee the TypeScript mock makes with
its `edge()` helper, enforced here by `validate()` at construction.

Retrieval is deterministic: scoring is keyword overlap over titles, snippets
and declared keywords. No model is consulted to decide *which* records are
relevant. A model may later phrase the answer (see `services/ask.py`), but the
evidence set is chosen here and is reproducible.
"""

from __future__ import annotations

import re
import threading
from collections import deque

from .records import (
    Assertion,
    DecisionRecord,
    Edge,
    EntityRecord,
    SourceRecord,
    TicketRecord,
)
from . import seed

# Record-id prefix -> the node type the relationship renderer draws.
NODE_TYPE_BY_PREFIX: dict[str, str] = {
    "MTG": "meeting",
    "DOC": "document",
    "MSG": "message",
    "DEC": "decision",
    "ENT": "entity",
    "CHG": "change",
}

_WORD = re.compile(r"[a-z0-9.]+")

# Record ids must survive tokenization whole: splitting DEC-004 into "dec" and
# "004" loses the one term in the question that identifies exactly one record.
RECORD_ID = re.compile(r"\b[a-z]{3,4}-\d{3}\b", re.I)

# Terms too common to carry retrieval signal on their own.
_STOPWORDS = frozenset(
    """a an and are as at be because but by did do does for from had has have
    how i if in into is it its of on or our so than that the their then there
    these they this to was we were what when where which who why will with
    you your does dont doesnt use used using make made get got""".split()
)


# Words that appear in so many entity names they identify nothing on their own.
# Expanding "Payment Service" into search terms must contribute "payment" but
# not "service", or every question about one service retrieves all of them.
# Stored stemmed, because that is the form `tokenize` produces. Plurals need
# no entry: "services" stems to "service".
GENERIC_ENTITY_WORDS = frozenset(
    {
        "service",
        "system",
        "process",
        "component",
        "team",
        "platform",
        "architecture",
        "data",
        "layer",
    }
)


def _negated_date(date: str) -> str:
    """Sort key that orders ISO dates newest-first inside an ascending sort."""
    return "".join(chr(ord("9") - int(c)) if c.isdigit() else c for c in date)


def _stem(word: str) -> str:
    """
    Conservative suffix stripping, so "records" matches "record" and
    "retained" matches "retain".

    Deliberately not a real stemmer: it only removes inflections that would
    otherwise cause a miss between a question and a document about the same
    thing. Anything more aggressive starts merging unrelated words, which
    costs more precision than it buys recall on a corpus this size.
    """
    for suffix, keep in (("ing", 4), ("ed", 3), ("es", 3), ("s", 3)):
        if word.endswith(suffix) and len(word) > keep and not word.endswith("ss"):
            return word[: -len(suffix)]
    return word


def tokenize(text: str) -> set[str]:
    """Lowercase, stemmed word set with stopwords removed, used on both sides
    of every comparison so the two are always stemmed alike. Record ids are
    kept intact alongside the words they would otherwise split into."""
    lowered = text.lower()
    terms = {
        _stem(w)
        for w in _WORD.findall(lowered)
        if w not in _STOPWORDS and len(w) > 1
    }
    terms |= {match.group(0) for match in RECORD_ID.finditer(lowered)}
    return terms


class GraphStore:
    """
    Not thread-safe for writes without the lock it holds internally; FastAPI
    serves requests concurrently and ingestion mutates this structure.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()

        self.sources: dict[str, SourceRecord] = {s.id: s for s in seed.SOURCES}
        self.entities: dict[str, EntityRecord] = {e.id: e for e in seed.ENTITIES}
        self.tickets: dict[str, TicketRecord] = {t.id: t for t in seed.TICKETS}
        self.decisions: dict[str, DecisionRecord] = {d.id: d for d in seed.DECISIONS}
        self.edges: list[Edge] = list(seed.EDGES)
        self.assertions: list[Assertion] = list(seed.ASSERTIONS)

        self._ingest_counter = 0
        self.validate()

    # -- integrity ---------------------------------------------------------

    def exists(self, record_id: str) -> bool:
        return (
            record_id in self.sources
            or record_id in self.entities
            or record_id in self.tickets
            or record_id in self.decisions
        )

    def validate(self) -> None:
        """
        Fail loudly at startup rather than serving a path that points at
        nothing. The frontend renders whatever ids we send it.
        """
        problems: list[str] = []

        for edge in self.edges:
            for end in (edge.source, edge.target):
                if not self.exists(end):
                    problems.append(f"edge {edge.source} -> {edge.target} cites unknown {end}")

        for decision in self.decisions.values():
            for source_id in decision.evidence:
                if source_id not in self.sources:
                    problems.append(f"{decision.id} cites unknown source {source_id}")

        for assertion in self.assertions:
            if assertion.entity_id not in self.entities:
                problems.append(
                    f"assertion on unknown entity {assertion.entity_id}"
                )
            if not self.exists(assertion.asserted_by):
                problems.append(
                    f"assertion asserted by unknown record {assertion.asserted_by}"
                )

        if problems:
            raise ValueError(
                "Knowledge graph is inconsistent:\n  " + "\n  ".join(problems)
            )

    # -- projection --------------------------------------------------------

    def node_type(self, record_id: str) -> str:
        prefix = record_id.split("-")[0].upper()
        return NODE_TYPE_BY_PREFIX.get(prefix, "ticket")

    def node_label(self, record_id: str) -> str:
        node_type = self.node_type(record_id)
        if node_type == "entity":
            found = self.entities.get(record_id)
            return found.name if found else record_id
        if node_type == "decision":
            found = self.decisions.get(record_id)
            return found.title if found else record_id
        if node_type == "ticket":
            found = self.tickets.get(record_id)
            return found.title if found else record_id
        if node_type == "change":
            return record_id
        found = self.sources.get(record_id)
        return found.title if found else record_id

    def build_path(self, edges: list[Edge]) -> dict:
        """
        Assemble a `RelationshipPath` payload. Node order follows first
        appearance, which is the order the renderer draws in.
        """
        seen: set[str] = set()
        nodes: list[dict] = []

        for edge in edges:
            for record_id in (edge.source, edge.target):
                if record_id not in seen:
                    seen.add(record_id)
                    nodes.append(
                        {
                            "id": record_id,
                            "type": self.node_type(record_id),
                            "label": self.node_label(record_id),
                        }
                    )

        return {
            "nodes": nodes,
            "edges": [
                {"from": e.source, "to": e.target, "label": e.label} for e in edges
            ],
        }

    def decision_as_source(self, decision_id: str) -> SourceRecord | None:
        """
        Render a decision as a citable source. Decisions can be evidence -
        `SourceType` includes "decision" for exactly this.
        """
        decision = self.decisions.get(decision_id)
        if decision is None:
            return None

        return SourceRecord(
            id=decision.id,
            type="decision",
            title=decision.title,
            date=decision.date,
            snippet=(
                f"{decision.rationale.split('. ')[0]}. "
                f"Decided by {decision.decided_by} on {decision.date}."
            ),
        )

    def cite(self, record_id: str) -> SourceRecord | None:
        """Resolve any record id to something the evidence panel can show."""
        if record_id in self.sources:
            return self.sources[record_id]
        return self.decision_as_source(record_id)

    # -- traversal ---------------------------------------------------------

    def edges_touching(self, record_id: str) -> list[Edge]:
        return [e for e in self.edges if e.source == record_id or e.target == record_id]

    def neighbours(self, record_id: str) -> set[str]:
        out: set[str] = set()
        for edge in self.edges_touching(record_id):
            out.add(edge.target if edge.source == record_id else edge.source)
        return out

    def subgraph(self, roots: list[str], depth: int = 1, limit: int = 12) -> list[Edge]:
        """
        Breadth-first edge collection around one or more roots.

        Returns edges in discovery order so the assembled path reads outward
        from the roots, and caps the result: a path wider than the renderer can
        draw is not more informative, just less legible.
        """
        collected: list[Edge] = []
        chosen: set[tuple[str, str]] = set()
        visited: set[str] = set()
        queue: deque[tuple[str, int]] = deque((r, 0) for r in roots if self.exists(r))
        visited.update(r for r, _ in queue)

        while queue and len(collected) < limit:
            record_id, level = queue.popleft()
            if level >= depth:
                continue

            for edge in self.edges_touching(record_id):
                key = (edge.source, edge.target)
                if key in chosen:
                    continue
                chosen.add(key)
                collected.append(edge)
                if len(collected) >= limit:
                    break

                other = edge.target if edge.source == record_id else edge.source
                if other not in visited:
                    visited.add(other)
                    queue.append((other, level + 1))

        return collected

    def shortest_path(self, start: str, goal: str, max_hops: int = 6) -> list[Edge]:
        """
        Undirected BFS, returning the edges of one shortest route. Empty when
        the two records are not connected within `max_hops`.
        """
        if start == goal or not self.exists(start) or not self.exists(goal):
            return []

        previous: dict[str, tuple[str, Edge]] = {}
        visited = {start}
        queue: deque[tuple[str, int]] = deque([(start, 0)])

        while queue:
            current, hops = queue.popleft()
            if hops >= max_hops:
                continue

            for edge in self.edges_touching(current):
                other = edge.target if edge.source == current else edge.source
                if other in visited:
                    continue
                visited.add(other)
                previous[other] = (current, edge)

                if other == goal:
                    trail: list[Edge] = []
                    cursor = goal
                    while cursor in previous:
                        parent, via = previous[cursor]
                        trail.append(via)
                        cursor = parent
                    trail.reverse()
                    return trail

                queue.append((other, hops + 1))

        return []

    # -- retrieval ---------------------------------------------------------

    def score_source(self, source: SourceRecord, terms: set[str]) -> int:
        total, _ = self._score_source_parts(source, terms)
        return total

    def _score_source_parts(
        self, source: SourceRecord, terms: set[str]
    ) -> tuple[int, bool]:
        """
        Returns `(score, is_strong)`.

        Title and declared keywords count double: a source titled "Data
        Retention Policy" answers a retention question better than one that
        mentions retention in passing.

        `is_strong` says the match is about the source's subject rather than
        its incidental wording - a title hit, a declared keyword, an explicit
        id, or two independent body terms. A single body word is noise: the
        question "what is the office cat called" overlaps "service-to-service
        calls were using static credentials" on exactly one stemmed word, and
        without this gate that meeting gets cited as evidence about cats.
        """
        title = tokenize(source.title)
        body = tokenize(source.snippet)
        keywords = tokenize(" ".join(source.keywords))

        title_hits = len(terms & title)
        body_hits = len(terms & body)
        keyword_hits = len(terms & keywords)
        id_hit = source.id.lower() in {t.lower() for t in terms}

        total = (
            2 * title_hits + body_hits + 2 * keyword_hits + (3 if id_hit else 0)
        )
        strong = bool(title_hits or keyword_hits or id_hit or body_hits >= 2)
        return total, strong

    def score_decision(self, decision: DecisionRecord, terms: set[str]) -> int:
        total, _ = self._score_decision_parts(decision, terms)
        return total

    def _score_decision_parts(
        self, decision: DecisionRecord, terms: set[str]
    ) -> tuple[int, bool]:
        """`(score, is_strong)`, on the same rule as `_score_source_parts`."""
        title = tokenize(decision.title)
        body = tokenize(decision.rationale)
        keywords = tokenize(" ".join(decision.keywords))

        title_hits = len(terms & title)
        body_hits = len(terms & body)
        keyword_hits = len(terms & keywords)
        id_hit = decision.id.lower() in {t.lower() for t in terms}

        total = (
            2 * title_hits + body_hits + 2 * keyword_hits + (4 if id_hit else 0)
        )
        strong = bool(title_hits or keyword_hits or id_hit or body_hits >= 2)
        return total, strong

    def search_sources(
        self, terms: set[str], limit: int = 4, floor: float = 0.4
    ) -> list[SourceRecord]:
        """
        `floor` drops weak hits relative to the best one. Without it a source
        matching a single incidental word is cited alongside the source that
        actually answers the question, and the evidence panel stops meaning
        anything.
        """
        scored = [
            (*self._score_source_parts(s, terms), s) for s in self.sources.values()
        ]
        hits = [(score, s) for score, strong, s in scored if score > 0 and strong]
        if not hits:
            return []

        best = max(score for score, _ in hits)
        hits = [(score, s) for score, s in hits if score >= best * floor]

        # Highest score first; newest source breaks a tie.
        hits.sort(key=lambda pair: (-pair[0], _negated_date(pair[1].date)))
        return [s for _, s in hits[:limit]]

    def search_decisions(
        self, terms: set[str], limit: int = 3, floor: float = 0.4
    ) -> list[DecisionRecord]:
        scored = [
            (*self._score_decision_parts(d, terms), d)
            for d in self.decisions.values()
        ]
        hits = [(score, d) for score, strong, d in scored if score > 0 and strong]
        if not hits:
            return []

        best = max(score for score, _ in hits)
        hits = [(score, d) for score, d in hits if score >= best * floor]

        hits.sort(key=lambda pair: (-pair[0], _negated_date(pair[1].date)))
        return [d for _, d in hits[:limit]]

    def match_entities(self, text: str) -> list[EntityRecord]:
        """
        Name and alias matching against free text. Order follows the seed list
        so results are stable between calls.
        """
        lowered = text.lower()
        found: list[EntityRecord] = []

        for entity in self.entities.values():
            candidates = (entity.name.lower(), *entity.aliases)
            if any(c in lowered for c in candidates):
                found.append(entity)

        return found

    def tickets_for(self, record_ids: set[str]) -> list[TicketRecord]:
        """Tickets adjacent to any of the given records."""
        out: list[TicketRecord] = []
        for ticket in self.tickets.values():
            if self.neighbours(ticket.id) & record_ids:
                out.append(ticket)
        return out

    def decisions_newest_first(self) -> list[DecisionRecord]:
        return sorted(self.decisions.values(), key=lambda d: d.date, reverse=True)

    # -- conflicts ---------------------------------------------------------

    def assertions_for(self, entity_id: str, attribute: str) -> list[Assertion]:
        return [
            a
            for a in self.assertions
            if a.entity_id == entity_id and a.attribute == attribute
        ]

    def is_superseded(self, assertion: Assertion) -> bool:
        """
        An assertion made by a superseded decision is history, not a live
        claim. DEC-007 still says "static vault credentials", but DEC-002
        supersedes it, so the two do not constitute a standing conflict.
        """
        decision = self.decisions.get(assertion.asserted_by)
        return decision is not None and decision.status == "Superseded"

    def standing_conflicts(self) -> list[tuple[Assertion, Assertion]]:
        """
        Every pair of live assertions that disagree about the same (entity,
        attribute). `/health` counts these; `/analyze` reports the ones the
        proposed change touches.
        """
        grouped: dict[tuple[str, str], list[Assertion]] = {}
        for assertion in self.assertions:
            if self.is_superseded(assertion):
                continue
            grouped.setdefault((assertion.entity_id, assertion.attribute), []).append(
                assertion
            )

        pairs: list[tuple[Assertion, Assertion]] = []
        for group in grouped.values():
            for i, left in enumerate(group):
                for right in group[i + 1 :]:
                    if left.value.lower() != right.value.lower():
                        pairs.append((left, right))

        return pairs

    # -- ingestion ---------------------------------------------------------

    def next_source_id(self, source_type: str) -> str:
        prefix = {
            "meeting": "MTG",
            "document": "DOC",
            "message": "MSG",
            "ticket": "TKT",
            "decision": "DEC",
        }.get(source_type, "DOC")

        with self._lock:
            self._ingest_counter += 1
            candidate = f"{prefix}-{900 + self._ingest_counter}"
            while self.exists(candidate):
                self._ingest_counter += 1
                candidate = f"{prefix}-{900 + self._ingest_counter}"
            return candidate

    def add_source(
        self,
        *,
        title: str,
        text: str,
        source_type: str = "document",
        date: str,
        snippet_chars: int = 600,
    ) -> SourceRecord:
        """
        Add ingested text as a citable source and link it to every entity it
        names. Linking is what makes ingested content reachable from a path;
        an unlinked source is only ever a keyword hit.
        """
        record = SourceRecord(
            id=self.next_source_id(source_type),
            type=source_type,
            title=title,
            date=date,
            snippet=text.strip()[:snippet_chars],
            keywords=tuple(sorted(tokenize(title))[:8]),
        )

        with self._lock:
            self.sources[record.id] = record
            for entity in self.match_entities(text):
                self.edges.append(Edge(record.id, entity.id, "mentions"))

        return record

    def counts(self) -> dict[str, int]:
        return {
            "sources": len(self.sources),
            "entities": len(self.entities),
            "relationships": len(self.edges),
            "decisions": len(self.decisions),
            "conflicts": len(self.standing_conflicts()),
        }


#: Process-wide store. FastAPI resolves it through `deps.get_store`.
store = GraphStore()
