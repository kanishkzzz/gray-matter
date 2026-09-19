"""
Company Insights - metrics read off the live graph.

The original page hardcoded four employees and three departments. These are
counted from whatever the graph currently holds, so ingesting a document moves
the numbers.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import api_client as api  # noqa: E402

st.set_page_config(page_title="Company Insights", page_icon="bar_chart", layout="wide")

st.title("Company Insights")
st.caption("Counted from the graph, not hardcoded.")

try:
    health = api.health()
    decisions = api.decisions()
    sources = api.sources()
except api.ApiError as error:
    st.error(str(error))
    st.stop()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Sources", health["sources"])
col2.metric("Entities", health["entities"])
col3.metric("Relationships", health["relationships"])
col4.metric("Decisions", health["decisions"])
col5.metric("Conflicts", health["conflicts"])

st.divider()

st.subheader("Decisions by status")

by_status: dict[str, int] = {}
for decision in decisions:
    by_status[decision["status"]] = by_status.get(decision["status"], 0) + 1

st.bar_chart(by_status)

st.divider()

st.subheader("Sources by kind")

by_kind: dict[str, int] = {}
for source in sources:
    by_kind[source["type"]] = by_kind.get(source["type"], 0) + 1

st.bar_chart(by_kind)

st.divider()

st.subheader("Decision register")

st.dataframe(
    [
        {
            "ID": d["id"],
            "Decision": d["title"],
            "Date": d["date"],
            "Status": d["status"],
        }
        for d in decisions
    ],
    use_container_width=True,
    hide_index=True,
)

st.divider()

st.subheader("Decision detail")

selected = st.selectbox(
    "Decision",
    [d["id"] for d in decisions],
    format_func=lambda i: (
        f"{i} - " + next(d["title"] for d in decisions if d["id"] == i)
    ),
)

if selected:
    try:
        detail = api.decision(selected)
    except api.ApiError as error:
        st.error(str(error))
    else:
        st.markdown(f"### {detail['title']}")
        st.caption(
            f"`{detail['id']}` - {detail['status']} - {detail['date']} - "
            f"decided by {detail['decided_by']}"
        )
        st.write(detail["rationale"])

        if detail["evidence"]:
            st.markdown("**Evidence**")
            for source in detail["evidence"]:
                with st.expander(f"{source['id']} - {source['title']}"):
                    st.write(source["snippet"])

        if detail["implemented_by"]:
            st.markdown("**Implemented by**")
            for ticket in detail["implemented_by"]:
                st.write(
                    f"`{ticket['key']}` {ticket['title']} - {ticket['status']}"
                )

        if detail["affects"]:
            st.markdown("**Affects**")
            st.write(", ".join(e["name"] for e in detail["affects"]))
