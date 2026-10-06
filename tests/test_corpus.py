"""Pipeline complet sur le corpus synthétique (~2 000 observations, 3 écosystèmes)."""

import asyncio
import hashlib
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "outils"))
import corpus_synthetique

from grappes.config import load_config
from grappes.mcp.queries import Queries, open_readonly
from grappes.pipeline import export, ingest, run
from grappes.storage.db import Database

ROOT = Path(__file__).resolve().parents[1]
GA, GB = "G-DEMO-A", "G-DEMO-B"


@pytest.fixture(scope="module")
def monde(tmp_path_factory):
    out = tmp_path_factory.mktemp("corpus")
    attendu = corpus_synthetique.write(out)
    cfg = load_config(ROOT / "config")
    db = Database(out / "c.db")
    reports = {eco: ingest(db, out / eco, eco, cfg) for eco in ("x", "telegram", "web")}
    run_id, res = run(db, cfg)
    return {
        "out": out, "attendu": attendu, "cfg": cfg, "db": db, "reports": reports,
        "run_id": run_id, "res": res,
        "by_ref": {e.primary_ref: e.entity_id for e in res.entities},
    }  # fmt: skip


def membres(monde, ref):
    eid = monde["by_ref"][ref]
    return sorted(
        (m for m in monde["res"].memberships if m["entity_id"] == eid),
        key=lambda m: -m["confidence"],
    )


def test_volume_et_rejets(monde):
    rep = monde["reports"]
    assert sum(n for n, _ in rep.values()) >= 2000
    assert rep["x"][1].duplicates == 40 and rep["x"][1].n_rejected == 0
    assert rep["telegram"][1].n_rejected == 1 and rep["web"][1].n_rejected == 1


def test_valides_par_recoupement(monde):
    for ref, exp in monde["attendu"].items():
        if exp == "valide":
            top = membres(monde, ref)[0]
            assert (top["grappe_id"], top["via"], top["status"]) == (GA, "recoupement", "classé")
            assert top["confidence"] >= monde["cfg"].scoring.crossref_floor


def test_refuses_jamais_valides(monde):
    """Aucun refus n'obtient `via = recoupement` ; chaque enregistrement dit pourquoi."""
    records = {r.cited: r for r in monde["res"].validations if r.grappe_id == GA}
    for ref, exp in monde["attendu"].items():
        if exp != "refuse":
            continue
        assert all(m["via"] != "recoupement" for m in membres(monde, ref)), ref
        if ref in records:
            assert not records[ref].validated and records[ref].reasons, ref
    assert "écosystèmes 1 < 2" in " ".join(records["x:cible_mono_eco"].reasons)
    assert "citants membres 2 < 3" in " ".join(records["web:cible-peu-citee.test"].reasons)
    assert "web:cible-perimee.test" not in records  # citations hors fenêtre
    bruit = (
        " ".join(records["web:cible-bruit.test"].reasons)
        if "web:cible-bruit.test" in records
        else ""
    )
    assert "web:cible-bruit.test" not in records or "non membres" in bruit


def test_mono_ecosysteme_refuse_e_nul_non_classe(monde):
    """D19 : 5 membres de A, un seul écosystème -> refusé, E = 0, conf = S, non classé."""
    for m in membres(monde, "x:cible_mono_eco"):
        assert m["ecosystem"] == 0 and m["confidence"] == m["semantic"]
        assert m["status"] != "classé"


def test_ambigu_et_circulaire(monde):
    assert membres(monde, "x:mixte")[0]["status"] == "ambigu"
    for i in range(3):
        assert all(m["status"] != "classé" for m in membres(monde, f"x:circ{i}"))
    assert monde["res"].iterations <= monde["cfg"].scoring.max_iter


def test_rejouable_a_l_identique(monde, tmp_path):
    cfg, db = monde["cfg"], monde["db"]
    assert run(db, cfg)[0] == monde["run_id"]
    export(db, cfg, tmp_path / "a")
    export(db, cfg, tmp_path / "b")
    for nom in ("entites.csv", "appartenances.csv"):
        h = [hashlib.sha256((tmp_path / d / nom).read_bytes()).hexdigest() for d in "ab"]
        assert h[0] == h[1]


def test_top_10_sources_grappe_a(monde):
    """« Les 10 sources les plus influentes de la Grappe A » : membres solides, triés, bornés."""
    q = Queries(open_readonly(monde["out"] / "c.db"), monde["cfg"])
    top = q.top_sources(GA, limit=10)
    assert len(top) == 10
    infl = [r["influence"] for r in top]
    assert infl == sorted(infl, reverse=True)
    assert all(r["ref"] and r["confidence"] >= 40 for r in top)
    assert not any(r["ref"].startswith(("x:jardinier", "telegram:canal_jardin")) for r in top)
    assert {r["ecosystem"] for r in q.top_sources(GA, limit=100, ecosystem="web")} == {"web"}


def test_top_10_via_client_mcp_stdio(monde):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "grappes.mcp.server"],
        env={
            **os.environ,
            "GRAPPES_DB": str(monde["out"] / "c.db"),
            "GRAPPES_CONFIG": str(ROOT / "config"),
            "PYTHONPATH": str(ROOT / "src"),
        },
    )

    async def scenario():
        async with stdio_client(params) as (r, w), ClientSession(r, w) as s:
            await s.initialize()
            top = await s.call_tool("top_sources", {"grappe_id": GA, "limit": 10})
            assert not top.is_error
            rows = [json.loads(c.text) for c in top.content if c.type == "text"]
            flat = [x for r in rows for x in (r if isinstance(r, list) else [r])]
            assert len(flat) == 10 and flat[0]["influence"] >= flat[-1]["influence"]
            valides = await s.call_tool("get_validated_refs", {"grappe_id": GA, "limit": 20})
            assert not valides.is_error and "cible" in valides.content[0].text

    asyncio.run(asyncio.wait_for(scenario(), 60))
