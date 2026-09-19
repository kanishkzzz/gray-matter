"""
`POST /ask` - natural-language question against the corpus.

Retrieval is graph-first and deterministic. The evidence list, the
relationship path and the related decisions are all selected by `GraphStore`
from records that exist; nothing in the structured response can be
hallucinated, because nothing in it comes from a model.

The prose answer is the one field a model may write, and only over evidence
already retrieved. With no key configured - or if the call fails - the
extractive composer produces the answer from the same evidence instead. The
two paths are interchangeable by design: turning the LLM off changes the
wording, never the citations.
"""

from __future__ import annotations

import logging

from .. import cognee_engine
from ..config import settings
from ..graph.records import DecisionRecord, SourceRecord
from ..graph.store import (
    GENERIC_ENTITY_WORDS,
    RECORD_ID,
    GraphStore,
    tokenize,
)
from .projections import decision_summary, source_payload

log = logging.getLogger("graymatter.ask")

MAX_EVIDENCE = 4


def _fallback(store: GraphStore) -> dict:
    """
    "Nothing found" is a real answer in this product. It states what was
    searched rather than shrugging, and returns a null path so the UI renders
    its empty state instead of an empty diagram.
    """
    counts = store.counts()
    return {
        "answer": (
            "No indexed source addresses this question. Searched "
            f"{counts['sources']} sources, {counts['entities']} entities and "
            f"{counts['decisions']} decisions across the corpus. Narrow the "
            "question to a named service, decision or document, or connect "
            "the system that holds this information."
        ),
        "evidence": [],
        "path": None,
        "related_decisions": [],
    }


def _compose_answer(
    question: str,
    sources: list[SourceRecord],
    decisions: list[DecisionRecord],
) -> str:
    """
    Extractive answer, built only from retrieved records.

    Hedged with "Evidence indicates" because that is exactly what this is: a
    restatement of what the cited sources say, not an independent claim.
    """
    lead = sources[0]
    parts: list[str] = [f"Evidence indicates: {lead.snippet}"]

    if decisions:
        decision = decisions[0]
        parts.append(
            f"This is recorded as {decision.id} - {decision.title} "
            f"({decision.status.lower()}, {decision.date}), "
            f"decided by {decision.decided_by}."
        )

    others = [s for s in sources[1:]]
    if others:
        listed = ", ".join(f"{s.title} ({s.id})" for s in others)
        parts.append(f"Corroborated by {listed}.")

    return " ".join(parts)


_LLM_PROMPT = """You are answering a question about a company's internal decision record.

Rules:
- Use ONLY the sources below. If they do not answer the question, say so plainly.
- Cite record ids inline, like DEC-004 or MTG-004, when you refer to them.
- Do not invent ids, dates, names or systems that are not in the sources.
- Three sentences at most. No preamble, no bullet points, no sign-off.
- Write "Evidence indicates ..." rather than asserting facts in your own voice.

Question: {question}

Sources:
{sources}

Answer:"""


async def _llm_answer(
    question: str,
    sources: list[SourceRecord],
    decisions: list[DecisionRecord],
) -> str | None:
    """
    Ask Cognee to phrase the answer over the retrieved evidence.

    The evidence is inlined into the prompt rather than relying on Cognee's
    own recall, so the prose is grounded in exactly the records the response
    cites - the answer and the evidence panel can never disagree.
    """
    if not (settings.use_llm_answers and cognee_engine.available()):
        return None

    rendered = "\n".join(
        f"[{s.id}] {s.title} ({s.type}, {s.date}): {s.snippet}" for s in sources
    )
    for decision in decisions:
        rendered += (
            f"\n[{decision.id}] {decision.title} (decision, {decision.date}, "
            f"{decision.status}, decided by {decision.decided_by}): "
            f"{decision.rationale}"
        )

    results = await cognee_engine.search(
        _LLM_PROMPT.format(question=question, sources=rendered)
    )
    if not results:
        return None

    answer = max(results, key=len).strip()
    # A one-word or echoed response is worse than the extractive composer.
    return answer if len(answer) > 40 else None


def _named_records(store: GraphStore, question: str) -> list[str]:
    """Record ids written out in the question that the graph actually holds."""
    seen: list[str] = []
    for match in RECORD_ID.finditer(question):
        record_id = match.group(0).upper()
        if store.exists(record_id) and record_id not in seen:
            seen.append(record_id)
    return seen


def _answer_for_records(
    store: GraphStore, question: str, record_ids: list[str]
) -> dict:
    """
    Direct lookup. The named record leads, its own evidence is cited, and its
    lineage is the path - no scoring involved, because the question already
    said which record it wants.
    """
    decisions = [store.decisions[r] for r in record_ids if r in store.decisions]

    # A named source is its own evidence; a named decision cites its own.
    cited: list[str] = []
    for record_id in record_ids:
        if record_id in store.sources:
            cited.append(record_id)
        elif record_id in store.decisions:
            cited.extend(store.decisions[record_id].evidence)

    sources: list[SourceRecord] = []
    seen: set[str] = set()
    for source_id in cited:
        if source_id in store.sources and source_id not in seen:
            seen.add(source_id)
            sources.append(store.sources[source_id])

    # A named ticket or entity has no evidence of its own; cite the record.
    if not sources:
        sources = [s for s in (store.cite(r) for r in record_ids) if s]

    edges = store.subgraph(record_ids, depth=2, limit=8)

    return {
        "answer": _compose_answer(question, sources, decisions),
        "evidence": [source_payload(s) for s in sources],
        "path": store.build_path(edges) if edges else None,
        "related_decisions": [decision_summary(d) for d in decisions],
    }


async def ask(store: GraphStore, question: str) -> dict:
    question = question.strip()
    if not question:
        return _fallback(store)

    # Generic words are dropped wherever they come from - the question text or
    # an entity name. "What database does the payment service use" should
    # retrieve on "database" and "payment", never on "service", which every
    # service in the graph matches equally.
    terms = tokenize(question) - GENERIC_ENTITY_WORDS

    for entity in store.match_entities(question):
        terms |= tokenize(entity.name) - GENERIC_ENTITY_WORDS

    # A question naming a record ("Tell me about DEC-004") is a lookup, not a
    # search. Answer with that record rather than whatever scores highest.
    named = _named_records(store, question)
    if named:
        return _answer_for_records(store, question, named)

    sources = store.search_sources(terms, limit=MAX_EVIDENCE)
    decisions = store.search_decisions(terms, limit=3)

    if not sources and not decisions:
        return _fallback(store)

    # A decision that answers the question but cites sources we did not
    # retrieve should still show its own evidence.
    if decisions:
        seen = {s.id for s in sources}
        for source_id in decisions[0].evidence:
            if source_id not in seen and len(sources) < MAX_EVIDENCE:
                found = store.sources.get(source_id)
                if found:
                    sources.append(found)
                    seen.add(source_id)

    if not sources:
        # Decision hits only - cite the decisions themselves.
        sources = [
            s for s in (store.decision_as_source(d.id) for d in decisions) if s
        ]

    roots = [d.id for d in decisions[:1]] or [sources[0].id]
    edges = store.subgraph(roots, depth=2, limit=8)
    path = store.build_path(edges) if edges else None

    answer = await _llm_answer(question, sources, decisions)
    if answer is None:
        answer = _compose_answer(question, sources, decisions)

    return {
        "answer": answer,
        "evidence": [source_payload(s) for s in sources],
        "path": path,
        "related_decisions": [decision_summary(d) for d in decisions],
    }
