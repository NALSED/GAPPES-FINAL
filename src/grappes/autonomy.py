"""Configuration d'autonomie : `config/autonomie.yaml` (limites, interdits, interrupteur) et
`config/sujets.yaml` (sujets en une phrase). C'est tout ce que Sednal fournit (FINAL.md § 2).

Règles générales de collecte (codées, non configurables à la baisse) : sources publiques
uniquement, robots.txt respecté, ni connexion ni compte, ni contournement de limite ou de captcha,
délai d'au moins 1 s par domaine, arrêt sur 403/429, User-Agent identifiable. Sednal édite seulement
la liste des INTERDITS (domaines, motifs) et les quotas.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from grappes.config import ConfigError

MIN_DOMAIN_DELAY_S = 1.0  # plancher imposé par les règles générales
DEFAULT_UA = "grappes-collecte/1 (collecte automatique de pages publiques ; respecte robots.txt)"
# Réseaux sociaux : jamais lus par le récupérateur de pages (leurs liens deviennent des citations).
DEFAULT_SOCIAL = (
    "x.com", "twitter.com", "t.co", "t.me", "telegram.me", "instagram.com", "facebook.com",
    "fb.com", "tiktok.com", "linkedin.com", "snapchat.com", "threads.net", "whatsapp.com",
)  # fmt: skip


@dataclass(frozen=True, slots=True)
class Autonomy:
    autonome: bool = False  # interrupteur : false = dry-run, rien n'est écrit ni appelé
    stop_file: Path = Path("donnees/STOP")  # sa présence arrête tout immédiatement
    # limites générales
    requetes_par_cycle: int = 50
    pages_par_cycle: int = 100
    nouvelles_sources_par_cycle: int = 20
    elements_par_cycle: int = 200  # observations ingérées au plus par cycle
    profondeur: int = 1  # 0 = résultats de recherche seulement ; 1 = + liens sortants des pages
    seuil_ingestion: float = 20.0  # proximité minimale (0 à 100) avec un sujet
    # interdits (éditables)
    interdits_domaines: tuple[str, ...] = ()
    interdits_motifs: tuple[str, ...] = ()
    # collecte
    delai_domaine_s: float = MIN_DOMAIN_DELAY_S
    user_agent: str = DEFAULT_UA
    reseaux_non_lus: tuple[str, ...] = DEFAULT_SOCIAL
    max_octets_page: int = 1_000_000
    # amorçage
    amorcage_max_termes: int = 20
    amorcage_poids: float = 0.4
    # apprentissage
    apprentissage_actif: bool = True
    min_confirmees: int = 3
    min_ecosystemes: int = 2
    max_termes_par_cycle: int = 5
    max_termes_total: int = 30
    poids_appris: float = 0.3
    expiration_cycles: int = 4
    # recalibrage borné
    recalibrage_actif: bool = True
    variation_max: float = 5.0
    bornes_seuil_min: tuple[float, float] = (30.0, 60.0)
    bornes_marge: tuple[float, float] = (5.0, 20.0)
    # stabilité : au-delà, retour en arrière automatique
    max_changement_grappe: float = 0.25
    max_taux_ambiguite: float = 0.5
    chute_max_confirmes: float = 0.3
    max_derive_lexique: float = 1.0
    instantanes_conserves: int = 10
    rapports_dir: Path = Path("rapports")


@dataclass(frozen=True, slots=True)
class Subject:
    id: str  # identifiant de grappe dérivé de la phrase
    phrase: str


@dataclass(frozen=True, slots=True)
class Subjects:
    subjects: tuple[Subject, ...] = field(default_factory=tuple)


def _yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigError(f"{path}: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigError(f"{path}: un objet YAML est attendu")
    return data


def _num(d: dict[str, Any], key: str, default: float, path: Path, minimum: float = 0.0) -> float:
    try:
        v = float(d.get(key, default))
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{path}: {key} doit être un nombre") from exc
    if not math.isfinite(v) or v < minimum:
        raise ConfigError(f"{path}: {key} doit être un nombre fini >= {minimum:g}")
    return v


def _strs(d: dict[str, Any], key: str, default: tuple[str, ...], path: Path) -> tuple[str, ...]:
    raw = d.get(key)
    if raw is None:
        return default
    if not isinstance(raw, list) or not all(isinstance(x, str) and x.strip() for x in raw):
        raise ConfigError(f"{path}: {key} doit être une liste de textes non vides")
    return tuple(dict.fromkeys(x.strip().casefold() for x in raw))


def _bounds(d: dict[str, Any], key: str, default: tuple[float, float], path: Path):
    raw = d.get(key)
    if raw is None:
        return default
    if not (isinstance(raw, list) and len(raw) == 2):
        raise ConfigError(f"{path}: {key} doit être [min, max]")
    lo, hi = (_num({"v": x}, "v", 0, path) for x in raw)
    if not 0 <= lo <= hi <= 100:
        raise ConfigError(f"{path}: {key} doit vérifier 0 <= min <= max <= 100")
    return (lo, hi)


def load_autonomy(config_dir: str | Path = "config") -> Autonomy:
    """`config/autonomie.yaml` ; absent = tout par défaut, donc `autonome: false`."""
    path = Path(config_dir) / "autonomie.yaml"
    if not path.exists():
        return Autonomy()
    d = _yaml(path)
    base = Autonomy()
    ap, rc, st = (d.get(k) or {} for k in ("apprentissage", "recalibrage", "stabilite"))
    for name, section in (("apprentissage", ap), ("recalibrage", rc), ("stabilite", st)):
        if not isinstance(section, dict):
            raise ConfigError(f"{path}: {name} doit être un mapping")
    amorcage = d.get("amorcage") or {}
    if not isinstance(amorcage, dict):
        raise ConfigError(f"{path}: amorcage doit être un mapping")
    interdits = d.get("interdits") or {}
    if not isinstance(interdits, dict):
        raise ConfigError(f"{path}: interdits doit être un mapping (domaines, motifs)")
    ua = d.get("user_agent", base.user_agent)
    if not isinstance(ua, str) or not ua.strip():
        raise ConfigError(f"{path}: user_agent doit être un texte (identifiable)")
    return Autonomy(
        autonome=bool(d.get("autonome", False)),
        stop_file=Path(str(d.get("stop_file", base.stop_file))),
        requetes_par_cycle=int(_num(d, "requetes_par_cycle", base.requetes_par_cycle, path)),
        pages_par_cycle=int(_num(d, "pages_par_cycle", base.pages_par_cycle, path)),
        nouvelles_sources_par_cycle=int(
            _num(d, "nouvelles_sources_par_cycle", base.nouvelles_sources_par_cycle, path)
        ),
        elements_par_cycle=int(_num(d, "elements_par_cycle", base.elements_par_cycle, path)),
        profondeur=int(_num(d, "profondeur", base.profondeur, path)),
        seuil_ingestion=_num(d, "seuil_ingestion", base.seuil_ingestion, path),
        interdits_domaines=_strs(interdits, "domaines", (), path),
        interdits_motifs=_strs(interdits, "motifs", (), path),
        delai_domaine_s=max(
            MIN_DOMAIN_DELAY_S, _num(d, "delai_domaine_s", MIN_DOMAIN_DELAY_S, path)
        ),
        user_agent=ua.strip(),
        reseaux_non_lus=tuple(
            dict.fromkeys((*DEFAULT_SOCIAL, *_strs(d, "reseaux_non_lus", (), path)))
        ),
        max_octets_page=int(_num(d, "max_octets_page", base.max_octets_page, path, 1000)),
        amorcage_max_termes=int(_num(amorcage, "max_termes", base.amorcage_max_termes, path)),
        amorcage_poids=_num(amorcage, "poids", base.amorcage_poids, path),
        apprentissage_actif=bool(ap.get("actif", True)),
        min_confirmees=int(_num(ap, "min_confirmees", base.min_confirmees, path, 1)),
        min_ecosystemes=int(_num(ap, "min_ecosystemes", base.min_ecosystemes, path, 1)),
        max_termes_par_cycle=int(_num(ap, "max_termes_par_cycle", base.max_termes_par_cycle, path)),
        max_termes_total=int(_num(ap, "max_termes_total", base.max_termes_total, path)),
        poids_appris=_num(ap, "poids", base.poids_appris, path),
        expiration_cycles=int(_num(ap, "expiration_cycles", base.expiration_cycles, path, 1)),
        recalibrage_actif=bool(rc.get("actif", True)),
        variation_max=_num(rc, "variation_max", base.variation_max, path),
        bornes_seuil_min=_bounds(rc, "bornes_seuil_min", base.bornes_seuil_min, path),
        bornes_marge=_bounds(rc, "bornes_marge", base.bornes_marge, path),
        max_changement_grappe=_num(st, "max_changement_grappe", base.max_changement_grappe, path),
        max_taux_ambiguite=_num(st, "max_taux_ambiguite", base.max_taux_ambiguite, path),
        chute_max_confirmes=_num(st, "chute_max_confirmes", base.chute_max_confirmes, path),
        max_derive_lexique=_num(st, "max_derive_lexique", base.max_derive_lexique, path),
        instantanes_conserves=int(
            _num(d, "instantanes_conserves", base.instantanes_conserves, path, 1)
        ),
        rapports_dir=Path(str(d.get("rapports_dir", base.rapports_dir))),
    )


def slug(phrase: str) -> str:
    """Identifiant de grappe stable dérivé d'une phrase : `sujet-<mots>` (accents et ponctuation ôtés)."""
    import re

    from grappes.semantic.scoring import normalize

    words = re.sub(r"[^\w]+", " ", normalize(phrase)).split()[:6]
    return "sujet-" + "-".join(words) if words else "sujet"


def load_subjects(config_dir: str | Path = "config") -> Subjects:
    """`config/sujets.yaml` : `sujets: ["une phrase", ...]`. Absent = aucun sujet."""
    path = Path(config_dir) / "sujets.yaml"
    if not path.exists():
        return Subjects()
    raw = _yaml(path).get("sujets") or []
    if not isinstance(raw, list) or not all(isinstance(x, str) and x.strip() for x in raw):
        raise ConfigError(f"{path}: `sujets` doit être une liste de phrases")
    seen: dict[str, Subject] = {}
    for phrase in raw:
        phrase = " ".join(phrase.split())
        sid = slug(phrase)
        if sid in seen and seen[sid].phrase != phrase:
            n = 2
            while f"{sid}-{n}" in seen:
                n += 1
            sid = f"{sid}-{n}"
        seen.setdefault(sid, Subject(sid, phrase))
    return Subjects(tuple(seen.values()))
