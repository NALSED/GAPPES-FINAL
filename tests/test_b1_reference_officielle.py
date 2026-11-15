"""B1 (spec 912) : référence construite depuis une liste officielle publiée, sans Wikidata."""

from __future__ import annotations

import pytest

from grappes.autocal.juger import JUSTE, NON_VERIFIABLE, Juge
from grappes.autocal.reference import Reference, build_from_list

LISTE = """\
# source: https://exemple.invalid/annuaire-des-clubs-de-cerf-volant
# releve: 2026-11-15
nom;alias;site;siren
Club des Vents du Nord;CVN|Vents du Nord;https://www.vents-du-nord.example/accueil;123 456 789
Cerfs-Volants de la Baie;;;
Cerfs-volants de la baie;;;
;;https://sans-nom.example;
"""


class WikidataInterdit:
    """Tout appel à Wikidata fait échouer le test : la référence officielle doit en être indépendante."""

    def __getattr__(self, name):
        raise AssertionError(f"appel Wikidata interdit : {name}")


@pytest.fixture
def ref(tmp_path):
    p = tmp_path / "clubs-cerf-volant.csv"
    p.write_text(LISTE, encoding="utf-8")
    return build_from_list("off-clubs-cerf-volant", "clubs de cerf-volant", p)


def test_la_liste_donne_une_reference_au_format_existant(ref, tmp_path):
    assert ref.r == 2  # ligne sans nom ignorée, doublon de casse réuni
    assert ref.origine == "liste_officielle"
    assert ref.classes == []
    assert "exemple.invalid" in ref.where and "2026-11-15" in ref.where
    e = ref.entities[0] if ref.entities[0].label.startswith("Club") else ref.entities[1]
    assert e.aliases == ["CVN", "Vents du Nord"]
    assert e.domains == ["vents-du-nord.example"]
    assert e.siren == ["123456789"]
    assert all(x.qid.startswith("off:") for x in ref.entities)
    ref.save(tmp_path / "r.json")
    assert Reference.load(tmp_path / "r.json") == ref
    ref.write_qrels(tmp_path / "r.qrels")
    assert (tmp_path / "r.qrels").read_text().count(" 1\n") == 2


def test_les_identifiants_ne_dependent_pas_de_l_ordre_des_lignes(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text(
        "# source: x\n# releve: 2026-11-15\nnom\nAlpha Voile\nBeta Voile\n", encoding="utf-8"
    )
    b.write_text(
        "# source: x\n# releve: 2026-11-15\nnom\nBeta Voile\nAlpha Voile\n", encoding="utf-8"
    )
    ra, rb = build_from_list("s", "p", a), build_from_list("s", "p", b)
    assert ra.entities == rb.entities


def test_une_liste_sans_source_ou_sans_date_est_refusee(tmp_path):
    p = tmp_path / "l.csv"
    p.write_text("nom\nAlpha Voile\n", encoding="utf-8")
    with pytest.raises(ValueError, match="source"):
        build_from_list("s", "p", p)


def test_une_ancienne_reference_sans_origine_se_charge_encore(tmp_path):
    p = tmp_path / "vieux.json"
    p.write_text(
        '{"sujet_id":"s","phrase":"p","where":"w","entities":[],"classes":["Q1"]}', encoding="utf-8"
    )
    assert Reference.load(p).origine == "wikidata"


def test_le_juge_ne_consulte_jamais_wikidata_avec_une_liste_officielle(ref, tmp_path):
    j = Juge(ref, WikidataInterdit(), tmp_path / "juge.json")
    assert j.juger("club des vents du nord", "web:autre.example").verdict == JUSTE
    assert j.juger("Peu importe", "web:www.vents-du-nord.example").verdict == JUSTE
    assert j.juger("X", "reg:sirene:12345678900012|123456789").verdict == JUSTE
    v = j.juger("Association inconnue", "web:inconnu.example")
    assert v.verdict == NON_VERIFIABLE and "liste officielle" in v.raison


def test_la_commande_ecrit_reference_et_fiche_sans_reseau(tmp_path, monkeypatch):
    from grappes.autocal import cli

    p = tmp_path / "l.csv"
    p.write_text(LISTE, encoding="utf-8")
    monkeypatch.setattr(cli, "DEFS", tmp_path / "autocal")
    assert (
        cli.main(
            [
                "reference-officielle",
                "--sujet",
                "off-x",
                "--phrase",
                "clubs de cerf-volant",
                "--liste",
                str(p),
            ]
        )
        == 0
    )
    assert Reference.load(tmp_path / "autocal/references/off-x.json").r == 2
    s = [x for x in cli.charger_sujets("officiel")]
    assert [x.id for x in s] == ["off-x"] and s[0].r == 2 and s[0].origine == "liste_officielle"
    assert cli.charger_sujets("tous") == []  # jamais collecté sans demande explicite (crédits)
