"""
Load the sample corpus in `backend/data/samples` through the running API.

    python scripts/load_samples.py                  (from backend/, API on :8000)
    python scripts/load_samples.py --base-url http://127.0.0.1:8000
    python scripts/load_samples.py --dry-run        (parse and report, send nothing)

Ingestion goes through `POST /ingest/text` rather than touching `GraphStore`
directly, so this exercises the same path the Streamlit console and any future
uploader use - including the Cognee write, when Cognee is installed.

Sources are linked to entities by name and alias matching over the text, so the
"linked" count in the output is the thing worth reading: a sample that links to
nothing is only a keyword hit and will never appear in a relationship path.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "data" / "samples"
MANIFEST = SAMPLES_DIR / "manifest.json"


def rows_to_text(raw: str) -> str:
    """
    Flatten CSV rows to one "column: value, column: value" line each.

    Mirrors `services.ingest.rows_to_text`: it reads as a sentence to an
    embedding model, and it keeps the column name next to the value so entity
    names in a cell are still matched by name.
    """
    reader = csv.DictReader(io.StringIO(raw))
    lines = []
    for row in reader:
        rendered = ", ".join(
            f"{key}: {value}" for key, value in row.items() if key and value
        )
        if rendered:
            lines.append(rendered)
    return "\n".join(lines)


def load_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8")
    return rows_to_text(raw) if path.suffix.lower() == ".csv" else raw


def call(base_url: str, path: str, payload: dict | None = None) -> dict:
    url = f"{base_url.rstrip('/')}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
        method="POST" if data else "GET",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse the manifest and print what would be sent.",
    )
    args = parser.parse_args()

    if not MANIFEST.exists():
        print(f"No manifest at {MANIFEST}", file=sys.stderr)
        return 1

    entries = json.loads(MANIFEST.read_text(encoding="utf-8"))

    if args.dry_run:
        for entry in entries:
            text = load_text(SAMPLES_DIR / entry["file"])
            print(
                f"  {entry['source_type']:9} {entry['file']:42} "
                f"{len(text):6,} chars"
            )
        print(f"\n{len(entries)} sample(s). Nothing sent.")
        return 0

    try:
        before = call(args.base_url, "/health")
    except urllib.error.URLError as error:
        print(
            f"Could not reach {args.base_url}: {error}\n"
            "Start the API first:  uvicorn app.main:app --port 8000",
            file=sys.stderr,
        )
        return 1

    print(
        f"Before:  {before['sources']} sources, {before['relationships']} "
        f"relationships, {before['conflicts']} conflicts\n"
    )

    failures = 0
    for entry in entries:
        path = SAMPLES_DIR / entry["file"]
        if not path.exists():
            print(f"  MISSING  {entry['file']}", file=sys.stderr)
            failures += 1
            continue

        payload = {
            "text": load_text(path),
            "title": entry["title"],
            "source_type": entry["source_type"],
            "date": entry.get("date"),
        }

        try:
            result = call(args.base_url, "/ingest/text", payload)
        except urllib.error.HTTPError as error:
            print(f"  FAIL     {entry['file']}: {error.read().decode()}", file=sys.stderr)
            failures += 1
            continue

        cognee = "cognee" if result["cognified"] else "graph only"
        print(f"  {result['source_id']:9} {result['title'][:44]:44} {cognee}")
        print(f"            {result['detail']}")

    after = call(args.base_url, "/health")
    print(
        f"\nAfter:   {after['sources']} sources, {after['relationships']} "
        f"relationships, {after['conflicts']} conflicts"
    )
    print(
        f"Added:   +{after['sources'] - before['sources']} sources, "
        f"+{after['relationships'] - before['relationships']} relationships"
    )

    if failures:
        print(f"\n{failures} failure(s).", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
