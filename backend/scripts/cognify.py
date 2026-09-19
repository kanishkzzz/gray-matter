"""
Build the Cognee knowledge graph over the files in backend/data/.

    python scripts/cognify.py
    python scripts/cognify.py --ask "How many paid leave days do employees get?"

This is the original prototype's `main.py`, kept as a one-shot job rather than
something the request path does. Cognifying takes tens of seconds and is not
work an HTTP handler should be doing.

It is optional. The API serves the seeded graph whether or not this has ever
been run; what this adds is semantic recall over the raw documents.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import cognee_engine  # noqa: E402
from app.config import DATA_DIR, settings  # noqa: E402

TEXT_SUFFIXES = {".txt", ".md"}


async def build(ask: str | None) -> int:
    if not settings.llm_configured:
        print("LLM_API_KEY is not set. Copy backend/.env.example to backend/.env")
        print("and fill it in, or skip this step - the API works without it.")
        return 1

    if cognee_engine.get_cognee() is None:
        print("Cognee is not installed or failed to load.")
        print("  pip install -r requirements-cognee.txt")
        return 1

    files = sorted(
        p for p in DATA_DIR.glob("**/*") if p.suffix.lower() in TEXT_SUFFIXES
    )
    if not files:
        print(f"No .txt or .md files in {DATA_DIR}.")
        return 1

    print(f"Adding {len(files)} document(s) from {DATA_DIR}...")
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        ok = await cognee_engine.add_text(f"{path.stem}\n\n{text}")
        print(f"  {'ok  ' if ok else 'FAIL'} {path.name}")

    print("\nBuilding the knowledge graph (this takes a while)...")
    if not await cognee_engine.cognify():
        print("Cognify failed. See the log above.")
        return 1
    print("Done.")

    if ask:
        print(f"\nAsking: {ask}")
        results = await cognee_engine.search(ask)
        if results:
            print("\n".join(results))
        else:
            print("No result.")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ask", help="Run one query against the graph once it is built."
    )
    args = parser.parse_args()
    return asyncio.run(build(args.ask))


if __name__ == "__main__":
    raise SystemExit(main())
