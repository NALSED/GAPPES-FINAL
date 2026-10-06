"""Orchestration : ingestion de dossiers JSON, run (scoring + affectation), export."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from grappes.clustering.assign import AssignResult, assign
from grappes.clustering.export import export_csv
from grappes.config import Config
from grappes.ingestion import RejectReport, get_fetcher
from grappes.storage.db import Database


def read_json_records(folder: str | Path) -> list[dict]:
    """Lit tous les `.json` (liste ou objet) et `.jsonl` d'un dossier, dans l'ordre des noms."""
    records: list[dict] = []
    for p in sorted(Path(folder).iterdir()):
        if p.suffix == ".jsonl":
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        records.append(None)  # compté comme rejet par le fetcher
        elif p.suffix == ".json":
            data = json.loads(p.read_text(encoding="utf-8"))
            records.extend(data if isinstance(data, list) else [data])
    return records


def ingest(
    db: Database, folder: str | Path, ecosystem: str, cfg: Config
) -> tuple[int, RejectReport]:
    fetcher = get_fetcher(ecosystem)
    obs, report = fetcher.parse_many(read_json_records(folder))
    weights = {o.source.key: cfg.sources.weight(o.source.key) for o in obs}
    new = db.add_observations(obs, weights)
    return new, report


def make_run_id(obs_ids: list[str], config_hash: str) -> str:
    h = hashlib.sha256(config_hash.encode())
    for i in sorted(obs_ids):
        h.update(i.encode())
    return "R-" + h.hexdigest()[:12]


def run(db: Database, cfg: Config) -> tuple[str, AssignResult]:
    """Rejouable : même entrée + même configuration = même run_id, mêmes résultats."""
    observations = db.load_observations()
    result = assign(observations, cfg)
    run_id = make_run_id([o.obs_id for o in observations], cfg.config_hash)
    db.save_run(
        run_id,
        cfg.config_hash,
        result.entities,
        result.memberships,
        result.citations,
        result.validations,
    )
    return run_id, result


def export(db: Database, cfg: Config, out_dir: str | Path) -> list[Path]:
    run_id, result = run(db, cfg)
    return export_csv(result, cfg, run_id, out_dir)
