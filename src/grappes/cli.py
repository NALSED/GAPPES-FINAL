"""CLI minimale : ingest, run, export."""

from __future__ import annotations

import argparse
import sys

from grappes.config import ConfigError, load_config
from grappes.pipeline import export, ingest, run
from grappes.storage.db import Database


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="grappes")
    p.add_argument("--db", default="donnees/grappes.db")
    p.add_argument("--config", default="config")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("ingest")
    s.add_argument("folder")
    s.add_argument("--ecosystem", required=True, choices=["x", "telegram", "web"])
    sub.add_parser("run")
    e = sub.add_parser("export")
    e.add_argument("--out", default="sorties")
    args = p.parse_args(argv)
    try:
        cfg = load_config(args.config)
    except ConfigError as exc:
        print(f"configuration invalide : {exc}", file=sys.stderr)
        return 2
    db = Database(args.db)
    try:
        if args.cmd == "ingest":
            new, rep = ingest(db, args.folder, args.ecosystem, cfg)
            print(
                f"{new} nouvelles observations, {rep.duplicates} doublons, {rep.n_rejected} rejets"
            )
        elif args.cmd == "run":
            run_id, res = run(db, cfg)
            print(f"{run_id} : {len(res.entities)} entités, {len(res.memberships)} appartenances")
        elif args.cmd == "export":
            for path in export(db, cfg, args.out):
                print(path)
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
