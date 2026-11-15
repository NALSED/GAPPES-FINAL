"""Revue de sécurité (D133) : aucune adresse de courriel écrite dans le code ; le contact du User-Agent vient de l'environnement."""

import re
from pathlib import Path

from grappes.contact import user_agent

RACINE = Path(__file__).resolve().parents[1]
COURRIEL = re.compile(r"[\w.+-]+@[\w-]+\.(?:fr|com|net|org)\b")


def test_le_contact_vient_de_la_variable_d_environnement(monkeypatch):
    monkeypatch.delenv("GRAPPES_CONTACT", raising=False)
    assert user_agent("decouverte") == "grappes/0.1 (decouverte) python-urllib"
    monkeypatch.setenv("GRAPPES_CONTACT", "  contact@exemple.invalid \n")
    assert user_agent("decouverte") == "grappes/0.1 (decouverte; contact@exemple.invalid) python-urllib"


def test_aucune_adresse_de_courriel_dans_le_code_du_moteur_ni_de_pilote():
    trouves = []
    for dossier in ("src", "pilote/src"):
        for f in (RACINE / dossier).rglob("*.py"):
            for m in COURRIEL.finditer(f.read_text(encoding="utf-8")):
                if not m.group(0).endswith(("@exemple.fr", "@example.com", "@example.org", "@anthropic.com")):
                    trouves.append(f"{f.relative_to(RACINE)} : {m.group(0).split('@')[1]}")
    assert trouves == []
