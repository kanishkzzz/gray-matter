"""
Contract verification.

    python scripts/verify_api.py          (in-process, no server needed)
    python scripts/verify_api.py --http   (against a running server on :8000)

Checks that every endpoint returns the shape `src/types/index.ts` declares:
the required keys, the enum members, and - the part that actually bites - that
every id referenced by a relationship path or a piece of evidence is a record
the graph holds. A path node pointing at nothing renders as a blank box in the
UI and is invisible in a type check.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

failures: list[str] = []
checks = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global checks
    checks += 1
    if condition:
        print(f"  ok    {label}")
    else:
        print(f"  FAIL  {label}{' - ' + detail if detail else ''}")
        failures.append(label)


# Enum members, copied from src/types/index.ts.
SOURCE_TYPES = {"meeting", "document", "ticket", "message", "decision"}
ENTITY_TYPES = {"service", "system", "process", "component", "team"}
DECISION_STATUS = {"Implemented", "Approved", "Proposed", "Superseded", "Rejected"}
TICKET_STATUS = {"Done", "In Progress", "To Do", "Blocked"}
SEVERITY = {"high", "medium", "low"}
NODE_TYPES = {
    "meeting",
    "document",
    "message",
    "decision",
    "ticket",
    "entity",
    "change",
}

ISO_DATE = 10  # YYYY-MM-DD


def check_source(source: dict, where: str) -> None:
    check(f"{where} source has all keys",
          {"id", "type", "title", "date", "snippet"} <= source.keys(),
          str(sorted(source.keys())))
    check(f"{where} source.type is a SourceType",
          source.get("type") in SOURCE_TYPES, str(source.get("type")))
    check(f"{where} source.date is ISO",
          len(str(source.get("date", ""))) == ISO_DATE, str(source.get("date")))
    check(f"{where} source.snippet is non-empty", bool(source.get("snippet")))


def check_path(path: dict, where: str, known_ids: set[str]) -> None:
    check(f"{where} path has nodes and edges", {"nodes", "edges"} <= path.keys())

    node_ids = {n["id"] for n in path["nodes"]}

    for node in path["nodes"]:
        check(f"{where} node {node['id']} type is a RelationshipNodeType",
              node["type"] in NODE_TYPES, node["type"])
        check(f"{where} node {node['id']} has a label",
              bool(node.get("label")) and node["label"] != node["id"],
              f"label={node.get('label')!r}")
        check(f"{where} node {node['id']} is a real record",
              node["id"] in known_ids, "not in the graph")

    for edge in path["edges"]:
        check(f"{where} edge uses 'from'/'to' keys",
              {"from", "to", "label"} <= edge.keys(), str(sorted(edge.keys())))
        check(f"{where} edge {edge['from']}->{edge['to']} endpoints are drawn",
              edge["from"] in node_ids and edge["to"] in node_ids)
        check(f"{where} edge {edge['from']}->{edge['to']} has a verb",
              bool(edge.get("label")))


def main(use_http: bool) -> int:
    if use_http:
        import httpx

        client = httpx.Client(base_url="http://127.0.0.1:8000", timeout=30)
        get = lambda p: client.get(p)            # noqa: E731
        post = lambda p, j: client.post(p, json=j)  # noqa: E731
    else:
        from fastapi.testclient import TestClient

        from app.main import app

        client = TestClient(app)
        get = lambda p: client.get(p)            # noqa: E731
        post = lambda p, j: client.post(p, json=j)  # noqa: E731

    from app.graph.store import store

    known_ids = (
        set(store.sources)
        | set(store.entities)
        | set(store.tickets)
        | set(store.decisions)
    )

    # -- GET /health --------------------------------------------------------
    print("\n=== GET /health ===")
    response = get("/health")
    check("200", response.status_code == 200, str(response.status_code))
    body = response.json()
    check("has every HealthResponse key",
          {"status", "sources", "entities", "relationships", "decisions",
           "conflicts"} <= body.keys(),
          str(sorted(body.keys())))
    check("counts are ints",
          all(isinstance(body[k], int)
              for k in ("sources", "entities", "relationships", "decisions",
                        "conflicts")))
    check("graph is non-empty", body["sources"] > 0 and body["decisions"] > 0)

    # -- GET /decisions -----------------------------------------------------
    print("\n=== GET /decisions ===")
    response = get("/decisions")
    check("200", response.status_code == 200, str(response.status_code))
    decisions = response.json()["decisions"]
    check("returns decisions", len(decisions) > 0)
    check("every status is a DecisionStatus",
          all(d["status"] in DECISION_STATUS for d in decisions))
    check("newest first",
          [d["date"] for d in decisions] == sorted(
              (d["date"] for d in decisions), reverse=True))
    check("summaries carry no detail fields",
          all("rationale" not in d for d in decisions))

    # -- GET /decisions/{id} ------------------------------------------------
    print("\n=== GET /decisions/DEC-004 ===")
    response = get("/decisions/DEC-004")
    check("200", response.status_code == 200, str(response.status_code))
    detail = response.json()
    check("has every DecisionDetail key",
          {"id", "title", "date", "status", "rationale", "decided_by",
           "evidence", "path", "implemented_by", "affects"} <= detail.keys(),
          str(sorted(detail.keys())))
    check("rationale is substantial", len(detail["rationale"]) > 80)
    check("decided_by is named", bool(detail["decided_by"]))
    check("has evidence", len(detail["evidence"]) > 0)
    for source in detail["evidence"]:
        check_source(source, "DEC-004")
    check_path(detail["path"], "DEC-004", known_ids)
    check("implemented_by statuses valid",
          all(t["status"] in TICKET_STATUS for t in detail["implemented_by"]))
    check("affects types valid",
          all(e["type"] in ENTITY_TYPES for e in detail["affects"]))
    check("PAY-101 implements DEC-004",
          any(t["key"] == "PAY-101" for t in detail["implemented_by"]))
    check("DEC-004 affects the Payment Service",
          any(e["name"] == "Payment Service" for e in detail["affects"]))

    print("\n=== GET /decisions/DEC-999 ===")
    response = get("/decisions/DEC-999")
    check("404 for an unknown decision", response.status_code == 404,
          str(response.status_code))

    print("\n=== every decision has a renderable trace ===")
    for summary in decisions:
        one = get(f"/decisions/{summary['id']}").json()
        check(f"{summary['id']} path nodes all exist",
              all(n["id"] in known_ids for n in one["path"]["nodes"]))
        check(f"{summary['id']} evidence all real",
              all(s["id"] in known_ids for s in one["evidence"]))

    # -- POST /ask ----------------------------------------------------------
    print("\n=== POST /ask ===")
    response = post("/ask", {"question": "Why did we choose PostgreSQL?"})
    check("200", response.status_code == 200, str(response.status_code))
    answer = response.json()
    check("has every AskResponse key",
          {"answer", "evidence", "path", "related_decisions"} <= answer.keys(),
          str(sorted(answer.keys())))
    check("answer is prose", len(answer["answer"]) > 40)
    check("cites evidence", len(answer["evidence"]) > 0)
    for source in answer["evidence"]:
        check_source(source, "ask")
    check("finds DEC-004",
          any(d["id"] == "DEC-004" for d in answer["related_decisions"]),
          str([d["id"] for d in answer["related_decisions"]]))
    if answer["path"]:
        check_path(answer["path"], "ask", known_ids)

    print("\n=== POST /ask - nothing found ===")
    response = post("/ask", {"question": "What is the office cat called?"})
    miss = response.json()
    check("200", response.status_code == 200)
    check("path is null, not an empty diagram", miss["path"] is None,
          str(miss["path"]))
    check("no evidence invented", miss["evidence"] == [])
    check("says what was searched", "Searched" in miss["answer"], miss["answer"][:80])

    print("\n=== POST /ask - other topics resolve ===")
    for question, expected in [
        ("How long do we retain transaction records?", "DEC-003"),
        ("How do services authenticate with each other?", "DEC-002"),
        ("Why do we have transaction monitoring?", "DEC-005"),
    ]:
        got = post("/ask", {"question": question}).json()
        ids = [d["id"] for d in got["related_decisions"]]
        check(f"{question!r} -> {expected}", expected in ids, str(ids))

    # -- POST /analyze ------------------------------------------------------
    print("\n=== POST /analyze - the conflict case ===")
    response = post(
        "/analyze",
        {"change": "Change payment database from MySQL to PostgreSQL"},
    )
    check("200", response.status_code == 200, str(response.status_code))
    result = response.json()
    check("has every AnalyzeResponse key",
          {"affected", "related_decisions", "related_tickets", "conflicts",
           "path"} <= result.keys(),
          str(sorted(result.keys())))
    check("affects the Payment Service",
          any(e["name"] == "Payment Service" for e in result["affected"]))
    check("detects a conflict", len(result["conflicts"]) > 0)

    if result["conflicts"]:
        conflict = result["conflicts"][0]
        check("conflict has every key",
              {"id", "entity", "existing_value", "proposed_value", "evidence",
               "severity", "requires_review"} <= conflict.keys(),
              str(sorted(conflict.keys())))
        check("conflict is MySQL vs PostgreSQL",
              conflict["existing_value"] == "MySQL"
              and conflict["proposed_value"] == "PostgreSQL",
              f"{conflict['existing_value']} vs {conflict['proposed_value']}")
        check("severity is a ConflictSeverity",
              conflict["severity"] in SEVERITY, conflict["severity"])
        check("conflict cites evidence", len(conflict["evidence"]) > 0)
        for source in conflict["evidence"]:
            check_source(source, "conflict")
        check("requires_review is a bool",
              isinstance(conflict["requires_review"], bool))

    check_path(result["path"], "analyze", known_ids)
    check("finds related tickets", len(result["related_tickets"]) > 0)
    check("ticket statuses valid",
          all(t["status"] in TICKET_STATUS for t in result["related_tickets"]))

    print("\n=== POST /analyze - no match invents nothing ===")
    empty = post("/analyze", {"change": "Repaint the office kitchen"}).json()
    check("no entities", empty["affected"] == [])
    check("no conflicts", empty["conflicts"] == [])
    check("empty path", empty["path"] == {"nodes": [], "edges": []},
          str(empty["path"]))

    # -- summary ------------------------------------------------------------
    print(f"\n{'=' * 60}")
    if failures:
        print(f"{len(failures)} of {checks} checks FAILED:")
        for label in failures:
            print(f"  - {label}")
        return 1

    print(f"All {checks} contract checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--http" in sys.argv))
