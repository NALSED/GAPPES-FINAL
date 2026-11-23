"""914/A : ce que le site de l'acteur déclare de lui-même. Affiché, jamais une preuve ; même numéro déclaré par deux sites : proposé à une
personne, jamais réuni d'office ; numéro du site différent du registre : alerte, niveau inchangé. Thèmes et numéros inventés."""

from __future__ import annotations

from types import SimpleNamespace

from fastapi.testclient import TestClient
from test_a7_numero import _app_avec, _etat, _p, _sans_splink  # noqa: F401 - la fixture s'applique ici aussi

from pilote import rapprochements
from pilote.formats._commun import texte_declare
from pilote.pont.faits import Provenance, faits_candidat, reunir_declarations


def site_key(hote: str) -> str:  # le moteur n'est pas importable depuis les tests du pilote : l'identité suffit ici
    return hote


def _c(ref="web:cerfs-volants.example", nom="Les Cerfs-Volants Bleus"):
    return SimpleNamespace(ref=ref, nom=nom, ville="", registres=set(), citants=set(), ner_sites={})


def _d(**kw):
    return SimpleNamespace(**{"siren": "", "domaine": "", "type_candidat": "", "liens": {}, **kw})


def test_declarations_d_un_site_reunies():
    assert reunir_declarations([{"ville": "Villebrume"}, {"numero": "412345678", "type_numero": "siren", "methode": "texte"}]) == {
        "ville": "Villebrume", "numero": "412345678", "type_numero": "siren", "methode": "texte"}
    assert "numero" not in reunir_declarations([{"numero": "412345678"}, {"numero": "999888777"}])  # deux numéros : on ne sait pas lequel
    assert reunir_declarations([{"numero": "41234567800011"}, {"numero": "41234567800029"}])["numero"] == "412345678"  # deux établissements : le SIREN


def test_la_declaration_est_affichee_pas_comptee():
    prov = Provenance(declare_par_site={"cerfs-volants.example": {"numero": "412345678", "type_numero": "siren", "ville": "Villebrume"}})
    ligne = faits_candidat(_c(), [], site_key, "FR", prov)
    assert ligne["faits"]["declare"]["numero"] == "412345678"
    assert ligne["numero_officiel"] == "" and ligne["faits"]["niveau"] == "a_verifier" and ligne["nb_endroits"] == 1
    assert "numero_site_different" not in ligne["faits"]


def test_numero_du_site_different_du_registre_alerte_niveau_inchange():
    prov = Provenance(declare_par_site={"cerfs-volants.example": {"numero": "999888777"}})
    sans = faits_candidat(_c(), [_d(siren="412345678")], site_key, "FR", Provenance())
    avec = faits_candidat(_c(), [_d(siren="412345678")], site_key, "FR", prov)
    assert avec["faits"]["numero_site_different"] is True and avec["faits"]["niveau"] == sans["faits"]["niveau"]
    meme = faits_candidat(_c(), [_d(siren="412345678")], site_key, "FR", Provenance(declare_par_site={"cerfs-volants.example": {"numero": "41234567800011"}}))
    assert "numero_site_different" not in meme["faits"]  # le SIRET du même SIREN : pas d'alerte


def test_seul_le_site_de_l_acteur_compte():
    prov = Provenance(declare_par_site={"annuaire.example": {"numero": "412345678"}})
    assert "declare" not in faits_candidat(_c(ref="ner:x"), [], site_key, "FR", prov)["faits"]


def test_meme_numero_declare_propose_jamais_reuni(cfg):
    fiches = [{"nom": "Cerfs-Volants Bleus", "faits": {"preuves": [_p("page:a.example")], "declare": {"numero": "412345678"}}},
              {"nom": "Club Cerf-Volant", "faits": {"preuves": [_p("page:b.example")], "declare": {"numero": "41234567800011"}}},
              {"nom": "Deux établissements A", "faits": {"declare": {"numero": "99988877700011"}}},
              {"nom": "Deux établissements B", "faits": {"declare": {"numero": "99988877700029"}}}]  # fmt: skip
    app, rid = _app_avec(cfg, fiches)
    with TestClient(app):
        bilan = rapprochements.proposer(cfg, app.state.fabrique, rid)
        assert bilan["proposes"] == 1 and "reunis" not in bilan
        cands, [r] = _etat(app, rid)
        assert r.etat == "a_examiner" and r.decide_par == "" and "numero_declare" in r.pourquoi
        assert not cands["Cerfs-Volants Bleus"].relations and cands["Cerfs-Volants Bleus"].nb_endroits == 1
        assert rapprochements.proposer(cfg, app.state.fabrique, rid)["proposes"] == 0  # relancer ne double rien


def test_cellule_d_export():
    assert texte_declare({"numero": "412345678", "type_numero": "siren", "ville": "Villebrume"}) == "SIREN 412345678 · Villebrume"
    assert texte_declare(None) == ""
