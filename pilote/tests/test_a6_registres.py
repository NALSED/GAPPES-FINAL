"""A6 (spec 912) : les registres de première main gratuits vérifient réellement un nom, sous le contrôle A2 (nom exact ET un autre
champ). Chaque source est essayée sur son exemple de réponse archivé ; aucun réseau."""

from __future__ import annotations

import json

import pytest

from pilote import adaptateurs
from pilote.adaptateurs import api_json, gleif, recherche_entreprises, ror
from pilote.config import charger as charger_config
from pilote.pont.verification import fiabilite_effective, relever_niveaux, verifier_candidats
from pilote.sources import charger_sources

BRANCHEES = ["recherche-entreprises", "registre-associations", "companies-house", "gleif", "ror"]
EXEMPLE = {"registre-associations": "exemples/recherche-entreprises.json"}  # même service, même forme de réponse


@pytest.fixture(scope="module")
def decls():
    cfg = charger_config()
    return cfg, charger_sources(cfg)[0]


def _convertis(cfg, d):
    brut = json.loads((cfg.dossier_sources / (d.exemple_reponse or EXEMPLE[d.id])).read_text(encoding="utf-8"))
    module = str(d.moteur["adaptateur"])
    if module == "recherche_entreprises":
        return recherche_entreprises.convertir(brut)
    return {"gleif": gleif.convertir, "ror": ror.convertir}[module](brut) if module != "api_json" else api_json.convertir(brut, d.moteur["parametres"])


def _verifier(monkeypatch, d, rendus, lignes):
    class Faux:
        @staticmethod
        def chercher(entree, client, parametres):
            return [dict(r) for r in rendus]

    monkeypatch.setattr(adaptateurs, "charger", lambda nom: Faux)
    spec = {"verificateurs": [{"source": d.id, "module": str(d.moteur["adaptateur"]), "verifie_sur": d.verifie_sur, "parametres": dict(d.moteur.get("parametres") or {})}],
            "mains_sources": {d.id: d.main}, "fiabilites_sources": {d.id: "A"}}  # fmt: skip
    verifier_candidats(lignes, spec, {}, lambda: False, 60.0, lambda *a, **k: None)
    fiabilite_effective(lignes, spec)
    relever_niveaux(lignes)
    return lignes


@pytest.mark.parametrize("sid", BRANCHEES)
def test_la_source_est_declaree_pour_verifier_par_le_nom_exact(decls, sid):
    d = decls[1][sid]
    assert d.verifie_sur == "nom" and d.main == "premiere" and "verifier" in d.roles
    assert d.moteur["parametres"].get("correspondance_exacte") is True


@pytest.mark.parametrize("sid", BRANCHEES)
def test_sur_son_exemple_archive_la_source_confirme_le_bon_nom_et_lui_seul(decls, monkeypatch, sid):
    cfg, tous = decls
    d = tous[sid]
    rendus = _convertis(cfg, d)
    assert rendus, sid
    vrai = next((r for r in rendus if r.get("ville") or r.get("site")), rendus[0])
    second = {"ville": vrai["ville"]} if vrai.get("ville") else {"site": vrai["site"]} if vrai.get("site") else {"numero_officiel": vrai["numero"]}
    lignes = [
        {"nom": vrai["nom"].title(), "faits": {"niveau": "a_verifier"}, **second},  # même nom (casse à part), second champ concordant
        {"nom": vrai["nom"], "ville": "Villeailleurs", "site": "ailleurs.example", "numero_officiel": "X-0", "faits": {"niveau": "a_verifier"}},  # homonyme
        {"nom": "Nom Sans Rapport Avec L'Exemple", "faits": {"niveau": "a_verifier"}, **second},  # autre nom, même ville : rien
    ]
    _verifier(monkeypatch, d, rendus, lignes)
    v0 = lignes[0]["faits"]["verifications"][0]
    assert v0["signal"] == "confirmation" and lignes[0]["faits"]["fiabilite_effective"] == "A" and lignes[0]["faits"]["niveau"] == "sur"
    v1 = lignes[1]["faits"]["verifications"][0]
    assert v1["signal"] == "meme_nom" and "fiabilite_effective" not in lignes[1]["faits"] and lignes[1]["faits"]["niveau"] == "a_verifier"
    assert not lignes[2]["faits"].get("verifications")  # une réponse approchante n'est jamais prise pour une confirmation


def test_les_sources_payantes_ne_sont_pas_branchees_sans_test_reel(decls):
    for sid in ("pappers", "opencorporates"):
        assert decls[1][sid].verifie_sur == ""


def test_eteintes_par_defaut_elles_verifient_des_qu_on_les_choisit(decls):
    from pilote.moteur_sources import verificatrices

    cfg = decls[0]
    assert not ({d.id for d in verificatrices(cfg, {})} & set(BRANCHEES))  # aucune recherche ne change sans un choix de la personne
    gratuites = ["recherche-entreprises", "registre-associations", "gleif", "ror"]  # companies-house demande sa clé
    assert [d.id for d in verificatrices(cfg, {"verificatrices": gratuites})] == gratuites  # posées sur le plan : elles vérifient
