"""Pages qui se recopient (spec 914, volet B) : deux sites dont le passage autour d'un nom est quasi identique comptent pour UN endroit.

Méthode standard de repérage des quasi-doublons (Broder, 1997, « On the resemblance and containment of documents ») : le passage est
découpé en suites de 5 mots (« bardeaux »), et deux passages se ressemblent selon la part de suites communes (similarité de Jaccard).
Le calcul est exact (pas d'estimation par MinHash) : on ne compare, pour un nom, que les quelques sites qui le citent, l'estimation
n'apporterait que de l'imprécision.

On ne compare jamais une page entière : deux sites faits avec le même modèle (menus, pied de page) se ressembleraient à tort. On prend
le passage autour du nom (40 mots avant, 40 après, à chaque endroit où il apparaît dans la page). Un passage de moins de 30 mots n'est
pas jugé. Deux passages sont des copies à partir de 80 % de suites communes (spec 914, choix 4). Le regroupement est transitif (A copie
B, B copie C : un seul endroit). Un registre n'est jamais regroupé : il n'a pas de texte ici."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from typing import Any

from grappes.canon import site_key

FENETRE = 40  # mots gardés de part et d'autre du nom
TAILLE = 5  # longueur des suites de mots comparées
MIN_MOTS = 30  # en dessous, le passage n'est pas jugé
SEUIL = 0.8  # part de suites communes à partir de laquelle deux passages sont des copies (choix 4 de la spec 914)


def mots(texte: str) -> list[str]:
    """Les mots d'un texte, sans casse ni accents."""
    t = "".join(c for c in unicodedata.normalize("NFKD", texte.casefold()) if not unicodedata.combining(c))
    return re.findall(r"\w+", t)


def passages(tokens: list[str], nom: list[str]) -> list[str]:
    """Le passage autour du nom dans une page : les fenêtres de chaque occurrence, réunies quand elles se chevauchent. Vide si le nom
    n'y est pas."""
    n = len(nom)
    if not n:
        return []
    debuts = [i for i in range(len(tokens) - n + 1) if tokens[i] == nom[0] and tokens[i : i + n] == nom]
    if not debuts:
        return []
    garde = sorted({j for i in debuts for j in range(max(0, i - FENETRE), min(len(tokens), i + n + FENETRE))})
    return [tokens[j] for j in garde]


def empreinte(p: list[str]) -> frozenset[tuple[str, ...]]:
    """Les suites de 5 mots du passage ; vide s'il est trop court pour être jugé."""
    if len(p) < MIN_MOTS:
        return frozenset()
    return frozenset(tuple(p[i : i + TAILLE]) for i in range(len(p) - TAILLE + 1))


def jaccard(a: frozenset, b: frozenset) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def groupes(empreintes: dict[str, list[frozenset]]) -> dict[str, str]:
    """site -> représentant de son groupe de copies (le plus petit nom du groupe), pour les seuls sites recopiés ou qui recopient.
    Deux sites sont reliés si une page de l'un et une page de l'autre ont des passages à SEUIL ou plus."""
    sites = sorted(s for s, es in empreintes.items() if any(es))
    parent = {s: s for s in sites}

    def racine(s: str) -> str:
        while parent[s] != s:
            parent[s] = parent[parent[s]]
            s = parent[s]
        return s

    for i, a in enumerate(sites):
        for b in sites[i + 1 :]:
            if racine(a) != racine(b) and any(jaccard(x, y) >= SEUIL for x in empreintes[a] for y in empreintes[b]):
                ra, rb = racine(a), racine(b)
                parent[max(ra, rb)] = min(ra, rb)
    out: dict[str, list[str]] = {}
    for s in sites:
        out.setdefault(racine(s), []).append(s)
    return {s: min(membres) for membres in out.values() if len(membres) > 1 for s in membres}


def site_de_source(cle: str) -> str:
    """L'éditeur d'une source, comme ailleurs (`citants_par_cite`, extraction des noms) : le site pour une page ou un flux, sinon la clé."""
    eco, _, ident = cle.partition(":")
    return site_key(ident) if eco in ("web", "rss") else cle


def editeurs_citants(citants: Iterable[str]) -> set[str]:
    return {site_de_source(c) for c in citants}


def marquer(cands: list[Any], observations: Iterable[Any]) -> None:
    """Pose `copies` (site -> représentant) sur chaque candidat cité ou nommé par au moins deux sites dont des passages se recopient.
    Les autres candidats ne sont pas touchés (une copie ne peut rien changer à un seul endroit)."""
    par_site: dict[str, list[list[str]]] = {}
    for o in observations:
        par_site.setdefault(site_de_source(o.source.key), []).append(mots(o.text))
    for c in cands:
        sites = set(getattr(c, "ner_sites", {}) or {}) | editeurs_citants(getattr(c, "citants", ()) or ())
        if len(sites) < 2 or not c.nom:
            continue
        nom = mots(c.nom)
        emp = {s: [e for t in par_site.get(s, []) if (e := empreinte(passages(t, nom)))] for s in sites}
        c.copies = groupes(emp)


def independants(sites: Iterable[str], copies: dict[str, str]) -> int:
    """Nombre de sites indépendants : un groupe de copies compte pour un."""
    return len({copies.get(s, s) for s in sites})
