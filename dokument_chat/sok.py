"""Henting (retrieval): deler dokumenter i biter og finner de mest relevante med BM25.

Skrevet med bare Python-standardbiblioteket, så det er lett å forstå hva som skjer
uten en vektordatabase.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

STOPPORD = set("""og i på er det som en et til av for med at har de ikke den om å fra
kan skal vil må eller men så du jeg vi dere seg sin sitt sine hva hvor når hvem
the a an of to and in is are for on with that this be by or as""".split())


@dataclass
class Bit:
    kilde: str
    nr: int
    tekst: str


def ord_i(tekst: str) -> list[str]:
    ordliste = re.findall(r"[a-zæøåA-ZÆØÅ0-9]+", tekst.lower())
    return [o for o in ordliste if o not in STOPPORD and len(o) > 1]


def les_fil(sti: Path) -> str:
    if sti.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader  # valgfri avhengighet
        except ImportError as feil:
            raise RuntimeError("Installer pypdf for å lese PDF-filer: pip install pypdf") from feil
        return "\n".join((s.extract_text() or "") for s in PdfReader(str(sti)).pages)
    return sti.read_text(encoding="utf-8", errors="replace")


def del_opp(tekst: str, kilde: str, maks_ord: int = 120, overlapp: int = 30) -> list[Bit]:
    """Deler teksten i biter på ca. maks_ord ord, med overlapp, og beholder linjeskift."""
    ordstrom: list[str] = []
    for linje in tekst.splitlines():
        if linje.strip():
            ordstrom.extend(linje.split())
            ordstrom.append("\n")
    biter, start, nr = [], 0, 0
    while start < len(ordstrom):
        stykke = " ".join(ordstrom[start:start + maks_ord]).replace(" \n ", "\n").replace(" \n", "\n").strip()
        if stykke:
            biter.append(Bit(kilde, nr, stykke))
            nr += 1
        start += maks_ord - overlapp
    return biter


class Indeks:
    def __init__(self, biter: list[Bit], k1: float = 1.5, b: float = 0.75):
        self.biter = biter
        self.k1, self.b = k1, b
        self.tf = [Counter(ord_i(bit.tekst)) for bit in biter]
        self.lengder = [sum(t.values()) for t in self.tf]
        self.snitt = (sum(self.lengder) / len(self.lengder)) if biter else 0
        df: Counter = Counter()
        for t in self.tf:
            df.update(t.keys())
        n = len(biter)
        self.idf = {o: math.log(1 + (n - f + 0.5) / (f + 0.5)) for o, f in df.items()}

    @classmethod
    def fra_mappe(cls, mappe: str | Path) -> "Indeks":
        biter: list[Bit] = []
        for sti in sorted(Path(mappe).iterdir()):
            if sti.suffix.lower() in (".txt", ".md", ".pdf"):
                biter.extend(del_opp(les_fil(sti), sti.name))
        if not biter:
            raise ValueError(f"Fant ingen .txt/.md/.pdf-filer i {mappe}")
        return cls(biter)

    def sok(self, sporsmal: str, k: int = 4) -> list[tuple[float, Bit]]:
        q = ord_i(sporsmal)
        poeng = []
        for i, tf in enumerate(self.tf):
            s = 0.0
            for o in q:
                if o in tf:
                    f = tf[o]
                    s += self.idf[o] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * self.lengder[i] / self.snitt))
            if s > 0:
                poeng.append((s, self.biter[i]))
        poeng.sort(key=lambda x: x[0], reverse=True)
        return poeng[:k]
