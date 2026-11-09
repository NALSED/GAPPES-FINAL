"""14.4 (retour du 08/11/2026) : un test de complétude pour que l'inventaire (14.3) le reste — un ajout non
déclaré (outil, source, format, opération IA) doit faire rougir ce test avant le commit, pas être découvert
plus tard par Aide ou l'Assistant IA qui n'en sauraient rien."""

from __future__ import annotations

from pilote import formats as _formats
from pilote import inventaire, operations_ia, suite
from pilote.sources import charger_sources


def test_toutes_les_sources_reelles_sont_dans_l_inventaire(cfg):
    decls, problemes = charger_sources(cfg)
    assert not problemes
    ids_inventaire = {s["id"] for s in inventaire.sources(cfg)}
    assert ids_inventaire == set(decls)
    # ce qu'une source trouve/consomme/produit vient de SA déclaration, jamais inventé ici
    une = next(s for s in inventaire.sources(cfg) if s["id"] == "tavily")
    assert une["trouve"] and une["main"] in ("premiere", "seconde") and une["cout"] in ("payant", "gratuit")


def test_tous_les_outils_reels_sont_dans_l_inventaire(cfg):
    e = suite.charger(cfg)
    ids_attendus = {o["id"] for o in e["outils"]}
    ids_inventaire = {o["id"] for o in inventaire.outils(cfg)}
    assert ids_inventaire == ids_attendus
    # les dix outils livrés ont bien un genre (relie l'outil aux valeurs acceptées de vocabulaires())
    livres = {o["id"]: o for o in inventaire.outils(cfg) if o["nature"] == "modele"}
    assert {"si", "filtre", "fusion", "format"} <= set(livres)
    assert all(o["genre"] for o in livres.values())


def test_tous_les_formats_sont_dans_l_inventaire(cfg):
    ids_attendus = set(_formats.decouvrir(cfg))
    ids_inventaire = {f["id"] for f in inventaire.formats(cfg)}
    assert ids_inventaire == ids_attendus and "csv" in ids_inventaire


def test_toutes_les_operations_ia_sont_dans_l_inventaire():
    ids_attendus = {o["id"] for o in operations_ia.vue()}
    ids_inventaire = {o["id"] for o in inventaire.operations_ia()}
    assert ids_inventaire == ids_attendus and {"resumer", "classer", "extraire_mots_cles"} <= ids_inventaire


def test_les_vocabulaires_fermes_viennent_des_constantes_reelles():
    # 10.2 : exactement le défaut que ce test doit attraper avant un commit, pas après — « fusion » et « rsshub »
    # avaient été oubliés du registre équivalent côté JS. Ici, dérivé des mêmes constantes que le moteur applique.
    v = inventaire.vocabulaires()
    assert "nom" in v["champs_condition"] and "ville" in v["champs_condition"]
    assert "egal" in v["comparateurs_condition"] and "non_vide" in v["comparateurs_condition"]
    assert v["niveaux_fusion"] == ["large", "normal", "strict"]
    assert "" in v["efforts_ia"] and "high" in v["efforts_ia"]


def test_les_actions_viennent_des_routes_reelles_de_l_application(cfg):
    from fastapi.testclient import TestClient

    from pilote.app import creer_app

    with TestClient(creer_app(cfg)) as c:
        app_routes = c.app.routes
    actions = inventaire.actions(app_routes)
    chemins = {a["chemin"] for a in actions}
    assert "/api/suite/sources" in chemins and "/api/suite/lancer" in chemins
    assert all(a["methode"] not in ("HEAD", "OPTIONS") for a in actions)
    assert inventaire.actions(None) == []  # jamais devinée hors d'une application montée


def test_inventaire_complet_rassemble_les_six_parties(cfg):
    inv = inventaire.inventaire(cfg)
    assert set(inv) == {"sources", "outils", "formats", "operations_ia", "vocabulaires", "actions"}
    assert inv["sources"] and inv["outils"] and inv["formats"] and inv["operations_ia"] and inv["vocabulaires"]
