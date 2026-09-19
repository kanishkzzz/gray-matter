"""
Gray Matter operator console.

The Streamlit app from the original prototype, kept as the operator-side
surface: ingestion, corpus inspection and engine configuration - the things
the Next.js product deliberately does not expose to readers.

It reads and writes through the API, so it and the web app always see the
same graph.

    streamlit run console/app.py        (from backend/)
"""

from __future__ import annotations

import streamlit as st

import api_client as api

st.set_page_config(
    page_title="Gray Matter Console",
    page_icon="brain",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .main-title { font-size: 40px; font-weight: 600; letter-spacing: -0.02em; }
    .subtitle   { color: #6B6B60; font-size: 17px; }
</style>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("# Gray Matter")
    st.caption("Operator console")
    st.divider()
    st.markdown("### Navigation")
    st.markdown("**Dashboard**")
    st.page_link("pages/1_Ask_Gray_Matter.py", label="Ask Gray Matter")
    st.page_link("pages/2_Data_Ingestion.py", label="Data Ingestion")
    st.page_link("pages/3_Knowledge_Explorer.py", label="Knowledge Explorer")
    st.page_link("pages/4_Company_Insights.py", label="Company Insights")
    st.page_link("pages/5_Truth_Engine.py", label="Truth Engine")
    st.page_link("pages/6_Settings.py", label="Settings")
    st.divider()
    st.caption(f"API: {api.BASE_URL}")

st.markdown(
    '<div class="main-title">Gray Matter</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Company knowledge, with the reasoning kept '
    "attached.</div>",
    unsafe_allow_html=True,
)
st.write("")

try:
    health = api.health()
except api.ApiError as error:
    st.error(str(error))
    st.stop()

engine = health.get("engine", {})

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Sources", health["sources"])
col2.metric("Entities", health["entities"])
col3.metric("Relationships", health["relationships"])
col4.metric("Decisions", health["decisions"])
col5.metric("Conflicts", health["conflicts"])

st.divider()

st.subheader("Engine")

left, right = st.columns(2)

with left:
    with st.container(border=True):
        st.markdown("**Retrieval**")
        st.write("Deterministic graph search over the relational store.")
        st.caption(
            "Always on. Chooses which records answer a question, so evidence "
            "and paths are reproducible and never model-generated."
        )

with right:
    with st.container(border=True):
        st.markdown("**Cognee**")
        if engine.get("cognee_loaded"):
            st.success("Loaded")
        elif engine.get("cognee_enabled"):
            st.info("Configured, not yet loaded (it loads on first use).")
        else:
            st.warning("Not configured - answers are composed extractively.")
        st.caption(
            f"{engine.get('llm_provider', '-')} / "
            f"{engine.get('llm_model', '-')}"
        )

st.divider()

st.subheader("What would you like to do?")

left, right = st.columns(2)

with left:
    with st.container(border=True):
        st.subheader("Ask a question")
        st.write(
            "Search the corpus and see the evidence and reasoning path behind "
            "the answer."
        )
        if st.button("Open Ask", use_container_width=True):
            st.switch_page("pages/1_Ask_Gray_Matter.py")

with right:
    with st.container(border=True):
        st.subheader("Add company data")
        st.write(
            "Spreadsheets, documents, forms and voice notes become citable "
            "sources in the graph."
        )
        if st.button("Open Data Ingestion", use_container_width=True):
            st.switch_page("pages/2_Data_Ingestion.py")

st.divider()

if health["conflicts"]:
    st.subheader("Standing conflicts")
    st.caption(
        "Records that disagree about the same attribute of the same entity. "
        "A superseded decision does not count as a live disagreement."
    )
    for conflict in api.conflicts():
        with st.container(border=True):
            st.markdown(
                f"**{conflict['entity']}** - {conflict['attribute']}"
            )
            for side in conflict["values"]:
                st.write(f"- `{side['value']}` per {side['asserted_by']}")
else:
    st.success("No standing conflicts in the graph.")
