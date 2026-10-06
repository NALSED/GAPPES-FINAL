"""Revue de robustesse : entrées vides, doublons, encodages, longs textes, dates, circularité."""

import csv
import json
import time

import pytest

from conftest import CONFIG_CLAIR
from grappes.config import load_config
from grappes.ingestion import get_fetcher
from grappes.pipeline import export, ingest, run
from grappes.semantic.scoring import score_proximity
from grappes.storage.db import Database

CONFIG = CONFIG_CLAIR


def rec(i, author, text, **extra):
    return json.dumps({"id": str(i), "author": author, "text": text, **extra}, ensure_ascii=False)


@pytest.fixture
def cfg():
    return load_config(CONFIG)


def pipeline(tmp_path, cfg, files, eco="x"):
    src = tmp_path / "in"
    src.mkdir()
    for name, content in files.items():
        (src / name).write_bytes(content if isinstance(content, bytes) else content.encode())
    db = Database(tmp_path / "t.db")
    new, report = ingest(db, src, eco, cfg)
    _, result = run(db, cfg)
    export(db, cfg, tmp_path / "out")
    return new, report, result


@pytest.mark.parametrize("eco", ["x", "telegram", "web"])
@pytest.mark.parametrize(
    "raw", [{}, {"text": None}, {"text": 123}, [], "chaine", None, {"author": None, "text": "a"}]
)
def test_enregistrements_degeneres_rejetes_sans_crash(eco, raw):
    obs, report = get_fetcher(eco).parse_many([raw])
    assert obs == [] and report.n_rejected == 1


def test_dossier_vide_et_json_vide(tmp_path, cfg):
    new, _, result = pipeline(tmp_path, cfg, {})
    assert new == 0 and result.entities == []
    assert (tmp_path / "out" / "entites.csv").read_text("utf-8").count("\n") == 1  # en-tête seul


def test_json_invalide_et_encodage_invalide_comptes_comme_rejets(tmp_path, cfg):
    files = {
        "a.json": "{oups",
        "b.jsonl": rec(1, "u", "café").encode("latin-1"),
        "c.json": "42",
        "d.jsonl": rec(2, "u", "soupe"),
    }
    new, report, _ = pipeline(tmp_path, cfg, files)
    assert new == 1 and report.n_rejected == 3


def test_bom_utf8_accepte(tmp_path, cfg):
    new, report, _ = pipeline(
        tmp_path, cfg, {"a.jsonl": b"\xef\xbb\xbf" + rec(1, "u", "soupe").encode()}
    )
    assert new == 1 and report.n_rejected == 0


def test_doublons_dans_le_lot_et_entre_lots(tmp_path, cfg):
    ligne = rec(1, "u", "soupe")
    new, report, _ = pipeline(tmp_path, cfg, {"a.jsonl": ligne + "\n" + ligne})
    assert new == 1 and report.duplicates == 1
    new2, _ = ingest(Database(tmp_path / "t.db"), tmp_path / "in", "x", cfg)
    assert new2 == 0  # ré-ingestion idempotente


def test_texte_vide_nul_non_chaine(tmp_path, cfg):
    lignes = [
        rec(1, "u", "soupe\u0000x"),
        rec(2, "u", ""),
        json.dumps({"id": "3", "author": "u", "text": None}),
        json.dumps({"id": "4", "author": "u", "text": 123}),
    ]
    new, report, result = pipeline(tmp_path, cfg, {"a.jsonl": "\n".join(lignes)})
    assert new + report.n_rejected == 4 and len(result.entities) == 1


def test_tres_long_texte_rapide():
    t0 = time.perf_counter()
    score = score_proximity("soupe " * 300_000 + "x" * 1_000_000, {"soupe": 1, "café crème": 1})
    assert 0 < score <= 100 and time.perf_counter() - t0 < 5


def test_caracteres_exotiques():
    assert score_proximity("\x00soupe\ud800 \U0001f600", {"soupe": 1}) > 0
    assert score_proximity("", {"soupe": 1}) == 0


def test_dates_absentes(tmp_path, cfg):
    lignes = [rec(1, "u1", "soupe recette @u2"), rec(2, "u2", "soupe", created_at="illisible")]
    _, _, result = pipeline(tmp_path, cfg, {"a.jsonl": "\n".join(lignes)})
    assert len(result.entities) == 2
    assert all(s.first_seen is None and s.last_seen is None for s in result.stats.values())
    rows = list(
        csv.reader((tmp_path / "out" / "entites.csv").open(encoding="utf-8"), delimiter=";")
    )
    assert all(r[-3] == "" and r[-2] == "" for r in rows[1:])


def test_citations_circulaires_bornees(tmp_path, cfg):
    lignes = [
        rec(i, f"u{i % 3}", f"soupe recette @u{(i + 1) % 3}", created_at="2026-03-01T00:00:00Z")
        for i in range(9)
    ]
    _, _, result = pipeline(tmp_path, cfg, {"a.jsonl": "\n".join(lignes)})
    assert len(result.entities) == 3 and result.iterations <= cfg.scoring.max_iter


def test_csv_neutralise_les_formules(tmp_path, cfg):
    lignes = [rec(1, "=cmd", "soupe"), rec(2, "+a;b", "soupe")]
    pipeline(tmp_path, cfg, {"a.jsonl": "\n".join(lignes)})
    rows = list(
        csv.reader((tmp_path / "out" / "entites.csv").open(encoding="utf-8"), delimiter=";")
    )
    for r in rows[1:]:
        assert r[2][:1] not in "=+-@" and r[3][:1] not in "=+-@"
