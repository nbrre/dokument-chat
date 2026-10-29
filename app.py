"""Nettside for dokument-chatten. Start med:  streamlit run app.py"""
import os
import tempfile
from pathlib import Path

import streamlit as st

from dokument_chat.sok import Indeks
from dokument_chat.svar import svar

st.set_page_config(page_title="Dokument-chat", page_icon="📄")
st.title("📄 Dokument-chat")
st.write("Still spørsmål om dokumentene dine. Svarene bygger bare på dokumentene og viser kildene.")

opplastet = st.file_uploader("Last opp egne dokumenter (valgfritt)", type=["txt", "md", "pdf"], accept_multiple_files=True)


@st.cache_resource
def standard_indeks():
    return Indeks.fra_mappe(Path(__file__).parent / "dokumenter")


if opplastet:
    mappe = Path(tempfile.mkdtemp())
    for f in opplastet:
        (mappe / Path(f.name).name).write_bytes(f.getvalue())
    indeks = Indeks.fra_mappe(mappe)
else:
    indeks = standard_indeks()
st.caption(f"{len(indeks.biter)} tekstbiter lastet.")

if "logg" not in st.session_state:
    st.session_state.logg = []
for rolle, tekst in st.session_state.logg:
    st.chat_message(rolle).write(tekst)

if sporsmal := st.chat_input("Spør om noe …"):
    st.chat_message("user").write(sporsmal)
    treff = indeks.sok(sporsmal)
    if os.getenv("ANTHROPIC_API_KEY"):
        with st.spinner("Claude leser utdragene …"):
            tekst = svar(sporsmal, treff)
    else:
        tekst = "(Ingen API-nøkkel – viser bare beste utdrag)\n\n" + (treff[0][1].tekst if treff else "Ingen treff.")
    kilder = ", ".join(f"[{i}] {b.kilde}" for i, (_, b) in enumerate(treff, 1))
    tekst += f"\n\n*Kilder: {kilder or 'ingen'}*"
    st.chat_message("assistant").write(tekst)
    st.session_state.logg += [("user", sporsmal), ("assistant", tekst)]
