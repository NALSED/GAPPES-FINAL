"""CLI minimale : ingest, run, export."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from grappes.config import ConfigError, load_config
from grappes.pipeline import export, ingest, run
from grappes.storage.db import Database


def _explain(db: Database, cfg, entity_id: str, grappe_id: str | None) -> int:
    from grappes.mcp.queries import Queries

    q = Queries(db.conn, cfg)
    try:
        fiche = q.get_entity(entity_id)
        if grappe_id is None:
            if not fiche["memberships"]:
                print(f"{entity_id} : aucune appartenance (non classé)")
                return 0
            grappe_id = fiche["memberships"][0]["grappe_id"]
        out = {"entite": fiche, "explication": q.explain_assignment(entity_id, grappe_id)}
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    return 0


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
    x = sub.add_parser("explain")
    x.add_argument("entity_id")
    x.add_argument("--grappe", help="grappe à expliquer (défaut : grappe principale)")
    pg = sub.add_parser("purge")
    pg.add_argument("--older-than", type=int, required=True, metavar="JOURS")
    sub.add_parser("mcp")
    args = p.parse_args(argv)
    try:
        cfg = load_config(args.config)
    except ConfigError as exc:
        print(f"configuration invalide : {exc}", file=sys.stderr)
        return 2
    if args.cmd == "mcp":
        from grappes.mcp.server import create_server

        try:
            create_server(args.db, args.config).run()
        except FileNotFoundError as exc:
            print(exc, file=sys.stderr)
            return 2
        return 0
    db = Database(args.db)
    try:
        if args.cmd == "ingest":
            if not Path(args.folder).is_dir():
                print(f"dossier introuvable : {args.folder}", file=sys.stderr)
                return 2
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
        elif args.cmd == "purge":
            print(f"{db.purge_older_than(args.older_than)} observations supprimées")
        elif args.cmd == "explain":
            return _explain(db, cfg, args.entity_id, args.grappe)
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
