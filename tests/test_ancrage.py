"""Promotion des décisions de `resultat_a_trancher.csv` en ancres (décision 901/Q28). Édition de texte,
jamais un aller-retour yaml.safe_load/dump (voir le module)."""

import csv

import pytest
import yaml

from grappes.ancrage import ajouter_ancre, ancres_existantes, promouvoir
from grappes.cli import main
from grappes.config import ConfigError


def test_ancres_existantes_inline_et_bloc():
    assert ancres_existantes("anchors: ['x:a', \"x:b\"]\n") == {"x:a", "x:b"}
    assert ancres_existantes("anchors:\n  - 'x:a'\n  - \"x:b\"\noppositions: []\n") == {"x:a", "x:b"}
    assert ancres_existantes("id: G-A\n") == set()


def test_ajouter_ancre_inline_ne_duplique_pas():
    texte = "id: G-A\nanchors: ['x:a']\noppositions: []\n"
    nouveau = ajouter_ancre(texte, "x:b")
    assert ancres_existantes(nouveau) == {"x:a", "x:b"}
    assert ajouter_ancre(nouveau, "x:a") == nouveau  # déjà présente : rien ne change


def test_ajouter_ancre_bloc_garde_le_reste_du_fichier_intact():
    texte = (
        'id: G-DEMO-A\nlabel: "Grappe de démonstration A (cuisine)"\n'
        "lexicon:\n  terms:\n    \"soupe\": 1.0\n"
        "anchors:\n  - \"x:chef_demo\"\n  - \"web:exemple-a.test\"\n"
        'oppositions:\n  - "G-DEMO-B"\n'
    )
    nouveau = ajouter_ancre(texte, "x:marie_m")
    assert ancres_existantes(nouveau) == {"x:chef_demo", "web:exemple-a.test", "x:marie_m"}
    # rien d'autre n'a bougé : label, lexicon et oppositions identiques caractère pour caractère
    for ligne in ('label: "Grappe de démonstration A (cuisine)"', '"soupe": 1.0', 'oppositions:', '"G-DEMO-B"'):
        assert ligne in nouveau
    assert yaml.safe_load(nouveau)["oppositions"] == ["G-DEMO-B"]


def test_ajouter_ancre_sans_cle_anchors_en_cree_une():
    nouveau = ajouter_ancre("id: G-A\noppositions: []\n", "x:a")
    assert ancres_existantes(nouveau) == {"x:a"}
    assert yaml.safe_load(nouveau)["id"] == "G-A"


@pytest.fixture
def depot(tmp_path):
    d = tmp_path / "cfg"
    (d / "grappes").mkdir(parents=True)
    (d / "grappes" / "a.yaml").write_text("id: G-A\nanchors: ['x:anchor1']\n", encoding="utf-8")
    (d / "grappes" / "b.yaml").write_text("id: G-B\nanchors:\n  - 'x:anchor2'\n", encoding="utf-8")
    return d


def _a_trancher(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["NOM", "GRAPPE", "REF", "DECISION"])
        for row in rows:
            w.writerow(row)
    return path


def test_promouvoir_ajoute_seulement_les_decisions_garder(depot, tmp_path):
    csv_path = _a_trancher(
        tmp_path / "resultat_a_trancher.csv",
        [
            ["Marie Martin", "G-A", "x:marie_m", "garder"],
            ["Paul Dupont", "G-B", "x:paul_d", "exclure"],
            ["Indécis", "G-A", "x:indecis", ""],
        ],
    )
    ajoutees = promouvoir(depot, csv_path)
    assert ajoutees == ["x:marie_m"]
    assert ancres_existantes((depot / "grappes" / "a.yaml").read_text(encoding="utf-8")) == {
        "x:anchor1", "x:marie_m",
    }
    assert ancres_existantes((depot / "grappes" / "b.yaml").read_text(encoding="utf-8")) == {"x:anchor2"}


def test_promouvoir_est_idempotent(depot, tmp_path):
    csv_path = _a_trancher(tmp_path / "t.csv", [["Marie Martin", "G-A", "x:marie_m", "garder"]])
    promouvoir(depot, csv_path)
    assert promouvoir(depot, csv_path) == []  # déjà ancrée : rien de plus à ajouter


def test_promouvoir_grappe_introuvable_leve_et_n_ecrit_rien(depot, tmp_path):
    csv_path = _a_trancher(tmp_path / "t.csv", [["Qui", "G-INCONNUE", "x:qui", "garder"]])
    avant = (depot / "grappes" / "a.yaml").read_text(encoding="utf-8")
    with pytest.raises(ConfigError, match="introuvable"):
        promouvoir(depot, csv_path)
    assert (depot / "grappes" / "a.yaml").read_text(encoding="utf-8") == avant


def test_cli_ancrer(depot, tmp_path, capsys):
    csv_path = _a_trancher(tmp_path / "t.csv", [["Marie Martin", "G-A", "x:marie_m", "garder"]])
    assert main(["--config", str(depot), "ancrer", "--fichier", str(csv_path)]) == 0
    assert "x:marie_m" in capsys.readouterr().out
    assert "x:marie_m" in (depot / "grappes" / "a.yaml").read_text(encoding="utf-8")


def test_cli_ancrer_fichier_absent(depot, tmp_path):
    assert main(["--config", str(depot), "ancrer", "--fichier", str(tmp_path / "absent.csv")]) == 2
