"""Knowledge Explorer - what is actually in the graph."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import api_client as api  # noqa: E402

st.set_page_config(page_title="Knowledge Explorer", page_icon="mag", layout="wide")

st.title("Knowledge Explorer")
st.caption("Every source the graph can cite, and what it is linked to.")

try:
    sources = api.sources()
    entities = api.entities()
except api.ApiError as error:
    st.error(str(error))
    st.stop()

tab_sources, tab_entities, tab_pipeline = st.tabs(["Sources", "Entities", "Pipeline"])

with tab_sources:
    st.caption(f"{len(sources)} sources, newest first.")

    kinds = sorted({s["type"] for s in sources})
    chosen = st.multiselect("Filter by kind", kinds, default=kinds)
    query = st.text_input("Search titles and content")

    shown = [
        s
        for s in sources
        if s["type"] in chosen
        and (
            not query
            or query.lower() in s["title"].lower()
            or query.lower() in s["snippet"].lower()
        )
    ]

    st.caption(f"Showing {len(shown)} of {len(sources)}.")

    for source in shown:
        with st.container(border=True):
            left, right = st.columns([4, 1])
            with left:
                st.markdown(f"**{source['title']}**")
                st.caption(
                    f"`{source['id']}` - {source['type']} - {source['date']}"
                )
            with right:
                if source["linked_entities"]:
                    st.caption(", ".join(source["linked_entities"]))
                else:
                    st.caption("unlinked")
            st.write(source["snippet"])

with tab_entities:
    st.caption(f"{len(entities)} entities.")
    for entity in entities:
        with st.container(border=True):
            st.markdown(f"**{entity['name']}**")
            st.caption(f"`{entity['id']}` - {entity['type']}")

with tab_pipeline:
    st.markdown(
        "Input data\n\n"
        "- Normalisation: spreadsheets, documents, forms and transcripts all "
        "become text\n"
        "- Stored as a citable source, linked to every entity it names\n"
        "- Cognee builds the semantic graph, when configured\n"
        "- Searchable company intelligence, with evidence attached"
    )
