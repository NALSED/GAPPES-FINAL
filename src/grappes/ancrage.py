"""Promotion des décisions de `resultat_a_trancher.csv` en ancres de confiance (décision 901/Q28).

Garder un cas « à trancher » ajoute sa référence à `anchors:` dans le YAML de la grappe concernée —
exactement comme une ancre posée par Sednal à la main (rien de nouveau à construire, voir 901/Q28).
Exclure n'écrit rien : la ligne reste hors de `resultat.csv`, aucune ancre créée.

L'édition du YAML se fait par le TEXTE, jamais par un aller-retour `yaml.safe_load`/`safe_dump` :
ça effacerait les commentaires et ferait passer des valeurs par le résolveur booléen de PyYAML
(le bug de la Norvège « NO » devenue `False`, voir `900-demenagement-du-code.md`). Après chaque
ajout, le fichier est relu avec `yaml.safe_load` pour vérifier qu'il reste valide et que la
référence y figure bien ; sinon rien n'est écrit sur disque.

Décision 904/Q29 : une grappe issue d'un sujet (`sujets.yaml`, créée automatiquement) n'a pas de
fichier YAML à elle, donc pas de `anchors:` où écrire. Un fichier séparé par sujet (`config/ancres/
<grappe>.yaml`) en tient lieu — JAMAIS dans `config/apprentissage/` : rien ici n'est réécrit par la
boucle d'apprentissage, qui ne lit ces ancres qu'en lecture (`cycle/learn.py`, via `config.py` qui
les charge dans `Grappe.anchors`, au même titre qu'une ancre posée à la main dans `config/grappes/`)."""

from __future__ import annotations

import csv
import re
from pathlib import Path

import yaml

_INLINE = re.compile(r"^(?P<cle>anchors:[ \t]*)\[(?P<contenu>.*)\](?P<fin>[ \t]*(?:#.*)?)$", re.MULTILINE)
_CLE_BLOC = re.compile(r"^anchors:[ \t]*(?:#.*)?$", re.MULTILINE)
_ITEM_BLOC = re.compile(r"^([ \t]*-[ \t]*)(.+?)[ \t]*(?:#.*)?$")
_SAFE = re.compile(r"[^a-z0-9_-]+")

DECISION_GARDER = "garder"
DECISION_EXCLURE = "exclure"
ANCRES_DIR = "ancres"


def _dequote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def ancres_existantes(texte: str) -> set[str]:
    """Références déjà listées sous `anchors:`, en ligne (`[...]`) ou en bloc (`- ...`)."""
    m = _INLINE.search(texte)
    if m:
        return {_dequote(x) for x in m.group("contenu").split(",") if x.strip()}
    m = _CLE_BLOC.search(texte)
    if not m:
        return set()
    out: set[str] = set()
    for ligne in texte[m.end() :].splitlines():
        if not ligne.strip():
            continue
        bi = _ITEM_BLOC.match(ligne)
        if not bi:
            break  # fin du bloc : une ligne qui n'est plus un item de liste
        out.add(_dequote(bi.group(2)))
    return out


def ajouter_ancre(texte: str, ref: str) -> str:
    """`texte` avec `ref` ajoutée à `anchors:`, sans rien modifier d'autre. Idempotent."""
    if ref in ancres_existantes(texte):
        return texte
    m = _INLINE.search(texte)
    if m:
        contenu = m.group("contenu").strip()
        nouveau = f"{contenu}, {ref!r}" if contenu else repr(ref)
        return texte[: m.start()] + f"{m.group('cle')}[{nouveau}]{m.group('fin')}" + texte[m.end() :]
    m = _CLE_BLOC.search(texte)
    if m:
        reste = texte[m.end() :]
        premiere = next((ligne for ligne in reste.splitlines() if ligne.strip()), "")
        bi = _ITEM_BLOC.match(premiere)
        indent = re.match(r"[ \t]*", bi.group(1)).group(0) if bi else "  "
        return texte[: m.end()] + f"\n{indent}- {ref!r}" + texte[m.end() :]
    sep = "" if texte.endswith("\n") else "\n"
    return texte + f"{sep}anchors:\n  - {ref!r}\n"


def _fichier_de_grappe(racine: Path, grappe_id: str) -> Path | None:
    for f in sorted((racine / "grappes").glob("*.yaml")):
        try:
            d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            continue
        if isinstance(d, dict) and d.get("id") == grappe_id:
            return f
    return None


def fichier_ancres_sujet(racine: str | Path, grappe_id: str) -> Path:
    """`config/ancres/<grappe>.yaml` : les ancres d'une grappe-sujet (décision 904/Q29)."""
    return Path(racine) / ANCRES_DIR / f"{_SAFE.sub('_', grappe_id.lower())}.yaml"


def lire_ancres_sujet(racine: str | Path, grappe_id: str) -> tuple[str, ...]:
    """Les ancres déjà promues pour cette grappe-sujet, lues par `config.py` à chaque chargement — exactement
    comme `anchors:` dans le YAML d'une grappe déclarée à la main. Fichier absent = aucune ancre, jamais une erreur."""
    f = fichier_ancres_sujet(racine, grappe_id)
    if not f.exists():
        return ()
    try:
        d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return ()
    brut = d.get("anchors") if isinstance(d, dict) else None
    return tuple(dict.fromkeys(str(a) for a in brut)) if isinstance(brut, list) else ()


def lire_decisions(path: Path) -> list[tuple[str, str]]:
    """[(grappe_id, ref), ...] des lignes de `resultat_a_trancher.csv` marquées « garder »."""
    out = []
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if (row.get("DECISION") or "").strip().casefold() == DECISION_GARDER:
                out.append((row["GRAPPE"], row["REF"]))
    return out


def promouvoir(racine: str | Path, decisions_csv: str | Path) -> list[str]:
    """Ajoute chaque référence « gardée » aux ancres de sa grappe. Renvoie les refs effectivement
    ajoutées (dédoublonnées, déjà présentes exclues). Lève `ConfigError` si une grappe est
    introuvable ou si l'ajout rendrait le YAML invalide : rien n'est écrit dans ce cas-là."""
    from grappes.config import ConfigError

    racine = Path(racine)
    ajoutees: list[str] = []
    par_fichier: dict[Path, str] = {}
    attendues: dict[Path, set[str]] = {}
    for grappe_id, ref in lire_decisions(Path(decisions_csv)):
        fichier = _fichier_de_grappe(racine, grappe_id)
        if fichier is None:
            from grappes.autonomy import load_subjects

            if not any(s.id == grappe_id for s in load_subjects(racine).subjects):
                raise ConfigError(f"ancrage : grappe {grappe_id!r} introuvable sous {racine / 'grappes'} ni dans sujets.yaml")
            fichier = fichier_ancres_sujet(racine, grappe_id)  # grappe-sujet (904/Q29) : fichier à part, créé au besoin
        if fichier in par_fichier:
            texte = par_fichier[fichier]
        elif fichier.exists():
            texte = fichier.read_text(encoding="utf-8")
        else:
            texte = f"grappe: {grappe_id}\nanchors: []\n"  # rien sur disque avant la validation finale (voir plus bas)
        avant = ancres_existantes(texte)
        par_fichier[fichier] = ajouter_ancre(texte, ref)
        attendues.setdefault(fichier, set()).add(ref)
        if ref not in avant:
            ajoutees.append(ref)
    for fichier, texte in par_fichier.items():
        try:
            relu = yaml.safe_load(texte) or {}
        except yaml.YAMLError as exc:
            raise ConfigError(f"ancrage : {fichier} serait invalide après ajout, rien n'est écrit ({exc})") from exc
        presentes = {_dequote(a) for a in (relu.get("anchors") or [])} if isinstance(relu, dict) else set()
        manquantes = attendues[fichier] - presentes
        if manquantes:
            raise ConfigError(f"ancrage : {fichier} n'aurait pas {sorted(manquantes)} dans anchors après ajout, rien n'est écrit")
        fichier.parent.mkdir(parents=True, exist_ok=True)
        fichier.write_text(texte, encoding="utf-8")
    return ajoutees
