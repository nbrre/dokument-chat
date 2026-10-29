"""Kommandolinje: python -m dokument_chat [mappe]   – still spørsmål, skriv 'q' for å avslutte."""
from __future__ import annotations

import argparse
import os

from .sok import Indeks
from .svar import svar


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="dokument_chat")
    p.add_argument("mappe", nargs="?", default="dokumenter")
    p.add_argument("-s", "--sporsmal", help="Still ett spørsmål og avslutt.")
    p.add_argument("--bare-sok", action="store_true", help="Vis treffene, ikke spør Claude.")
    a = p.parse_args(argv)

    indeks = Indeks.fra_mappe(a.mappe)
    print(f"Lastet {len(indeks.biter)} biter fra {a.mappe}.")
    bare_sok = a.bare_sok or not os.getenv("ANTHROPIC_API_KEY")
    if bare_sok and not a.bare_sok:
        print("(Ingen ANTHROPIC_API_KEY – viser bare søketreff. Se README.)")

    def ett(sp: str) -> None:
        treff = indeks.sok(sp)
        if bare_sok:
            for poeng, bit in treff:
                print(f"\n[{bit.kilde} #{bit.nr}] (poeng {poeng:.2f})\n{bit.tekst[:300]}…")
            if not treff:
                print("Ingen treff.")
        else:
            print("\n" + svar(sp, treff))
            print("\nKilder: " + ", ".join(f"[{i}] {b.kilde} #{b.nr}" for i, (_, b) in enumerate(treff, 1)))

    if a.sporsmal:
        ett(a.sporsmal)
        return 0
    while True:
        try:
            sp = input("\nSpørsmål> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if sp.lower() in ("q", "quit", "avslutt"):
            break
        if sp:
            ett(sp)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
