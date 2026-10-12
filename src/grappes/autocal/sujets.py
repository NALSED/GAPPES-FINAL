"""Génération reproductible des sujets d'évaluation (graine notée) et des trois jeux disjoints.

Un sujet = une classe d'organisations Wikidata comptant 20 à 200 instances françaises : on obtient d'un coup une
phrase de sujet, une liste attendue (référence silver standard) et R pour la R-précision. Difficulté
(facile / moyen / difficile) = présence des acteurs dans Wikidata et dans les registres : part d'instances avec site
officiel (P856) et avec identifiant SIREN (P1616), répartie en terciles. Les trois jeux (mise au point, validation,
test) ont la même proportion de difficultés ; chacun garde un contrôle négatif (aucun acteur réel).
"""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path

from grappes.autocal.reference import FR, Reference, build, class_where
from grappes.autocal.wikidata import Wikidata, WikidataError

SEED = 20261012  # graine de tirage (notée ici et dans calibration.md)
ORG = "Q43229"  # organisation

CLASSES_QUERY = (
    "SELECT ?class (COUNT(?item) AS ?n) WHERE { ?item wdt:P856 ?site ; wdt:P17 wd:Q142 ; wdt:P31 ?class . } "
    "GROUP BY ?class HAVING (COUNT(?item) >= 20 && COUNT(?item) <= 250)"
)


@dataclass(slots=True)
class Sujet:
    id: str
    phrase: str
    jeu: str = ""  # dev | validation | test
    difficulte: str = ""  # facile | moyen | difficile | temoin
    origine: str = ""  # amorcage | genere | controle_negatif
    classe: str = ""  # QID de la classe (sujets générés)
    r: int = 0
    part_site: float = 0.0
    part_siren: float = 0.0
    notes: str = ""
    where: str = ""
    classes_ok: list[str] = field(default_factory=list)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(asdict(self), ensure_ascii=False, indent=1), encoding="utf-8")


def classes_organisations(w: Wikidata, log=print) -> dict[str, dict]:
    """Classes d'organisations (P279* organisation) de 20 à 250 instances françaises avec site officiel."""
    rows = w.sparql(CLASSES_QUERY)
    ids = [r["class"] for r in rows]
    n = {r["class"]: int(r["n"]) for r in rows}
    labels: dict[str, str] = {}
    for i in range(0, len(ids), 50):
        d = w.api(action="wbgetentities", ids="|".join(ids[i : i + 50]), props="labels", languages="fr|en")
        for k, v in d["entities"].items():
            lab = v.get("labels", {})
            labels[k] = (lab.get("fr") or lab.get("en") or {}).get("value", "")
    org: set[str] = set()
    for i in range(0, len(ids), 10):
        chunk = ids[i : i + 10]
        q = "SELECT DISTINCT ?class WHERE { VALUES ?class { %s } ?class wdt:P279* wd:%s . }" % (
            " ".join("wd:" + c for c in chunk), ORG,
        )  # fmt: skip
        try:
            org |= {r["class"] for r in w.sparql(q)}
        except WikidataError as exc:
            log(f"classes {i}-{i + 10} : {exc}")
    return {c: {"label": labels.get(c, ""), "n": n[c]} for c in sorted(org) if labels.get(c)}


def mesurer_classe(w: Wikidata, qid: str) -> dict:
    """Taille de la référence (instances directes en France) et parts avec site officiel / SIREN."""
    q = (
        "SELECT (COUNT(DISTINCT ?item) AS ?n) (COUNT(DISTINCT ?s) AS ?ns) (COUNT(DISTINCT ?r) AS ?nr) WHERE { "
        f"?item wdt:P31 wd:{qid} ; wdt:P17 wd:{FR} . OPTIONAL {{ ?item wdt:P856 ?s }} OPTIONAL {{ ?item wdt:P1616 ?r }} }}"
    )
    row = w.sparql(q)[0]
    n = int(row["n"])
    return {"n": n, "part_site": int(row["ns"]) / n if n else 0.0, "part_siren": int(row["nr"]) / n if n else 0.0}


def phrase_de(label: str) -> str:
    return f"Les organisations de type « {label} » en France"


def tirer(w: Wikidata, classes: dict[str, dict], combien: int, seed: int = SEED, log=print) -> list[Sujet]:
    """Tire au hasard (graine fixée) `combien` classes dont la référence compte 20 à 200 entités."""
    rng = random.Random(seed)
    ordre = sorted(classes)
    rng.shuffle(ordre)
    out: list[Sujet] = []
    for qid in ordre:
        if len(out) >= combien:
            break
        try:
            m = mesurer_classe(w, qid)
        except WikidataError as exc:
            log(f"{qid} ignorée : {exc}")
            continue
        if not 20 <= m["n"] <= 200:
            continue
        lab = classes[qid]["label"]
        out.append(
            Sujet(
                id=f"g-{qid.lower()}", phrase=phrase_de(lab), origine="genere", classe=qid, r=m["n"],
                part_site=round(m["part_site"], 3), part_siren=round(m["part_siren"], 3),
                where=class_where(qid), classes_ok=[qid], notes=lab,
            )  # fmt: skip
        )
    return out


def difficultes(sujets: list[Sujet]) -> None:
    """Difficulté par terciles de la présence (moyenne part_site, part_siren) : haute = facile."""
    ordre = sorted(sujets, key=lambda s: (-(s.part_site + s.part_siren) / 2, s.id))
    n = len(ordre)
    for i, s in enumerate(ordre):
        s.difficulte = "facile" if i < n / 3 else "moyen" if i < 2 * n / 3 else "difficile"


def construire_reference(w: Wikidata, s: Sujet) -> Reference:
    return build(w, s.id, s.phrase, s.where, s.classes_ok)
