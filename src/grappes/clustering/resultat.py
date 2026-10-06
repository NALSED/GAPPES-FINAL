"""Sortie finale simple : `sorties/resultat.csv`, une seule colonne `NOM` (SORTIE_FINALE.md).

Une ligne par entité retenue : assignée à une grappe (confirmée ou probable, seuil configurable),
sous un nom lisible. Variantes d'écriture fusionnées, tri alphabétique, UTF-8 sans BOM. Un fichier
par grappe (`resultat_<grappe>.csv`) quand il y en a plusieurs. Les personnes physiques (type
`person`, c'est-à-dire sans indice institutionnel explicite) sont exclues sauf `inclure_personnes`. Les scores et explications restent dans
`entites.csv`, `appartenances.csv`, la base et le serveur MCP.
"""

from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

from grappes.clustering.assign import AMBIGU, CLASSE, AssignResult
from grappes.clustering.export import safe_cell
from grappes.config import Config
from grappes.models import EntityType
from grappes.semantic.scoring import normalize

_SPACES = re.compile(r"\s+")
_TECH_LOOKING = re.compile(r"^[\w.-]+\.[a-z]{2,}$", re.IGNORECASE)  # exemple.org : un domaine


def readable_name(name: str | None, ident: str = "") -> str | None:
    """Nom lisible nettoyé, ou `None` : vide, URL, domaine seul, `@compte`, identifiant technique."""
    if not name:
        return None
    clean = "".join(" " if unicodedata.category(c) in ("Cc", "Zl", "Zp") else c for c in name)
    clean = "".join(c for c in clean if unicodedata.category(c) not in ("Cf", "Cs", "Co", "Cn"))
    clean = _SPACES.sub(" ", clean).strip()
    if not clean or not any(c.isalpha() for c in clean):
        return None
    low = clean.casefold()
    if "://" in clean or low.startswith(("www.", "@", "t.me/")) or "/" in clean:
        return None
    if _TECH_LOOKING.match(clean) or (ident and low == ident.casefold() and " " not in clean):
        return None
    return clean


def dedup_key(name: str, suffixes: tuple[str, ...] = ()) -> str:
    """Clé de fusion des variantes : casse, accents, ponctuation, espaces, suffixes ignorés."""
    words = re.sub(r"[^\w]+", " ", normalize(name)).split()
    sfx = {normalize(s) for s in suffixes}
    while len(words) > 1 and words[-1] in sfx:
        words.pop()
    return "".join(words)


def sort_key(name: str) -> tuple[str, str]:
    return (re.sub(r"[^\w]+", " ", normalize(name)).strip(), name)


def select_names(result: AssignResult, cfg: Config) -> dict[str, list[tuple[str, float]]]:
    """grappe -> [(nom, confiance)] des entités retenues, avant fusion des variantes."""
    sc = cfg.scoring
    threshold = (
        sc.niveau_probable if sc.resultat_confiance_min is None else sc.resultat_confiance_min
    )
    kept = {CLASSE, AMBIGU} if sc.resultat_inclure_ambigus else {CLASSE}
    ents = {e.entity_id: e for e in result.entities}
    out: dict[str, list[tuple[str, float]]] = {g.grappe_id: [] for g in cfg.grappes}
    for m in result.memberships:
        e = ents[m["entity_id"]]
        if m["status"] not in kept or m["confidence"] < threshold:
            continue
        if e.type is EntityType.PERSON and not sc.resultat_inclure_personnes:
            continue  # personnes physiques exclues par défaut (en cas de doute : une personne)
        name = readable_name(result.names.get(e.primary_ref), e.primary_ref.split(":", 1)[-1])
        if name:
            out[m["grappe_id"]].append((name, m["confidence"]))
    return out


def merge_variants(rows: list[tuple[str, float]], suffixes: tuple[str, ...] = ()) -> list[str]:
    """Fusionne les variantes d'un même nom ; garde la plus fiable (puis l'ordre alphabétique)."""
    best: dict[str, tuple[str, float]] = {}
    for name, conf in rows:
        key = dedup_key(name, suffixes)
        if not key:
            continue
        cur = best.get(key)
        if cur is None or (-conf, sort_key(name)) < (-cur[1], sort_key(cur[0])):
            best[key] = (name, conf)
    return sorted((n for n, _ in best.values()), key=sort_key)


def _write(path: Path, names: list[str]) -> Path:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["NOM"])
        for n in names:
            w.writerow([safe_cell(n)])
    return path


def write_resultat(result: AssignResult, cfg: Config, out_dir: str | Path) -> list[Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    sfx = cfg.scoring.resultat_suffixes
    by_grappe = select_names(result, cfg)
    everything = [row for rows in by_grappe.values() for row in rows]
    paths = [_write(out / "resultat.csv", merge_variants(everything, sfx))]
    if len(cfg.grappes) > 1:
        for gid, rows in by_grappe.items():
            slug = re.sub(r"[^\w.-]", "_", gid)
            paths.append(_write(out / f"resultat_{slug}.csv", merge_variants(rows, sfx)))
    return paths
