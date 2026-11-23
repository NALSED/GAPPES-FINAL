"""913/N2 et N3 : une ville écrite par un registre et un SIREN/SIRET d'une même entreprise concordent ; la confirmation A2 en tient compte."""

from __future__ import annotations

import pytest

from pilote.pont.verification import concordance
from pilote.rapprochements import comparer


@pytest.mark.parametrize(("a", "b"), [
    ("Saint-Étienne", "SAINT-ETIENNE"), ("Paris", "Paris 11e Arrondissement"), ("Paris", "PARIS 11"), ("Lyon", "Lyon 3ème"),
    ("L'Isle-d'Abeau", "L ISLE D ABEAU"),
])  # fmt: skip
def test_meme_ville(a: str, b: str) -> None:
    assert comparer("ville", a, b) == "accord"


@pytest.mark.parametrize(("a", "b"), [("Lyon", "Paris"), ("Saint-Denis", "Saint-Dié")])
def test_villes_differentes(a: str, b: str) -> None:
    assert comparer("ville", a, b) == "desaccord"


@pytest.mark.parametrize(("a", "b", "etat"), [
    ("41234567800012", "412345678", "accord"),  # un SIRET et son SIREN : la même entreprise
    ("412 345 678", "412345678", "accord"),
    ("41234567800012", "41234567800020", "desaccord"),  # deux établissements : jamais réunis par A7, jamais concordants ici
    ("412345678", "512345678", "desaccord"),
    ("W381234567", "W381234567", "accord"),  # un numéro RNA se compare tel quel
    ("W381234567", "W381234568", "desaccord"),
])  # fmt: skip
def test_numeros(a: str, b: str, etat: str) -> None:
    assert comparer("numero", a, b) == etat


def test_la_confirmation_a2_voit_la_meme_ville_et_le_meme_siren() -> None:
    e = concordance({"ville": "Saint-Étienne", "numero_officiel": "41234567800012"}, {"ville": "Saint-Etienne", "numero": "412345678"})
    assert e["ville"] == "accord" and e["numero"] == "accord"
