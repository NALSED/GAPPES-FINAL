"""Découverte par registres pour un sujet (chantier 1, D63) et fusion avec les candidats du web.

La phrase est traduite en requêtes de registre SANS lire la référence d'évaluation ; les résultats sont archivés
(`donnees/autocal/decouverte/<sujet>.json`) : un rejeu ne retourne jamais au réseau.

Fusion : une entité de registre dont le site officiel est le domaine d'un candidat du web enrichit ce candidat
(commune, registre) au lieu d'en créer un second ; deux registres qui nomment le même acteur (même SIREN, sinon même
nom normalisé) ne comptent qu'une fois. Les variantes de nom restantes (« Fenix Toulouse » / « Fenix Toulouse
Handball ») sont SIGNALÉES, jamais fusionnées d'office.
"""

from __future__ import annotations

import copy
import json
from dataclasses import asdict
from pathlib import Path

from grappes.autocal.juger import norm_name
from grappes.autocal.pool import Candidat, Contexte
from grappes.canon import canonical_domain, site_key
from grappes.decouverte.client import Http
from grappes.decouverte.registres import Decouvert, DecouverteConfig, decouvrir

DOSSIER = Path("donnees/autocal/decouverte")
CACHE_HTTP = Path("donnees/autocal/decouverte_cache")


def decouverts(sujet_id: str, phrase: str, cfg: DecouverteConfig | None = None, refaire: bool = False) -> list[Decouvert]:
    cfg = cfg or DecouverteConfig()
    f = DOSSIER / f"{sujet_id}.json"
    if f.exists() and not refaire:
        return [Decouvert(**d) for d in json.loads(f.read_text(encoding="utf-8"))]
    out = decouvrir(phrase, Http(CACHE_HTTP, delai_s=1.0), cfg)
    DOSSIER.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps([asdict(d) for d in out], ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def _groupes(ds: list[Decouvert]) -> list[dict]:
    """Un groupe par acteur : même SIREN, sinon même nom normalisé."""
    groupes: list[dict] = []
    par_siren: dict[str, dict] = {}
    par_nom: dict[str, dict] = {}
    for d in sorted(ds, key=lambda x: (x.registre != "wikidata", x.registre, x.identifiant)):
        g = (par_siren.get(d.siren) if d.siren else None) or par_nom.get(norm_name(d.nom))
        if g is None:
            g = {"nom": d.nom, "registres": set(), "ids": {}, "ville": "", "domaine": "", "siren": ""}
            groupes.append(g)
        g["registres"].add(d.registre)
        g["ids"].setdefault(d.registre, d.identifiant)
        g["ville"] = g["ville"] or d.ville
        g["domaine"] = g["domaine"] or d.domaine
        g["siren"] = g["siren"] or d.siren
        if d.siren:
            par_siren[d.siren] = g
        par_nom[norm_name(d.nom)] = g
    return groupes


def fusionner(ctx: Contexte, ds: list[Decouvert], sources: tuple[str, ...]) -> list[Candidat]:
    """Candidats du web (copies enrichies) + acteurs de registre sans équivalent web."""
    cands = [copy.copy(c) for c in ctx.candidats]
    par_site = {site_key(canonical_domain(c.ref.partition(":")[2])): c for c in cands if c.ref.startswith(("web:", "rss:"))}
    par_nom = {norm_name(c.nom): c for c in cands if c.nom}
    facteur = ctx.rel.table.factors["A"]
    for g in _groupes([d for d in ds if d.registre in sources]):
        site = site_key(canonical_domain(g["domaine"])) if g["domaine"] else ""
        c = par_site.get(site) if site else None
        c = c or par_nom.get(norm_name(g["nom"]))
        if c is not None:
            c.registres = c.registres | g["registres"]
            c.ville = c.ville or g["ville"]
            continue
        reg = "wikidata" if "wikidata" in g["registres"] else sorted(g["registres"])[0]
        ref = f"reg:{reg}:{g['ids'][reg]}" + (f"|{g['siren']}" if g["siren"] else "")
        cands.append(
            Candidat(ref, g["nom"], g["nom"], 0.0, "registre", 0.0, 0.0, 0.0, facteur=facteur,
                     registres=set(g["registres"]), ville=g["ville"])
        )  # fmt: skip
    return sorted(cands, key=lambda c: c.ref)


def variantes(cands: list[Candidat]) -> list[tuple[str, str]]:
    """Paires de noms dont l'un est un préfixe de mots de l'autre (doublons probables), à signaler."""
    noms = sorted({norm_name(c.nom) for c in cands if c.nom and c.registres}, key=len)
    out = []
    for i, a in enumerate(noms):
        for b in noms[i + 1 :]:
            if b != a and b.startswith(a + " ") and len(a.split()) >= 2:
                out.append((a, b))
    return out
