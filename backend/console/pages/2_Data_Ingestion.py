"""
Data Ingestion - the four input kinds from the original prototype.

Each one is reduced to text, sent to the API, stored as a citable source and
linked to whatever entities it names. The original page called `cognee.add`
and `cognee.cognify` directly from the UI thread; that work now happens
server-side so the web app sees the same graph.

Handling is chosen from the file's extension, not from the dropdown. The
dropdown defaults to "Excel / CSV", so trusting it sent every .txt upload into
`pd.read_excel` and crashed the page - the file itself is the reliable signal,
and the dropdown is only a hint for what the reader intended.
"""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import api_client as api  # noqa: E402

st.set_page_config(page_title="Data Ingestion", page_icon="inbox_tray", layout="wide")

st.title("Data Ingestion")
st.caption("Turn business data into sources the graph can cite.")

TABULAR = {".xlsx", ".xls", ".csv"}
TEXTUAL = {".txt", ".md", ".markdown", ".log", ".json"}
AUDIO = {".mp3", ".wav", ".m4a"}


def submit(text: str, title: str, source_type: str, date: str | None = None) -> None:
    if not text.strip():
        st.warning("There is nothing to store - the content is empty.")
        return

    with st.spinner("Adding to the knowledge graph..."):
        try:
            result = api.ingest_text(text, title, source_type, date)
        except api.ApiError as error:
            st.error(str(error))
            return

    st.success(f"{result['title']} stored as {result['source_id']}.")
    st.caption(result["detail"])


data_type = st.selectbox(
    "Data type", ["Excel / CSV", "Text Document", "Form Data", "Voice Note"]
)

# -- Form data needs no file, so it is handled before the uploader ----------
if data_type == "Form Data":
    st.info("Submitted fields become one citable source in the graph.")

    with st.form("company_form"):
        employee_name = st.text_input("Employee name")
        department = st.text_input("Department")
        request = st.text_area("Request")
        submitted = st.form_submit_button("Submit form", type="primary")

    if submitted:
        if not (employee_name or department or request):
            st.warning("Fill in at least one field.")
        else:
            body = "\n".join(
                f"{label}: {value}"
                for label, value in (
                    ("Employee Name", employee_name),
                    ("Department", department),
                    ("Request", request),
                )
                if value
            )
            submit(body, f"Form submission - {employee_name or 'unnamed'}", "document")
    st.stop()

uploaded_file = st.file_uploader(
    "Upload a file",
    type=["xlsx", "xls", "csv", "txt", "md", "markdown", "log", "json", "mp3", "wav", "m4a"],
)

if not uploaded_file:
    st.stop()

suffix = Path(uploaded_file.name).suffix.lower()
stem = Path(uploaded_file.name).stem.replace("_", " ").replace("-", " ").title()

st.success(f"Selected: {uploaded_file.name}")

# What the file actually is, regardless of what the dropdown says.
if suffix in TABULAR:
    handler = "Excel / CSV"
elif suffix in TEXTUAL:
    handler = "Text Document"
elif suffix in AUDIO:
    handler = "Voice Note"
else:
    st.error(f"{suffix or 'This file'} is not a format this page can read.")
    st.stop()

if handler != data_type:
    st.info(
        f"This is a {suffix} file, so it is being handled as "
        f"**{handler}** rather than {data_type}."
    )

# -- Tabular ---------------------------------------------------------------
if handler == "Excel / CSV":
    try:
        if suffix == ".csv":
            frame = pd.read_csv(uploaded_file)
        else:
            frame = pd.read_excel(uploaded_file)
    except Exception as error:
        st.error(f"Could not read {uploaded_file.name}: {error}")
        st.caption(
            "If this is really a text file, rename it with a .txt extension "
            "and upload it again."
        )
        st.stop()

    if frame.empty:
        st.warning("That file has no rows.")
        st.stop()

    st.subheader("Preview")
    st.dataframe(frame, use_container_width=True)
    st.caption(f"{len(frame)} rows, {len(frame.columns)} columns.")

    title = st.text_input("Source title", value=stem)

    if st.button("Ingest spreadsheet", type="primary"):
        # One line per row reads as a sentence to an embedding model, which a
        # raw CSV dump does not.
        lines = [
            ", ".join(f"{column}: {value}" for column, value in row.items())
            for _, row in frame.iterrows()
        ]
        submit("\n".join(lines), title, "document")

# -- Text ------------------------------------------------------------------
elif handler == "Text Document":
    raw = uploaded_file.read()
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        content = raw.decode("latin-1", errors="replace")
        st.warning(
            "This file is not UTF-8. It was decoded as Latin-1, so some "
            "characters may be wrong - check the preview before storing."
        )

    if not content.strip():
        st.warning("That file is empty.")
        st.stop()

    st.subheader("Preview")
    st.text_area("Content", content, height=260)
    st.caption(f"{len(content.split())} words, {len(content)} characters.")

    title = st.text_input("Source title", value=stem)
    source_type = st.selectbox("Record as", ["document", "meeting", "message"], index=0)
    date = st.date_input("Date", value=dt.date.today())

    if st.button("Ingest document", type="primary"):
        submit(content, title, source_type, date.isoformat())

# -- Audio -----------------------------------------------------------------
else:
    st.audio(uploaded_file)
    st.warning(
        "Transcription is not wired up. Paste the transcript below to ingest "
        "it as a source - the audio itself is not stored."
    )

    transcript = st.text_area("Transcript", height=200)
    title = st.text_input("Source title", value=stem)
    date = st.date_input("Date", value=dt.date.today())

    if st.button("Ingest transcript", type="primary"):
        submit(transcript, title, "meeting", date.isoformat())
