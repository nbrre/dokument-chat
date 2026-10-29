# 📄 Dokument-chat (RAG med Claude)

Still spørsmål om egne dokumenter – for eksempel regelverk som **CRA, KI-loven og e-faktura** –
og få svar på norsk med **kildehenvisninger**. Svarene bygger bare på dokumentene, og
modellen sier fra når svaret ikke står der i stedet for å gjette.

*Retrieval-Augmented Generation (RAG) chatbot for your own documents, built from scratch with
BM25 search and Claude. Text and examples are in Norwegian.*

![Tester](../../actions/workflows/tester.yml/badge.svg)

## Hvordan det fungerer

```
Dokumenter ──► deles i biter (med overlapp) ──► BM25-indeks
                                                   │
Spørsmål ─────────────────────────────────────────►│──► 4 beste biter ──► Claude ──► svar med [1], [2] …
```

1. **Oppdeling** (`dokument_chat/sok.py`): tekst, Markdown og PDF deles i biter på ca. 120 ord
   med 30 ords overlapp, så setninger ikke kuttes bort mellom to biter.
2. **Søk (retrieval)**: en egen implementasjon av **BM25** – samme rangeringsmetode som mange
   søkemotorer bruker – skrevet med bare Python-standardbiblioteket. Ingen vektordatabase trengs.
3. **Svar (generation)** (`dokument_chat/svar.py`): de beste bitene sendes til Claude i
   `<utdrag>`-markører med kilde. Systemprompten krever kildehenvisning og forbyr gjetting, og
   innholdet i dokumentene behandles som data (vern mot *prompt injection*).

## Kom i gang

```bash
git clone https://github.com/nbrre/dokument-chat.git
cd dokument-chat
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...                  # Windows PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."
```

**Kommandolinje** (bruker mappen `dokumenter/`):

```bash
python -m dokument_chat                       # interaktiv chat
python -m dokument_chat -s "Hvor raskt må en sårbarhet rapporteres etter CRA?"
python -m dokument_chat --bare-sok -s "Når kommer krav om e-faktura?"   # uten API-nøkkel
```

**Nettside** (med opplasting av egne PDF-er):

```bash
streamlit run app.py
```

## Eksempel

```
Spørsmål> Hvor raskt må en sårbarhet rapporteres etter CRA?

Produsenten må sende et tidlig varsel innen 24 timer etter å ha blitt kjent med en aktivt
utnyttet sårbarhet, og en fullstendig melding innen 72 timer [1].

Kilder: [1] cyber_resilience_act.md #1, …
```

## Tester

```bash
python -m unittest -v
```

Testene sjekker at søket finner riktig dokument, at oppdelingen overlapper, og at
Claude-kallet får med kildene (med en falsk klient – ingen API-nøkkel trengs).

## Videre arbeid

- Embeddings/hybrid-søk for bedre treff på synonymer
- Evaluering med et fast sett spørsmål og forventede kilder
- Lagre indeksen på disk for store dokumentsamlinger

## Om meg

Laget av **Barre**, bachelor i informasjonsteknologi/informasjonssikkerhet.

> Eksempeldokumentene er egne, korte oppsummeringer og ikke juridisk rådgivning.

Lisens: MIT
