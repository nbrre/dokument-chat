import pathlib
import unittest
from types import SimpleNamespace

from dokument_chat.sok import Indeks, del_opp
from dokument_chat import svar as svarmodul

DOK = pathlib.Path(__file__).resolve().parent.parent / "dokumenter"


class TestSok(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.indeks = Indeks.fra_mappe(DOK)

    def test_finner_riktig_dokument(self):
        cases = {
            "Hvor raskt må en sårbarhet rapporteres?": "cyber_resilience_act.md",
            "Når må vi sende EHF faktura?": "e_faktura_norge.md",
            "Må chatbot opplyse om at den er KI?": "ki_loven.md",
        }
        for sporsmal, forventet in cases.items():
            with self.subTest(sporsmal=sporsmal):
                self.assertEqual(self.indeks.sok(sporsmal)[0][1].kilde, forventet)

    def test_ingen_treff_gir_tom_liste(self):
        self.assertEqual(self.indeks.sok("fotball pizza"), [])

    def test_del_opp_overlapper(self):
        tekst = " ".join(f"ord{i}" for i in range(300))
        biter = del_opp(tekst, "x", maks_ord=100, overlapp=20)
        self.assertGreater(len(biter), 2)
        self.assertIn("ord80", biter[0].tekst)
        self.assertIn("ord80", biter[1].tekst)


class FalskKlient:
    def __init__(self):
        self.messages = self
        self.kall = None

    def create(self, **kw):
        self.kall = kw
        return SimpleNamespace(content=[SimpleNamespace(type="text", text="Innen 24 timer [1].")])


class TestSvar(unittest.TestCase):
    def test_svar_sender_utdrag_med_kilde(self):
        indeks = Indeks.fra_mappe(DOK)
        treff = indeks.sok("Hvor raskt må en sårbarhet rapporteres?")
        klient = FalskKlient()
        tekst = svarmodul.svar("Hvor raskt?", treff, klient=klient)
        self.assertEqual(tekst, "Innen 24 timer [1].")
        melding = klient.kall["messages"][0]["content"]
        self.assertIn('kilde="cyber_resilience_act.md"', melding)

    def test_ingen_treff_spor_ikke_modellen(self):
        self.assertIn("står ikke", svarmodul.svar("x", [], klient=None))


if __name__ == "__main__":
    unittest.main()
