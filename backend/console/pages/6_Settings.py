"""
Settings - what the running backend is actually configured with.

The original page showed three hardcoded values that were true only by
coincidence. These are read from the live service, so they cannot drift from
what is really loaded.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import api_client as api  # noqa: E402

st.set_page_config(page_title="Settings", page_icon="gear", layout="wide")

st.title("Settings")
st.caption("Read from the running backend. Change these in backend/.env.")

try:
    health = api.health()
except api.ApiError as error:
    st.error(str(error))
    st.stop()

engine = health.get("engine", {})

st.subheader("Engine")

col1, col2 = st.columns(2)

with col1:
    st.text_input("LLM provider", value=engine.get("llm_provider", ""), disabled=True)
    st.text_input("LLM model", value=engine.get("llm_model", ""), disabled=True)
    st.text_input(
        "API key",
        value="configured" if engine.get("llm_configured") else "not set",
        disabled=True,
    )

with col2:
    st.text_input(
        "Embedding provider",
        value=engine.get("embedding_provider", ""),
        disabled=True,
    )
    st.text_input(
        "Embedding model", value=engine.get("embedding_model", ""), disabled=True
    )
    st.text_input("API base URL", value=api.BASE_URL, disabled=True)

st.divider()

st.subheader("Status")

if engine.get("cognee_loaded"):
    st.success("Cognee is loaded and serving semantic recall.")
elif engine.get("cognee_enabled"):
    st.info("Cognee is configured and will load on first use.")
else:
    st.warning(
        "Cognee is not active. Retrieval and every structured response still "
        "work; answers are composed from the retrieved sources rather than "
        "phrased by a model."
    )

if engine.get("llm_answers"):
    st.caption("Answer prose: written by the model over retrieved evidence.")
else:
    st.caption("Answer prose: composed extractively from retrieved evidence.")

st.divider()

st.subheader("Graph")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Sources", health["sources"])
col2.metric("Entities", health["entities"])
col3.metric("Relationships", health["relationships"])
col4.metric("Decisions", health["decisions"])
col5.metric("Conflicts", health["conflicts"])

st.divider()

st.subheader("Configuration reference")

st.code(
    "\n".join(
        [
            "# backend/.env",
            "LLM_API_KEY=...",
            "LLM_PROVIDER=gemini",
            "LLM_MODEL=gemini/gemini-3.6-flash",
            "EMBEDDING_PROVIDER=fastembed",
            "EMBEDDING_MODEL=BAAI/bge-small-en-v1.5",
            "EMBEDDING_DIMENSIONS=384",
            "USE_COGNEE=true",
            "USE_LLM_ANSWERS=true",
        ]
    ),
    language="bash",
)
