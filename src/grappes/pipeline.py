"""Orchestration : ingestion de dossiers JSON, run (scoring + affectation), export."""

from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Iterator
from itertools import islice
from pathlib import Path
from typing import Any

from grappes.clustering.assign import AssignResult, assign
from grappes.clustering.export import export_csv
from grappes.clustering.resultat import write_resultat
from grappes.config import Config
from grappes.fiabilite import Reliability
from grappes.ingestion import RejectReport, get_fetcher
from grappes.storage.db import Database

log = logging.getLogger(__name__)


BATCH = 5000  # enregistrements traités (puis écrits) à la fois : mémoire bornée
MAX_LINE = 10 * 1024 * 1024  # une ligne .jsonl plus longue est rejetée sans être chargée en entier


def iter_json_records(folder: str | Path, max_file_mb: int | None = 200) -> Iterator[Any]:
    """Enregistrements des `.json` (liste ou objet) et `.jsonl` d'un dossier, dans l'ordre des noms.

    Les objets sont rendus tels quels : `Fetcher.unwrap` défait les enveloppes d'export. UTF-8 avec
    ou sans BOM. Un `.jsonl` est lu ligne à ligne (taille de fichier illimitée) ; un `.json`, qui
    doit être chargé en entier, est refusé au-delà de `max_file_mb`. Tout fichier, ligne ou
    encodage invalide devient un enregistrement `None`, compté comme rejet : le lot n'est jamais
    interrompu.
    """
    for p in sorted(Path(folder).iterdir()):
        if p.suffix not in (".json", ".jsonl") or not p.is_file():
            continue
        if p.suffix == ".jsonl":
            yield from _iter_jsonl(p)
        else:
            yield from _read_json(p, max_file_mb)


def _iter_jsonl(path: Path) -> Iterator[Any]:
    first = True
    with path.open("rb") as f:
        while True:
            raw = f.readline(MAX_LINE + 1)
            if not raw:
                return
            if len(raw) > MAX_LINE and not raw.endswith(b"\n"):
                log.warning("%s: ligne de plus de %d octets rejetée", path.name, MAX_LINE)
                while (rest := f.readline(MAX_LINE)) and not rest.endswith(b"\n"):
                    pass  # on saute le reste de la ligne sans la garder en mémoire
                yield None
                first = False
                continue
            try:
                line = raw.decode("utf-8-sig" if first else "utf-8")
            except UnicodeDecodeError:
                first = False
                yield None  # encodage invalide : cette ligne seulement
                continue
            first = False
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    yield None


def _read_json(path: Path, max_file_mb: int | None) -> Iterator[Any]:
    if max_file_mb is not None and path.stat().st_size > max_file_mb * 1024 * 1024:
        log.warning("%s: plus de %d Mo, fichier rejeté (utiliser .jsonl)", path.name, max_file_mb)
        yield None
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except UnicodeDecodeError as exc:
        log.warning("%s: encodage UTF-8 invalide (%s), fichier rejeté", path.name, exc)
        yield None
        return
    except (json.JSONDecodeError, RecursionError) as exc:
        log.warning("%s: JSON invalide (%s), fichier rejeté", path.name, type(exc).__name__)
        yield None
        return
    yield from (data if isinstance(data, list) else [data])


def read_json_records(folder: str | Path) -> list[Any]:
    """Version liste de `iter_json_records` (petits dossiers, tests)."""
    return list(iter_json_records(folder))


def ingest(
    db: Database, folder: str | Path, ecosystem: str, cfg: Config, batch: int = BATCH
) -> tuple[int, RejectReport]:
    """Lit, normalise et stocke un dossier, par lots : mémoire bornée quelle que soit la taille."""
    fetcher = get_fetcher(ecosystem).configure(cfg)
    report, seen, new, offset = RejectReport(), set(), 0, 0
    records = iter_json_records(folder, cfg.scoring.max_fichier_mo)
    while chunk := list(islice(records, batch)):
        raws = [r for doc in chunk for r in fetcher.unwrap(doc)]
        obs, rep = fetcher.parse_many(raws, seen=seen, offset=offset)
        obs = fetcher.finalize(obs, db)
        weights = {o.source.key: cfg.sources.weight(o.source.key) for o in obs}
        new += db.add_observations(obs, weights, letter=reliability_for(db, cfg).letter)
        report.absorb(rep)
        offset += len(raws)
    return new, report


def make_run_id(obs_ids: list[str], config_hash: str) -> str:
    h = hashlib.sha256(config_hash.encode())
    for i in sorted(obs_ids):
        h.update(i.encode())
    return "R-" + h.hexdigest()[:12]


def reliability_for(db: Database, cfg: Config) -> Reliability:
    """Fiabilité à l'exécution : table Admiralty (+ registres officiels et Tranco quand ils sont en cache)."""
    return Reliability(cfg.fiabilite)


def run(db: Database, cfg: Config) -> tuple[str, AssignResult]:
    """Rejouable : même entrée + même configuration (+ mêmes registres et classement) = même run_id."""
    observations = db.load_observations()
    rel = reliability_for(db, cfg)
    result = assign(observations, cfg, names=db.load_display_names(), reliability=rel)
    run_id = make_run_id([o.obs_id for o in observations], cfg.config_hash + rel.fingerprint)
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
