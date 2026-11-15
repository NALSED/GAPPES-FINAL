"""Commandes de la mission autocalibration : `python -m grappes.autocal.cli <commande>`.

* `collecter [--jeu dev|validation|test|tous] [--sujet ID]` : collectes RÉELLES manquantes (consomment du quota
  Tavily : une requête = un crédit), une par sujet, jamais refaites si une cassette existe.
* `credits` : crédits Tavily consommés / plafond (point d'API gratuit).
* `reference-officielle --sujet ID --phrase "…" --liste FICHIER.csv` : écrit la référence et la fiche d'un sujet à
  partir d'une liste officielle publiée (B1, spec 912). Aucun appel réseau, aucun crédit. Jeu : `officiel`.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

from grappes.autocal.collecte import RACINE, collecter, dossier, preparer
from grappes.autocal.sujets import Sujet

DEFS = Path("autocal")


def charger_sujets(jeu: str = "tous") -> list[Sujet]:
    out = []
    for f in sorted((DEFS / "sujets").glob("*.json")):
        s = Sujet(**json.loads(f.read_text(encoding="utf-8")))
        # « tous » = les trois jeux historiques ; le jeu « officiel » (B1) ne se collecte que sur demande explicite
        if jeu == s.jeu or (jeu == "tous" and s.jeu != "officiel"):
            out.append(s)
    return out


def credits() -> tuple[int, int]:
    from grappes.env import load_secrets

    load_secrets("config/secrets.env")
    import os

    req = urllib.request.Request(
        "https://api.tavily.com/usage",
        headers={"Authorization": f"Bearer {os.environ['TAVILY_API_KEY']}"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)["account"]
    return d["plan_usage"], d["plan_limit"]


def cmd_collecter(args) -> int:
    todo = [s for s in charger_sujets(args.jeu) if not args.sujet or s.id == args.sujet]
    for s in todo:
        d = dossier(s.id, RACINE)
        if (d / "collecte.txt").exists() and not args.refaire:
            print(f"{s.id} : déjà collecté ({(d / 'collecte.txt').read_text().strip()})")
            continue
        used, cap = credits()
        if cap - used < 20:
            print(
                f"crédits Tavily insuffisants ({used}/{cap}) : arrêt avant {s.id}", file=sys.stderr
            )
            return 3
        preparer(s.id, s.phrase)
        out = collecter(s.id)
        used2, _ = credits()
        print(
            f"{s.id} : {out.status}, {used2 - used} crédit(s) consommé(s) ({used2}/{cap})",
            flush=True,
        )
    return 0


def cmd_reference_officielle(args) -> int:
    from grappes.autocal.reference import build_from_list

    ref = build_from_list(args.sujet, args.phrase, args.liste)
    if not ref.entities:
        print(f"{args.liste} : aucune entité lisible", file=sys.stderr)
        return 2
    for d in ("references", "sujets"):
        (DEFS / d).mkdir(parents=True, exist_ok=True)
    ref.save(DEFS / "references" / f"{args.sujet}.json")
    Sujet(
        id=args.sujet,
        phrase=args.phrase,
        jeu="officiel",
        origine="liste_officielle",
        r=ref.r,
        where=ref.where,
    ).save(DEFS / "sujets" / f"{args.sujet}.json")
    print(f"{args.sujet} : {ref.r} acteurs attendus ({ref.where})")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="autocal")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("collecter")
    c.add_argument(
        "--jeu", default="tous", choices=["dev", "validation", "test", "officiel", "tous"]
    )
    c.add_argument("--sujet")
    c.add_argument("--refaire", action="store_true")
    sub.add_parser("credits")
    r = sub.add_parser("reference-officielle")
    r.add_argument("--sujet", required=True)
    r.add_argument("--phrase", required=True)
    r.add_argument("--liste", required=True)
    args = p.parse_args(argv)
    if args.cmd == "credits":
        print("%d/%d" % credits())
        return 0
    if args.cmd == "reference-officielle":
        return cmd_reference_officielle(args)
    return cmd_collecter(args)


if __name__ == "__main__":
    sys.exit(main())
