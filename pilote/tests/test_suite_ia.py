"""Assistant IA (3.8.09) : le registre d'opérations (sur le modèle des formats de sortie) et l'appel à l'agent,
en silence (claude -p) — rien de ce qui est testé ici n'appelle le vrai agent."""

from __future__ import annotations

import subprocess

import pytest

from fastapi.testclient import TestClient

from pilote import operations_ia, suite_ia
from pilote.app import creer_app


def test_les_trois_operations_se_declarent_et_savent_construire_leur_invite():
    ops = {o["id"]: o for o in operations_ia.vue()}
    assert {"resumer", "classer", "extraire_mots_cles"} <= set(ops)
    for o in ops.values():
        assert o["champ_sortie"] and o["nom"] and o["description"]
    decls = operations_ia.decouvrir()
    assert "FFSA" in decls["resumer"]["module"].prompt({"nom": "FFSA"}, {})
    assert "sport" in decls["classer"]["module"].prompt({"nom": "x"}, {"categories": "sport, culture"})
    assert "3" in decls["extraire_mots_cles"]["module"].prompt({"nom": "x"}, {"maximum": "3"})


def test_route_api_operations_ia(cfg):
    with TestClient(creer_app(cfg)) as c:
        ids = {o["id"] for o in c.get("/api/operations_ia").json()}
    assert {"resumer", "classer", "extraire_mots_cles"} <= ids


def test_commande_silencieuse_passe_le_modele_choisi():
    assert suite_ia.commande("", "fais ceci") == ["claude", "-p", "fais ceci"]
    assert suite_ia.commande("haiku", "fais ceci") == ["claude", "-p", "fais ceci", "--model", "haiku"]


def test_demander_leve_une_erreur_claire_sans_agent_installe(monkeypatch):
    def leve(*a, **k):
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "run", leve)
    with pytest.raises(OSError, match="n'est pas installé"):
        suite_ia.demander("", "x")


def test_demander_leve_une_erreur_claire_sur_sortie_vide(monkeypatch):
    class Faux:
        returncode = 0
        stdout = "   "
        stderr = ""

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: Faux())
    with pytest.raises(ValueError, match="rien rendu"):
        suite_ia.demander("", "x")


def test_demander_rend_la_sortie_de_l_agent(monkeypatch):
    class Faux:
        returncode = 0
        stdout = "voici le résumé"
        stderr = ""

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: Faux())
    assert suite_ia.demander("", "x") == "voici le résumé"


def test_appliquer_construit_l_invite_de_l_operation_choisie(monkeypatch):
    vus = []
    monkeypatch.setattr(suite_ia, "demander", lambda modele, prompt: vus.append((modele, prompt)) or "ok")
    decl = operations_ia.decouvrir()["resumer"]
    assert suite_ia.appliquer(decl, {"nom": "FFSA"}, {}, modele="sonnet") == "ok"
    assert vus[0][0] == "sonnet" and "FFSA" in vus[0][1]


def test_appliquer_lignes_pose_le_champ_et_la_marque(monkeypatch):
    monkeypatch.setattr(suite_ia, "demander", lambda modele, prompt: "un résumé")
    decl = operations_ia.decouvrir()["resumer"]
    lignes = [{"nom": "FFSA"}, {"nom": "FFBB"}]
    bilan = suite_ia.appliquer_lignes(lignes, decl, {"modele": "", "marquer": True})
    assert bilan == {"ia_appels": 2}
    assert all(l["resume_ia"] == "un résumé" and l["ia_marque"] == ["resume_ia"] for l in lignes)


def test_appliquer_lignes_sans_marquer_pose_le_champ_sans_la_marque(monkeypatch):
    monkeypatch.setattr(suite_ia, "demander", lambda modele, prompt: "un résumé")
    decl = operations_ia.decouvrir()["resumer"]
    lignes = [{"nom": "FFSA"}]
    suite_ia.appliquer_lignes(lignes, decl, {"modele": "", "marquer": False})
    assert lignes[0]["resume_ia"] == "un résumé" and "ia_marque" not in lignes[0]


def test_appliquer_lignes_garde_le_resultat_sans_le_champ_ia_si_l_agent_echoue(monkeypatch):
    def demande(modele, prompt):
        raise OSError("l'agent Claude Code n'a pas pu répondre : panne")

    monkeypatch.setattr(suite_ia, "demander", demande)
    decl = operations_ia.decouvrir()["resumer"]
    lignes = [{"nom": "FFSA"}]
    signales = []
    bilan = suite_ia.appliquer_lignes(lignes, decl, {"modele": "", "marquer": True}, signaler=lambda *a, **k: signales.append((a, k)))
    assert bilan == {"ia_appels": 0, "ia_echecs": 1}
    assert "resume_ia" not in lignes[0] and "ia_marque" not in lignes[0]
    assert signales and signales[0][0] == ("ia_echec",)
