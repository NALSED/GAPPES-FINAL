"""Entités nommées d'un sujet (chantier 2, D63) : extraction depuis les textes archivés, fusion avec les candidats.

Les textes viennent de la base du rejeu (aucun réseau) ; l'extraction est archivée par (modèle, texte) : le modèle ne
tourne qu'une fois par texte. Une organisation nommée devient un candidat `ner:<nom normalisé>`, citée par les
sources qui l'ont nommée (arêtes source -> entité pour la découverte de vérité). Si son nom normalisé est celui d'un
candidat déjà connu (web ou registre), elle l'enrichit au lieu d'en créer un second.
"""

from __future__ import annotations

from pathlib import Path

from grappes.autocal.juger import norm_name
from grappes.autocal.pool import Candidat, Contexte
from grappes.ner.extraire import NerConfig, Nomme, charger_config, extraire

CACHE = Path("donnees/autocal/ner")


def nommes_du_sujet(ctx: Contexte, cfg: NerConfig | None = None) -> dict[str, Nomme]:
    cfg = cfg or charger_config()
    pages = [(o.obs_id, o.source.key, o.text) for o in ctx.db.load_observations()]
    return extraire(pages, cfg, CACHE)


def ajouter(
    ctx: Contexte, cands: list[Candidat], nommes: dict[str, Nomme]
) -> tuple[list[Candidat], list[tuple[str, str]]]:
    """(candidats avec les entités nommées, citations source -> entité nommée)."""
    cands = list(cands)
    par_nom = {norm_name(c.nom): c for c in cands if c.nom}
    cits: list[tuple[str, str]] = []
    obs_source = {o.obs_id: o.source.key for o in ctx.db.load_observations()}
    for cle, n in sorted(nommes.items()):
        c = par_nom.get(norm_name(n.nom))
        if c is None:
            c = Candidat(
                f"ner:{cle}", n.nom, n.nom, 0.0, "nomme", 0.0, 0.0, 0.0,
                facteur=ctx.rel.factor(f"ner:{cle}"), citants=set(), ecosystemes=set(),
            )  # fmt: skip
            cands.append(c)
            par_nom[norm_name(n.nom)] = c
        for site, conf in n.score_par_site.items():
            c.ner_sites[site] = max(c.ner_sites.get(site, 0.0), conf)
        for oid in sorted(n.pages):
            if oid in obs_source:
                cits.append((obs_source[oid], c.ref))
    return sorted(cands, key=lambda c: c.ref), sorted(set(cits))
