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
