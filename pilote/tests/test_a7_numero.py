"""A7 (spec 912) : deux fiches qui portent le même numéro officiel sont réunies d'office ; un rapprochement confirmé met à jour le
nombre d'endroits. Aucune fiche n'est effacée, et tout se défait."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from pilote import rapprochements
from pilote.app import creer_app
from pilote.base import Candidat, Journal, Rapprochement, Recherche


@pytest.fixture(autouse=True)
def _sans_splink(monkeypatch):
    monkeypatch.setattr(rapprochements, "_scorer", lambda fiches, seuil: [])


def _p(lieu, main="seconde"):
    return {"source": "s", "classe": "web", "main": main, "lieu": lieu}


def _app_avec(cfg, fiches):
    app = creer_app(cfg)
    with app.state.fabrique.begin() as s:
        r = Recherche(qui="test", sujet={"quoi": "x"}, parametres={}, etat="terminee")
        s.add(r)
        s.flush()
        for f in fiches:
            s.add(Candidat(recherche_id=r.id, genre_source="web", pays="FR", trouve_par=["x"], **{"nb_endroits": 1, "relations": [], **f}))
        return app, r.id


def _etat(app, rid):
    with app.state.fabrique() as s:
        cands = {c.nom: c for c in s.scalars(select(Candidat).where(Candidat.recherche_id == rid))}
        return cands, s.scalars(select(Rapprochement).where(Rapprochement.recherche_id == rid)).all()


def test_meme_siren_ou_siret_du_meme_siren_reunis_d_office(cfg):
    fiches = [{"nom": "Atelier du Phare", "numero_officiel": "412 345 678", "faits": {"preuves": [_p("page:a.example")]}},
              {"nom": "ATELIER PHARE SARL", "numero_officiel": "41234567800021", "faits": {"preuves": [_p("page:b.example")]}},
              {"nom": "Club des Vents", "numero_officiel": "999888777", "faits": {}}]  # fmt: skip
    app, rid = _app_avec(cfg, fiches)
    with TestClient(app):
        bilan = rapprochements.proposer(cfg, app.state.fabrique, rid)
        assert bilan["reunis"] == 1 and bilan["proposes"] == 0
        cands, [r] = _etat(app, rid)
        assert r.etat == "confirme" and r.confiance == 1.0 and r.decide_par == "pilote" and r.pourquoi == {"numero_officiel": "même numéro officiel (412345678)"}
        a, b = cands["Atelier du Phare"], cands["ATELIER PHARE SARL"]
        assert {x["vers"] for x in a.relations if x["type"] == "meme_entite"} == {"ATELIER PHARE SARL"}
        assert a.nb_endroits == 2 and b.nb_endroits == 2 and cands["Club des Vents"].nb_endroits == 1  # deux pages distinctes, comptées une fois chacune
        assert rapprochements.proposer(cfg, app.state.fabrique, rid).get("reunis", 0) == 0  # relancer ne double rien
        with app.state.fabrique() as s:
            assert [j.detail["n"] for j in s.scalars(select(Journal).where(Journal.evenement == "rapprochements_reunis_par_numero"))] == [1]


def test_separer_defait_le_lien_et_rend_le_compte_d_avant(cfg):
    fiches = [{"nom": "A", "numero_officiel": "412345678", "faits": {"preuves": [_p("page:a.example")]}},
              {"nom": "B", "numero_officiel": "412345678", "faits": {"preuves": [_p("page:b.example")]}}]  # fmt: skip
    app, rid = _app_avec(cfg, fiches)
    with TestClient(app):
        rapprochements.proposer(cfg, app.state.fabrique, rid)
        _, [r] = _etat(app, rid)
        rapprochements.trancher(cfg, app.state.fabrique, r.id, "separe", "t")
        cands, [r] = _etat(app, rid)
        assert r.etat == "separe" and cands["A"].nb_endroits == 1 and cands["B"].nb_endroits == 1 and not cands["A"].relations
        assert rapprochements.proposer(cfg, app.state.fabrique, rid).get("reunis", 0) == 0  # la décision d'une personne n'est pas refaite d'office


def test_un_rapprochement_confirme_en_tri_met_a_jour_le_nombre_d_endroits(cfg):
    fiches = [{"nom": "Club des Vents", "faits": {"preuves": [_p("page:a.example"), _p("page:c.example")]}, "nb_endroits": 2},
              {"nom": "Club des vents de Lorient", "faits": {"preuves": [_p("page:a.example"), _p("page:b.example")]}, "nb_endroits": 2}]  # fmt: skip
    app, rid = _app_avec(cfg, fiches)
    with TestClient(app):
        with app.state.fabrique.begin() as s:
            ids = [c.id for c in s.scalars(select(Candidat).where(Candidat.recherche_id == rid).order_by(Candidat.id))]
            r = Rapprochement(recherche_id=rid, a=ids[0], b=ids[1], confiance=0.6, pourquoi={})
            s.add(r)
            s.flush()
            ident = r.id
        rapprochements.trancher(cfg, app.state.fabrique, ident, "confirme", "t")
        cands, _ = _etat(app, rid)
        assert {c.nb_endroits for c in cands.values()} == {3}  # a, b, c : la page commune n'est comptée qu'une fois


def test_numeros_differents_absents_ou_trop_courts_rien_n_est_reuni(cfg):
    fiches = [{"nom": "A", "numero_officiel": "412345678", "faits": {}}, {"nom": "B", "numero_officiel": "412345679", "faits": {}},
              {"nom": "C", "numero_officiel": "", "faits": {}}, {"nom": "D", "numero_officiel": "", "faits": {}},
              {"nom": "E", "numero_officiel": "12", "faits": {}}, {"nom": "F", "numero_officiel": "12", "faits": {}}]  # fmt: skip
    app, rid = _app_avec(cfg, fiches)
    with TestClient(app):
        assert rapprochements.proposer(cfg, app.state.fabrique, rid).get("reunis", 0) == 0


def test_un_siege_et_son_etablissement_lies_par_la_source_restent_deux_fiches(cfg):
    fiches = [{"nom": "Atelier du Phare", "numero_officiel": "41234567800013", "faits": {}, "relations": [{"type": "etablissement", "vers": "Atelier du Phare Lorient"}]},
              {"nom": "Atelier du Phare Lorient", "numero_officiel": "41234567800021", "faits": {}}]  # fmt: skip
    app, rid = _app_avec(cfg, fiches)
    with TestClient(app):
        assert rapprochements.proposer(cfg, app.state.fabrique, rid).get("reunis", 0) == 0


def test_une_fiche_de_personne_n_est_jamais_reunie_d_office(cfg):
    fiches = [{"nom": "A", "numero_officiel": "412345678", "genre_de_chose": "personne", "faits": {}}, {"nom": "B", "numero_officiel": "412345678", "faits": {}}]
    app, rid = _app_avec(cfg, fiches)
    with TestClient(app):
        assert rapprochements.proposer(cfg, app.state.fabrique, rid).get("reunis", 0) == 0


def test_deux_siret_differents_d_un_meme_siren_restent_deux_etablissements(cfg):
    fiches = [{"nom": "Atelier du Phare Lorient", "numero_officiel": "41234567800013", "faits": {}}, {"nom": "Atelier du Phare Colmar", "numero_officiel": "41234567800021", "faits": {}}]
    app, rid = _app_avec(cfg, fiches)
    with TestClient(app):
        assert rapprochements.proposer(cfg, app.state.fabrique, rid).get("reunis", 0) == 0
