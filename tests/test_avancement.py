"""Rapport d'avancement (D70) : inactif par défaut, une ligne JSON par événement, jamais d'exception."""

import json

from grappes import avancement
from grappes.search.base import Journal


def lire(f):
    return [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines()]


def test_inactif_sans_variable(monkeypatch, tmp_path):
    monkeypatch.delenv(avancement.VARIABLE, raising=False)
    avancement.signaler("etape", etape="recherche")  # ne fait rien, ne lève rien
    assert list(tmp_path.iterdir()) == []


def test_ecrit_une_ligne_json_par_evenement(monkeypatch, tmp_path):
    f = tmp_path / "av.jsonl"
    monkeypatch.setenv(avancement.VARIABLE, str(f))
    avancement.signaler("plan", prises={"tavily": 3})
    avancement.signaler("etape", etape="verification")
    ev = lire(f)
    assert [e["evenement"] for e in ev] == ["plan", "etape"] and ev[0]["prises"] == {"tavily": 3} and "t" in ev[0]


def test_chemin_illisible_ne_leve_pas(monkeypatch):
    monkeypatch.setenv(avancement.VARIABLE, "/nulle/part/absent/av.jsonl")
    avancement.signaler("etape", etape="x")


def test_chaque_appel_reel_du_journal_est_signale_pas_les_refus(monkeypatch, tmp_path):
    f = tmp_path / "av.jsonl"
    monkeypatch.setenv(avancement.VARIABLE, str(f))
    j = Journal(tmp_path / "j.log")
    j.log("tavily", "mot", "GET https://x.test/s", "200")
    j.log("tavily", "mot", "-", "refusé : hors liste blanche")
    j.log("pages", "", "GET https://y.test", "erreur SearchError")
    ev = lire(f)
    assert [(e["prise"], e["statut"]) for e in ev] == [("tavily", "200"), ("pages", "erreur SearchError")]
