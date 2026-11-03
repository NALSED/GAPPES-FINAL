"""Sortie finale simple : `sorties/resultat.csv`, une seule colonne `NOM` (SORTIE_FINALE.md).

Une ligne par entité retenue : assignée à une grappe (confirmée ou probable, seuil configurable),
sous un nom lisible. Variantes d'écriture fusionnées, tri alphabétique, UTF-8 sans BOM. Un fichier
par grappe (`resultat_<grappe>.csv`) quand il y en a plusieurs. Les scores et explications restent
dans `entites.csv`, `appartenances.csv`, la base et le serveur MCP.

Personnes physiques (type `person`, sans indice institutionnel explicite) : décision 901/Q21, trois cas
(l'ancienne règle « en cas de doute, une personne » excluait des résultats utiles, ex. le compte Instagram
public de Messi dans une recherche sur le football). (1) Matche directement la recherche (statut « classé »,
au-dessus du seuil) : gardée dans `resultat.csv`, comme n'importe quelle entité. (2) Hors sujet (sous le seuil,
ou statut « non classé ») : exclue, comme avant. (3) Doute (statut « ambigu », le programme ne peut pas
trancher) : part dans `resultat_a_trancher.csv`, jamais dans `resultat.csv` ni silencieusement exclue. Le
réglage `resultat.inclure_personnes` reste une échappatoire : à true, les personnes suivent la même règle que
les autres entités, sans fichier « à trancher » séparé.
"""

from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

from grappes.autonomy import Autonomy, load_autonomy
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


def select_rows(
    result: AssignResult, cfg: Config
) -> tuple[dict[str, list[tuple[str, float, str]]], list[tuple[str, float, str, str]]]:
    """(grappe -> [(nom, confiance, clé de source)] des entités retenues, [(nom, confiance, clé, grappe)] des
    personnes physiques en doute — décision 901/Q21), avant fusion des variantes."""
    sc = cfg.scoring
    threshold = (
        sc.niveau_probable if sc.resultat_confiance_min is None else sc.resultat_confiance_min
    )
    kept = {CLASSE, AMBIGU} if sc.resultat_inclure_ambigus else {CLASSE}
    ents = {e.entity_id: e for e in result.entities}
    out: dict[str, list[tuple[str, float, str]]] = {g.grappe_id: [] for g in cfg.grappes}
    doute: list[tuple[str, float, str, str]] = []
    for m in result.memberships:
        e = ents[m["entity_id"]]
        if m["confidence"] < threshold:
            continue
        est_personne = e.type is EntityType.PERSON and not sc.resultat_inclure_personnes
        if est_personne and m["status"] == AMBIGU:
            name = readable_name(result.names.get(e.primary_ref), e.primary_ref.split(":", 1)[-1])
            if name:
                doute.append((name, m["confidence"], e.primary_ref, m["grappe_id"]))
            continue  # doute : ni un match direct ni du bruit, jamais silencieusement exclu ni inclus
        if m["status"] not in kept:
            continue  # hors sujet : exclu, comme pour n'importe quelle entité
        name = readable_name(result.names.get(e.primary_ref), e.primary_ref.split(":", 1)[-1])
        if name:
            out[m["grappe_id"]].append((name, m["confidence"], e.primary_ref))
    return out, doute


def select_names(result: AssignResult, cfg: Config) -> dict[str, list[tuple[str, float]]]:
    """grappe -> [(nom, confiance)] des entités retenues, avant fusion des variantes."""
    by_grappe, _ = select_rows(result, cfg)
    return {g: [(n, c) for n, c, _ in rows] for g, rows in by_grappe.items()}


def merge_rows(
    rows: list[tuple[str, float, str]], suffixes: tuple[str, ...] = ()
) -> list[tuple[str, str]]:
    """Fusionne les variantes d'un même nom ; garde la plus fiable (puis l'ordre alphabétique). (nom, clé de source)."""
    best: dict[str, tuple[str, float, str]] = {}
    for name, conf, ref in rows:
        key = dedup_key(name, suffixes)
        if not key:
            continue
        cur = best.get(key)
        if cur is None or (-conf, sort_key(name)) < (-cur[1], sort_key(cur[0])):
            best[key] = (name, conf, ref)
    return [(n, r) for n, _, r in sorted(best.values(), key=lambda v: sort_key(v[0]))]


def merge_variants(rows: list[tuple[str, float]], suffixes: tuple[str, ...] = ()) -> list[str]:
    """Fusionne les variantes d'un même nom ; garde la plus fiable (puis l'ordre alphabétique)."""
    return [n for n, _ in merge_rows([(n, c, "") for n, c in rows], suffixes)]


def _write(path: Path, names: list[str]) -> Path:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["NOM"])
        for n in names:
            w.writerow([safe_cell(n)])
    return path


A_TRANCHER_HEADER = ["NOM", "GRAPPE", "REF", "DECISION"]


def _write_a_trancher(path: Path, rows: list[tuple[str, float, str, str]]) -> Path:
    """`resultat_a_trancher.csv` (décision 901/Q21) : une ligne par (référence, grappe) en doute, triée par nom.
    Pas de fusion de variantes ici (chaque ligne doit rester identifiable par référence pour `ancrage.py`,
    décision 901/Q28) ; `DECISION` vide, à remplir « garder » ou « exclure » à la main."""
    vues: dict[tuple[str, str], tuple[str, str, str]] = {}
    for name, _conf, ref, grappe in rows:
        vues[(ref, grappe)] = (name, grappe, ref)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(A_TRANCHER_HEADER)
        for name, grappe, ref in sorted(vues.values(), key=lambda v: sort_key(v[0])):
            w.writerow([safe_cell(name), grappe, ref, ""])
    return path


TSITES_HEADER = ["nom", "ville", "pays"]


def _town(raw: str) -> str:
    """Commune telle que fournie par le registre ; les registres la donnent en capitales : mise en forme seulement."""
    t = " ".join(raw.split())
    return t.title() if t.isupper() else t


def write_tsites(
    path: Path,
    rows: list[tuple[str, str]],
    auto: Autonomy,
    places: dict[str, tuple[str, str]] | None = None,
) -> Path:
    """`resultat_tsites.csv` (compatibilité trouver-sites, D59) : nom;ville;pays, UTF-8 sans BOM. Mêmes noms que
    `resultat.csv`. Ville : seulement celle d'un registre officiel, sinon vide (jamais déduite). Pays : celui du
    registre s'il en donne un, sinon `export_tsites.pays_defaut`."""
    places = places or {}
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        w.writerow(TSITES_HEADER)
        for name, ref in rows:
            town, country = places.get(ref, ("", ""))
            w.writerow([safe_cell(name), _town(town), country or auto.export_tsites_pays_defaut])
    return path


def write_resultat(
    result: AssignResult,
    cfg: Config,
    out_dir: str | Path,
    auto: Autonomy | None = None,
    places: dict[str, tuple[str, str]] | None = None,
) -> list[Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    sfx = cfg.scoring.resultat_suffixes
    by_grappe, doute = select_rows(result, cfg)
    everything = [row for rows in by_grappe.values() for row in rows]
    merged = merge_rows(everything, sfx)
    a_trancher = out / "resultat_a_trancher.csv"
    a_trancher_paths = []
    if doute:
        a_trancher_paths.append(_write_a_trancher(a_trancher, doute))
    else:
        a_trancher.unlink(missing_ok=True)  # pas de doute cette fois : pas de fichier périmé
    from grappes.sortie import LigneSortie, charger_profils
    from grappes.sortie import ecrire as ecrire_profils

    profils = {p.id: p for p in charger_profils(cfg.racine if cfg.racine is not None else "config")}
    paths = []
    if profils.get("resultat") is None or profils["resultat"].actif:
        paths.append(_write(out / "resultat.csv", [n for n, _ in merged]))
        if len(cfg.grappes) > 1:
            for gid, rows in by_grappe.items():
                slug = re.sub(r"[^\w.-]", "_", gid)
                paths.append(
                    _write(out / f"resultat_{slug}.csv", [n for n, _ in merge_rows(rows, sfx)])
                )
    else:
        (out / "resultat.csv").unlink(missing_ok=True)
    paths += a_trancher_paths
    if auto is None:
        auto = load_autonomy(cfg.racine) if cfg.racine is not None else Autonomy()
    tsites = out / "resultat_tsites.csv"
    if auto.export_tsites_actif and (profils.get("tsites") is None or profils["tsites"].actif):
        paths.append(write_tsites(tsites, merged, auto, places))
    else:
        tsites.unlink(missing_ok=True)  # sortie désactivée : pas de fichier périmé
    # profils configurables (D64) : tout autre profil (ex. `brut`), depuis les mêmes lignes retenues
    places = places or {}
    conf = {ref: c for rows in by_grappe.values() for _, c, ref in rows}
    lignes = [
        LigneSortie(
            n, _town(places.get(ref, ("", ""))[0]), places.get(ref, ("", ""))[1] or auto.export_tsites_pays_defaut,
            conf.get(ref), "", "non calibré (score historique du système)", [ref], [], "retenu",
        )
        for n, ref in merged
    ]  # fmt: skip
    paths += ecrire_profils(lignes, [p for p in profils.values()], out, ignorer=frozenset({"resultat", "tsites"}))
    return paths
