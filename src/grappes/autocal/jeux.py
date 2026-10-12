"""Chargement des jeux de sujets : rejeu de la collecte (une seule fois, sans réseau), référence, juge.

`donnees/autocal/rejeux/<sujet>/` garde le rejeu de référence (paramètres de collecte par défaut). Les essais
d'optimisation ne refont que le classement et la mesure, sur ces données archivées.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from grappes.autocal.collecte import RACINE, rejouer_collecte
from grappes.autocal.juger import Juge
from grappes.autocal.pool import Contexte, charger
from grappes.autocal.reference import Reference
from grappes.autocal.sujets import Sujet
from grappes.autocal.wikidata import Wikidata

DEFS = Path("autocal")
REJEUX = Path("donnees/autocal/rejeux")
JUGES = Path("donnees/autocal/juges")
WIKIDATA = Path("donnees/autocal/wikidata")


@dataclass(slots=True)
class DonneesSujet:
    sujet: Sujet
    ctx: Contexte
    ref: Reference | None  # None pour un témoin (aucun acteur réel)
    juge: Juge | None

    @property
    def id(self) -> str:
        return self.sujet.id


def sujets_du_jeu(jeu: str) -> list[Sujet]:
    ids = json.loads((DEFS / "jeux.json").read_text(encoding="utf-8"))["jeux"][jeu]
    return [
        Sujet(**json.loads((DEFS / "sujets" / f"{i}.json").read_text(encoding="utf-8")))
        for i in ids
    ]


def rejeu(sid: str, refaire: bool = False) -> Path:
    cible = REJEUX / sid
    if refaire or not (cible / "grappes.db").exists():
        out, rep = rejouer_collecte(sid, cible, racine=RACINE)
        if rep.misses:
            raise RuntimeError(f"{sid} : {len(rep.misses)} requête(s) hors cassette au rejeu")
        if out.status != "ok":
            raise RuntimeError(f"{sid} : rejeu {out.status} {out.extra}")
    return cible


def charger_sujet(s: Sujet, w: Wikidata | None = None, juger: bool = True) -> DonneesSujet:
    cible = rejeu(s.id)
    ctx = charger(cible)
    ref, juge = None, None
    if s.origine != "controle_negatif":
        ref = Reference.load(DEFS / "references" / f"{s.id}.json")
        if juger:
            juge = Juge(ref, w or Wikidata(WIKIDATA), JUGES / f"{s.id}.json")
    return DonneesSujet(s, ctx, ref, juge)
