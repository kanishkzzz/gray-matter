"""
Q&A quality suite.

    python scripts/verify_ask.py

`verify_api.py` checks that /ask returns the right *shape*. This checks that it
returns the right *answer*: that each question surfaces the decision and the
source that genuinely address it, that unrelated questions retrieve nothing at
all, and that the prose never cites a record the evidence list does not carry.

The last of those is the one that matters most. An answer mentioning DEC-004
while the evidence panel shows something else is worse than no answer: the
citation looks checkable and is not.
"""

from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.graph.store import store  # noqa: E402
from app.services.ask import ask  # noqa: E402

failures: list[str] = []
checks = 0

RECORD_ID = re.compile(r"\b(?:DEC|MTG|DOC|MSG|ENT|PAY|AUTH|OPS|TKT)-\d{3}\b")


def check(label: str, condition: bool, detail: str = "") -> None:
    global checks
    checks += 1
    if condition:
        print(f"  ok    {label}")
    else:
        print(f"  FAIL  {label}{' - ' + detail if detail else ''}")
        failures.append(label)


# (question, expected lead decision, source ids that must appear)
ANSWERABLE = [
    (
        "Why did we choose PostgreSQL for the payment service?",
        "DEC-004",
        ["DOC-014", "MTG-004"],
    ),
    ("What database does the payment service use?", "DEC-004", ["DOC-001"]),
    ("Why did we move off MySQL?", "DEC-004", ["MTG-004"]),
    ("How long do we retain transaction records?", "DEC-003", ["DOC-009"]),
    ("What is our data retention policy?", "DEC-003", ["DOC-009"]),
    ("How do services authenticate with each other?", "DEC-002", ["DOC-021"]),
    ("Why did we adopt OAuth?", "DEC-002", ["MTG-002"]),
    ("Why do we have transaction monitoring?", "DEC-005", ["DOC-007"]),
    ("What alerting do we have on failed transactions?", "DEC-005", ["DOC-007"]),
    ("Why is the payments platform event driven?", "DEC-001", ["MTG-001"]),
    ("Tell me about DEC-004", "DEC-004", []),
]

# Questions the corpus genuinely cannot answer. Each must return nothing
# rather than the nearest keyword collision.
UNANSWERABLE = [
    "What is the office cat called?",
    "How much holiday do I get?",
    "Who won the football match?",
    "What is the wifi password?",
    "When is the Christmas party?",
]


async def main() -> int:
    print("\n=== questions the corpus can answer ===")
    for question, expected_decision, expected_sources in ANSWERABLE:
        result = await ask(store, question)

        decision_ids = [d["id"] for d in result["related_decisions"]]
        source_ids = [s["id"] for s in result["evidence"]]

        check(
            f"{question!r} leads with {expected_decision}",
            decision_ids[:1] == [expected_decision],
            f"got {decision_ids}",
        )
        for source_id in expected_sources:
            check(
                f"  cites {source_id}",
                source_id in source_ids,
                f"got {source_ids}",
            )
        check(f"  has a path", result["path"] is not None)
        check(f"  answer is prose", len(result["answer"]) > 60)

    print("\n=== questions the corpus cannot answer ===")
    for question in UNANSWERABLE:
        result = await ask(store, question)
        check(
            f"{question!r} retrieves no evidence",
            result["evidence"] == [],
            f"got {[s['id'] for s in result['evidence']]}",
        )
        check(
            f"  no decisions",
            result["related_decisions"] == [],
            f"got {[d['id'] for d in result['related_decisions']]}",
        )
        check(f"  null path", result["path"] is None)
        check(
            f"  says what was searched",
            "Searched" in result["answer"],
            result["answer"][:60],
        )

    print("\n=== every cited id in the prose is in the evidence ===")
    for question, _, _ in ANSWERABLE:
        result = await ask(store, question)
        available = (
            {s["id"] for s in result["evidence"]}
            | {d["id"] for d in result["related_decisions"]}
            | {n["id"] for n in (result["path"] or {"nodes": []})["nodes"]}
        )
        mentioned = set(RECORD_ID.findall(result["answer"]))
        unsupported = mentioned - available
        check(
            f"{question[:44]!r} cites nothing unsupported",
            not unsupported,
            f"unsupported: {sorted(unsupported)}",
        )

    print("\n=== evidence is never empty when a decision was found ===")
    for question, _, _ in ANSWERABLE:
        result = await ask(store, question)
        if result["related_decisions"]:
            check(
                f"{question[:44]!r} shows its evidence",
                len(result["evidence"]) > 0,
            )

    print(f"\n{'=' * 60}")
    if failures:
        print(f"{len(failures)} of {checks} checks FAILED:")
        for label in failures:
            print(f"  - {label}")
        return 1
    print(f"All {checks} Q&A checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
