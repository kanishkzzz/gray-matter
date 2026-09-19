"""Ask Gray Matter - question the corpus and inspect what backed the answer."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import api_client as api  # noqa: E402

st.set_page_config(page_title="Ask Gray Matter", page_icon="speech_balloon", layout="wide")

st.title("Ask Gray Matter")
st.caption("Every answer carries the sources it came from.")

if "history" not in st.session_state:
    st.session_state.history = []

for entry in st.session_state.history:
    with st.chat_message("user"):
        st.write(entry["question"])
    with st.chat_message("assistant"):
        st.write(entry["answer"])

question = st.chat_input("Ask something about the company...")

if question:
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching the knowledge graph..."):
            try:
                result = api.ask(question)
            except api.ApiError as error:
                st.error(str(error))
                st.stop()

        st.write(result["answer"])
        st.session_state.history.append(
            {"question": question, "answer": result["answer"]}
        )

        evidence = result["evidence"]
        if evidence:
            st.divider()
            st.markdown(f"**Evidence** - {len(evidence)} sources")
            for source in evidence:
                with st.expander(
                    f"{source['id']} - {source['title']} "
                    f"({source['type']}, {source['date']})"
                ):
                    st.write(source["snippet"])
        else:
            st.info("No indexed source supports an answer to this question.")

        path = result["path"]
        if path and path["edges"]:
            st.divider()
            st.markdown("**Reasoning path**")
            labels = {n["id"]: n["label"] for n in path["nodes"]}
            for edge in path["edges"]:
                st.write(
                    f"`{edge['from']}` {labels.get(edge['from'], '')} "
                    f"--- *{edge['label']}* --> "
                    f"`{edge['to']}` {labels.get(edge['to'], '')}"
                )

        related = result["related_decisions"]
        if related:
            st.divider()
            st.markdown("**Related decisions**")
            for decision in related:
                st.write(
                    f"`{decision['id']}` {decision['title']} "
                    f"- {decision['status']}, {decision['date']}"
                )
