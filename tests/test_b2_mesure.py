"""B2 (spec 912, audit 910 § 3.3, § 3.4, § 4) : l'outil de mesure compare à base égale."""

from __future__ import annotations

import re
from pathlib import Path

from grappes.autocal import evaluation as ev
from grappes.autocal.juger import FAUX, JUSTE, NON_VERIFIABLE
from grappes.autocal.reference import RefEntity, Reference

REF = Reference(
    "s", "p", "w", [RefEntity("Q1", "Alpha"), RefEntity("Q2", "Beta"), RefEntity("Q3", "Gamma")]
)


def _j(docid: str, verdict: str, score: float) -> ev.Jugement:
    return ev.Jugement(ev.Classe("web:" + docid, docid, score), verdict, docid, "")


def test_le_nombre_d_attendus_est_celui_de_la_reference_quelle_que_soit_la_configuration():
    a = [_j("Q1", JUSTE, 0.9), _j("Q999", JUSTE, 0.8), _j("x:1", NON_VERIFIABLE, 0.7)]
    b = [_j("Q1", JUSTE, 0.9), _j("Q7", FAUX, 0.5)]
    ma, mb = ev.mesurer(REF, a), ev.mesurer(REF, b)
    assert ma["R"] == mb["R"] == 3
    # un « juste » hors de la référence ne gonfle ni les attendus ni la note
    assert ev.qrels_de(REF, a)["s"].get("Q999") is None
    assert ma["mesures"]["Rprec"] == mb["mesures"]["Rprec"]


def test_la_part_d_attendus_trouves_est_donnee():
    m = ev.mesurer(
        REF, [_j("Q1", JUSTE, 0.9), _j("Q1", JUSTE, 0.4), _j("Q2", JUSTE, 0.3), _j("Q7", FAUX, 0.2)]
    )
    assert m["attendus_trouves"] == 2
    assert abs(m["part_attendus_trouves"] - 2 / 3) < 1e-9
    assert ev.mesurer(REF, [])["part_attendus_trouves"] == 0.0


def test_les_en_tetes_n_annoncent_plus_une_validation_imbriquee_absente():
    base = Path(ev.__file__).parent
    for nom in ("optimiser.py", "protocole.py"):
        entete = (base / nom).read_text(encoding="utf-8").split('"""')[1]
        assert not re.search(r"validation imbriquée (et|,)", entete), nom
