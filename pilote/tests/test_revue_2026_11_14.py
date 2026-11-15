"""Relecture intégrale du 14/11/2026 (pilote) : un test par défaut corrigé. Noms et thèmes inventés."""

from __future__ import annotations

import json
import sys

from pilote import mentions
from pilote.adaptateurs import programmes


def test_fiabilite_lue_par_etiquette_de_prise(tmp_path):
    """Un nom trouvé par un flux garde l'étiquette de la prise (« rss-… ») : la lettre de sa source doit être retrouvée, pas « F »."""
    (tmp_path / "lancement.json").write_text(json.dumps({"jetons": {"rss-jardins": "flux_perso", "sirene_naf": "annuaire"}}), encoding="utf-8")
    lettres = mentions.fiabilites_par_jeton(tmp_path, {"flux_perso": "B", "annuaire": "A"})
    assert lettres["rss-jardins"] == "B"
    assert lettres["sirene_naf"] == "A"
    assert lettres["flux_perso"] == "B"  # l'identifiant de la source reste lisible tel quel


def test_fiabilite_sans_fichier_de_lancement(tmp_path):
    assert mentions.fiabilites_par_jeton(tmp_path, {"annuaire": "A"}) == {"annuaire": "A"}
    (tmp_path / "lancement.json").write_text("pas du json", encoding="utf-8")
    assert mentions.jetons_de_la_recherche(tmp_path) == {}
    (tmp_path / "lancement.json").write_text("[]", encoding="utf-8")
    assert mentions.jetons_de_la_recherche(tmp_path) == {}


def test_programme_local_ne_recoit_pas_les_cles_des_autres_sources(monkeypatch):
    monkeypatch.setenv("CLE_SOURCE_JARDINS", "secret-inventé")
    monkeypatch.setenv("VARIABLE_ORDINAIRE", "visible")
    code = "import json,os;print(json.dumps([{'nom':os.environ.get('CLE_SOURCE_JARDINS','absente'),'origine':os.environ.get('VARIABLE_ORDINAIRE','absente')}]))"
    script = {"commande": [sys.executable, "-c", code]}
    assert programmes.executer(script, {})[0]["nom"] == "secret-inventé"  # sans consigne : environnement hérité, comme avant
    rendu = programmes.executer(script, {}, sans_variables=("CLE_SOURCE_JARDINS",))[0]
    assert rendu == {"nom": "absente", "origine": "visible"}


def test_message_serveur_mcp_muet_ne_parle_plus_du_catalogue():
    import inspect

    from pilote import adaptateurs

    assert "serveur du catalogue" not in inspect.getsource(adaptateurs)


def test_role_enrichir_choisi_a_l_ajout_reste_enrichir():
    from pilote import suite_reel

    assert suite_reel._roles_ajout("ENRICHIR") == ["enrichir"]  # donnait « chercher » : la source partait chercher des noms
    assert suite_reel._roles_ajout("VERIFIER") == ["verifier"]
    assert suite_reel._roles_ajout("CHERCHER") == ["chercher"]
    commun = suite_reel._commun_ajout({"cat": "perso", "role": "ENRICHIR", "nom": "Annuaire des jardins"})
    assert commun["roles"] == ["enrichir"]


def test_declaration_ajoutee_garde_le_role_enrichir():
    from pilote import sources_ajout

    d = sources_ajout._commun({"nom": "Annuaire des jardins", "roles": ["enrichir"]}, "annuaire-des-jardins", "api")
    assert d["roles"] == ["enrichir"]


def test_jointure_sans_cle_ne_touche_pas_les_fiches_sans_numero(tmp_path):
    """Une ligne du second fichier sans numéro complétait TOUTES les fiches sans numéro avec sa ville."""
    from pilote import fichier_local as fl

    principal = tmp_path / "principal.csv"
    principal.write_text("nom,numero\nAtelier des Jardins,111\nCercle des Potagers,\n", encoding="utf-8")
    second = tmp_path / "second.csv"
    second.write_text("numero,ville\n111,Villebois\n,Montclair\n", encoding="utf-8")
    spec = {"format": "csv", "colonnes": {"nom": "nom", "numero": "numero"},
            "jointures": [{"fichier": str(second), "format": "csv", "cle": "numero", "colonnes": {"ville": "ville"}}]}
    fl.importer(principal, "jardins", tmp_path, spec)
    assert fl.exact(tmp_path, "jardins", "Atelier des Jardins")[0]["ville"] == "Villebois"
    assert "ville" not in fl.exact(tmp_path, "jardins", "Cercle des Potagers")[0]


def test_base_sqlite_adoptee_sans_table_meta(tmp_path):
    import sqlite3

    from pilote import fichier_local as fl

    f = fl.chemin_base(tmp_path, "adoptee")
    f.parent.mkdir(parents=True)
    con = sqlite3.connect(f)
    con.executescript("CREATE TABLE donnees (id INTEGER PRIMARY KEY, nom TEXT); CREATE TABLE noms (id INTEGER PRIMARY KEY, nom_n TEXT, donnee INTEGER);")
    con.close()
    assert fl.meta(tmp_path, "adoptee") == {}


def test_fichier_de_prise_qui_n_est_pas_un_dictionnaire(tmp_path):
    from pilote import ajout

    f = tmp_path / "liste.yaml"
    f.write_text("- un\n- deux\n", encoding="utf-8")
    assert ajout._id_du_fichier(f) == ""


def test_source_scrapling_sans_scrapling_installe_dit_pourquoi(monkeypatch):
    import builtins

    from pilote.adaptateurs import ErreurSource
    from pilote.adaptateurs import scrapling as sc

    vrai_import = builtins.__import__

    def sans_scrapling(nom, *a, **k):
        if nom.startswith("scrapling"):
            raise ImportError(nom)
        return vrai_import(nom, *a, **k)

    monkeypatch.setattr(builtins, "__import__", sans_scrapling)
    try:
        sc.convertir("<html></html>", {"liste": "li", "champs": {"nom": "a::text"}})
    except ErreurSource as exc:
        assert "pas installé" in str(exc)
    else:
        raise AssertionError("une ErreurSource était attendue")


def test_nombre_de_sources_compte_des_sources_pas_des_prises():
    from pilote import suite_plan

    ligne = {"nom": "Atelier des Jardins", "trouve_par": ["annuaire_naf", "annuaire_nom"]}
    lc = {"champ": "_corroboration", "comparateur": "min", "valeurs": ["2"]}
    jetons = {"annuaire_naf": "annuaire", "annuaire_nom": "annuaire"}
    assert suite_plan._teste_ligne(ligne, lc, {}, None, jetons) is False  # une seule source, passée par deux prises
    assert suite_plan._teste_ligne({**ligne, "trouve_par": ["annuaire_naf", "web"]}, lc, {}, None, jetons) is True


def test_niveau_ia_lu_chiffre_par_chiffre():
    from pilote import suite_plan

    assert suite_plan._niveau_ia({"Niveau": "2 — Trier"}) == 2
    assert suite_plan._niveau_ia({"Niveau": "12"}) == 1
    assert suite_plan._niveau_ia({"Niveau": "23 — rien"}) == 1


def test_gexf_deux_homonymes_restent_deux_points(tmp_path):
    import xml.etree.ElementTree as ET

    from pilote.formats import gexf

    def ligne(i, ville, relations):
        return {"id": i, "nom": "Atelier des Jardins", "ville": ville, "pays": "FR", "origine_phrase": "", "fonction": "", "decision": "garder", "site": "", "relations": relations}

    jeu = {"lignes": [ligne(1, "Villebois", [{"type": "filiale_de", "vers": "Cercle des Potagers"}]), ligne(2, "Montclair", []),
                      {**ligne(3, "Montclair", [{"type": "siege", "vers": "Atelier des Jardins"}]), "nom": "Cercle des Potagers"}],
           "trace": {"date": "2026-11-14T10:00:00", "sujet": "jardins", "recherche": "r", "nombre": 3, "filtre": "", "sources": []}}
    f = tmp_path / "r.gexf"
    gexf.ecrire(jeu, "detail", {}, f)
    ns = {"g": gexf.NS}
    racine = ET.parse(f).getroot()
    noeuds = racine.findall(".//g:node", ns)
    assert [n.get("label") for n in noeuds].count("Atelier des Jardins") >= 2  # deux fiches, deux points
    liens = {(e.get("source"), e.get("target")) for e in racine.findall(".//g:edge", ns)}
    assert ("n1", "n3") in liens  # le lien vers un nom unique s'accroche à sa fiche
    assert all(t not in ("n1", "n2") for s, t in liens if s == "n3")  # « Atelier des Jardins » désigne deux fiches : point extérieur, pas l'une au hasard


def test_classer_refuse_une_categorie_hors_liste(monkeypatch):
    from pilote import suite_ia

    reponses = iter(["Potager.", "verger fruitier inventé", "JARDIN PARTAGÉ"])
    monkeypatch.setattr(suite_ia, "appliquer", lambda *a, **k: (next(reponses), 1))
    lignes = [{"nom": "Atelier des Jardins"}, {"nom": "Cercle des Potagers"}, {"nom": "Club des Semis"}]
    operation = {"champ_sortie": "categorie_ia"}
    bilan = suite_ia.appliquer_lignes(lignes, operation, {"categories": "potager, jardin partagé"})
    assert lignes[0]["faits"]["ia"]["categorie_ia"] == "potager"
    assert "faits" not in lignes[1]  # hors liste : rien d'écrit
    assert lignes[2]["faits"]["ia"]["categorie_ia"] == "jardin partagé"
    assert bilan["ia_echecs"] == 1


# --- Points de logique de D117 repris le 15/11/2026 (D132)
def test_le_tableau_de_bord_recoit_la_table_des_etiquettes_de_prise():
    from pathlib import Path

    racine = Path(__file__).resolve().parents[1]
    assert 'ctx.avancer(jetons=' in (racine / "src/pilote/executeur_grappes.py").read_text(encoding="utf-8")
    js = (racine / "static/suite/js/tableau.js").read_text(encoding="utf-8")
    assert "sourceParId((r.avancement?.jetons || {})[pid] || pid)" in js


# --- Contre-relecture de D117 (D134) : un programme local garde SA clé, il ne reçoit pas celles des autres sources
def test_un_programme_local_garde_sa_propre_cle():
    from pathlib import Path

    from pilote.adaptateurs import programmes

    assert programmes.cles_des_autres({"CLE_A": "1", "CLE_PROGRAMME": "2"}, ["CLE_PROGRAMME"]) == ("CLE_A",)
    assert programmes.cles_des_autres({"CLE_A": "1"}, None) == ("CLE_A",)
    racine = Path(__file__).resolve().parents[1]
    assert '"cles_noms": list(d.cles)' in (racine / "src/pilote/moteur_sources.py").read_text(encoding="utf-8")
    assert "programmes.cles_des_autres(secrets, sc.get(\"cles_noms\"))" in (racine / "src/pilote/pont/executer.py").read_text(encoding="utf-8")
