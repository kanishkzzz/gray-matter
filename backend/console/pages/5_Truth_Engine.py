"""Truth Engine - what a proposed change would contradict."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import api_client as api  # noqa: E402

st.set_page_config(page_title="Truth Engine", page_icon="warning", layout="wide")

st.title("Truth Engine")
st.caption(
    "Describe a change. The graph reports what it touches and what it "
    "contradicts."
)

change = st.text_area(
    "Proposed change",
    placeholder="Change payment database from MySQL to PostgreSQL",
    height=100,
)

if st.button("Analyse change", type="primary"):
    if not change.strip():
        st.warning("Describe the change first.")
        st.stop()

    with st.spinner("Checking against the graph..."):
        try:
            result = api.analyze(change)
        except api.ApiError as error:
            st.error(str(error))
            st.stop()

    conflicts = result["conflicts"]

    if conflicts:
        st.subheader(f"{len(conflicts)} conflict(s)")
        for conflict in conflicts:
            with st.container(border=True):
                severity = conflict["severity"]
                banner = st.error if severity == "high" else st.warning
                banner(
                    f"{conflict['entity']} - the graph says "
                    f"**{conflict['existing_value']}**, this change proposes "
                    f"**{conflict['proposed_value']}** ({severity})"
                )
                st.markdown("**Evidence on both sides**")
                for source in conflict["evidence"]:
                    with st.expander(
                        f"{source['id']} - {source['title']} ({source['date']})"
                    ):
                        st.write(source["snippet"])
                if conflict["requires_review"]:
                    st.caption("Requires review before proceeding.")
    elif result["affected"]:
        st.success("No conflict found with what the graph currently records.")
    else:
        st.info(
            "Nothing in the graph matches this change. No entity, decision or "
            "ticket was found - so no impact is claimed."
        )

    if result["affected"]:
        st.divider()
        st.subheader("Affected")
        st.write(", ".join(e["name"] for e in result["affected"]))

    if result["related_decisions"]:
        st.divider()
        st.subheader("Related decisions")
        for decision in result["related_decisions"]:
            st.write(
                f"`{decision['id']}` {decision['title']} - "
                f"{decision['status']}, {decision['date']}"
            )

    if result["related_tickets"]:
        st.divider()
        st.subheader("Related tickets")
        for ticket in result["related_tickets"]:
            st.write(f"`{ticket['key']}` {ticket['title']} - {ticket['status']}")

    path = result["path"]
    if path["edges"]:
        st.divider()
        st.subheader("Relationship path")
        labels = {n["id"]: n["label"] for n in path["nodes"]}
        for edge in path["edges"]:
            st.write(
                f"`{edge['from']}` {labels.get(edge['from'], '')} "
                f"--- *{edge['label']}* --> "
                f"`{edge['to']}` {labels.get(edge['to'], '')}"
            )
