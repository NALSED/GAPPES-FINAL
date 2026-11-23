"""914/B : des pages qui se recopient comptent pour un seul endroit ; une page qui recopie le site de l'acteur ne compte pas."""

from __future__ import annotations

from types import SimpleNamespace

from pilote.pont.faits import Provenance, endroits_comptes, faits_candidat


def site_key(hote: str) -> str:  # le moteur n'est pas importable depuis les tests du pilote : l'identité suffit ici
    return hote


def _c(citants, copies, ref="ner:x"):
    return SimpleNamespace(ref=ref, nom="Les Cerfs-Volants Bleus", ville="", registres=set(), citants=set(citants), ner_sites={}, copies=copies)


def test_deux_pages_qui_se_recopient_un_endroit():
    ligne = faits_candidat(_c(["web:a.example", "web:b.example"], {"a.example": "a.example", "b.example": "a.example"}), [], site_key, "FR", Provenance())
    assert ligne["nb_endroits"] == 1 and ligne["faits"]["niveau"] == "a_verifier"
    assert [p.get("copie_de") for p in ligne["faits"]["preuves"]] == [None, "a.example"]  # les deux restent affichées


def test_sans_copie_rien_ne_change():
    ligne = faits_candidat(_c(["web:a.example", "web:b.example"], {}), [], site_key, "FR", Provenance())
    assert ligne["nb_endroits"] == 2 and ligne["faits"]["niveau"] == "sur"


def test_copie_plus_un_site_independant():
    c = _c(["web:a.example", "web:b.example", "web:c.example"], {"a.example": "a.example", "b.example": "a.example"})
    assert faits_candidat(c, [], site_key, "FR", Provenance())["nb_endroits"] == 2


def test_page_qui_recopie_le_site_de_l_acteur_ne_compte_pas():
    c = _c(["web:annuaire.example", "web:autre.example"], {"annuaire.example": "annuaire.example", "cerfs.example": "annuaire.example"}, ref="web:cerfs.example")
    ligne = faits_candidat(c, [], site_key, "FR", Provenance())
    assert ligne["nb_endroits"] == 1  # l'annuaire recopie le site du club : seul autre.example est indépendant


def test_registre_premiere_main_intact():
    ps = [{"source": "r", "classe": "registre", "main": "premiere", "lieu": "registre:r"},
          {"source": "s", "classe": "web", "main": "seconde", "lieu": "page:b.example", "copie_de": "a.example"}]  # fmt: skip
    assert endroits_comptes(ps) == 1
