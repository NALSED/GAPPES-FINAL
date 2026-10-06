"""Orchestration : ingestion de dossiers JSON, run (scoring + affectation), export."""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

from grappes.clustering.assign import AssignResult, assign
from grappes.clustering.export import export_csv
from grappes.clustering.resultat import write_resultat
from grappes.config import Config
from grappes.ingestion import RejectReport, get_fetcher
from grappes.storage.db import Database

log = logging.getLogger(__name__)


def read_json_records(folder: str | Path) -> list[dict]:
    """Lit tous les `.json` (liste ou objet) et `.jsonl` d'un dossier, dans l'ordre des noms.
    Les objets sont rendus tels quels : `Fetcher.unwrap` défait les enveloppes d'export.

    UTF-8 avec ou sans BOM. Un fichier illisible (encodage, JSON invalide) ou une ligne
    invalide devient un enregistrement `None`, compté comme rejet par le fetcher : le lot
    n'est jamais interrompu.
    """
    records: list[dict] = []
    for p in sorted(Path(folder).iterdir()):
        if p.suffix not in (".json", ".jsonl") or not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError as exc:
            log.warning("%s: encodage UTF-8 invalide (%s), fichier rejeté", p.name, exc)
            records.append(None)
            continue
        if p.suffix == ".jsonl":
            for line in text.splitlines():
                if line.strip():
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        records.append(None)
        else:
            try:
                data = json.loads(text)
            except json.JSONDecodeError as exc:
                log.warning("%s: JSON invalide (%s), fichier rejeté", p.name, exc)
                records.append(None)
                continue
            records.extend(data if isinstance(data, list) else [data])
    return records


def ingest(
    db: Database, folder: str | Path, ecosystem: str, cfg: Config
) -> tuple[int, RejectReport]:
    fetcher = get_fetcher(ecosystem).configure(cfg)
    records = [r for doc in read_json_records(folder) for r in fetcher.unwrap(doc)]
    obs, report = fetcher.parse_many(records)
    obs = fetcher.finalize(obs, db)
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
    result = assign(observations, cfg, names=db.load_display_names())
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
    return [*export_csv(result, cfg, run_id, out_dir), *write_resultat(result, cfg, out_dir)]
