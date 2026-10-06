"""Chargement et validation des YAML de configuration ; empreinte `config_hash`."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from grappes.ecosystem.crossref import CrossRefRule
from grappes.models import Grappe, Lexicon


class ConfigError(ValueError):
    """Configuration invalide."""


@dataclass(frozen=True, slots=True)
class ScoringConfig:
    top_n_observations: int = 5
    seuil_min: float = 40.0
    marge_ambiguite: float = 10.0
    niveau_confirme: float = 70.0
    niveau_probable: float = 40.0
    entity_types: dict[str, str] = field(
        default_factory=lambda: {"x": "person", "telegram": "group", "web": "site"}
    )
    csv_separator: str = ";"
    csv_bom: bool = False
    w_semantic: float = 0.50
    w_ecosystem: float = 0.30
    w_anchor: float = 0.20
    crossref_floor: float = 60.0
    max_iter: int = 3
    crossref: CrossRefRule = field(default_factory=CrossRefRule)


@dataclass(frozen=True, slots=True)
class SourcesConfig:
    defaults: dict[str, float] = field(default_factory=dict)
    overrides: dict[str, float] = field(default_factory=dict)

    def weight(self, key: str) -> float:
        if key in self.overrides:
            return self.overrides[key]
        return self.defaults.get(key.split(":", 1)[0], 1.0)


@dataclass(frozen=True, slots=True)
class Config:
    scoring: ScoringConfig
    sources: SourcesConfig
    grappes: tuple[Grappe, ...]
    config_hash: str


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigError(f"{path}: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigError(f"{path}: un objet YAML est attendu")
    return data


def _weights(d: Any, where: str, *, allow_negative: bool = False) -> dict[str, float]:
    if d is None:
        return {}
    if not isinstance(d, dict):
        raise ConfigError(f"{where}: un mapping terme -> poids est attendu")
    out: dict[str, float] = {}
    for k, v in d.items():
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise ConfigError(f"{where}: poids non numérique pour {k!r}")
        if v <= 0 and not allow_negative:
            raise ConfigError(f"{where}: poids {k!r} doit être > 0")
        out[str(k)] = float(v)
    return out


def load_scoring(path: Path) -> ScoringConfig:
    d = _load_yaml(path)
    csv = d.get("csv") or {}
    default = ScoringConfig()
    w = d.get("poids_confiance") or {}
    cr = d.get("crossref") or {}
    dr = default.crossref
    try:
        window = cr.get("window_days", dr.window_days)
        rule = CrossRefRule(
            min_citers=int(cr.get("min_citers", dr.min_citers)),
            min_ecosystems=int(cr.get("min_ecosystems", dr.min_ecosystems)),
            min_weight_sum=float(cr.get("min_weight_sum", dr.min_weight_sum)),
            min_citer_confidence=float(cr.get("min_citer_confidence", dr.min_citer_confidence)),
            window_days=None if window is None else int(window),
        )
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{path}: crossref : {exc}") from exc
    try:
        cfg = ScoringConfig(
            top_n_observations=int(d.get("top_n_observations", default.top_n_observations)),
            seuil_min=float(d.get("seuil_min", default.seuil_min)),
            marge_ambiguite=float(d.get("marge_ambiguite", default.marge_ambiguite)),
            niveau_confirme=float(d.get("niveau_confirme", default.niveau_confirme)),
            niveau_probable=float(d.get("niveau_probable", default.niveau_probable)),
            entity_types={str(k): str(v) for k, v in (d.get("entity_types") or {}).items()}
            or default.entity_types,
            csv_separator=str(csv.get("separator", default.csv_separator)),
            csv_bom=bool(csv.get("bom", default.csv_bom)),
            w_semantic=float(w.get("semantique", default.w_semantic)),
            w_ecosystem=float(w.get("ecosysteme", default.w_ecosystem)),
            w_anchor=float(w.get("ancrage", default.w_anchor)),
            crossref_floor=float(d.get("crossref_floor", default.crossref_floor)),
            max_iter=int(d.get("max_iter", default.max_iter)),
            crossref=rule,
        )
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{path}: {exc}") from exc
    if cfg.top_n_observations < 1:
        raise ConfigError(f"{path}: top_n_observations doit être >= 1")
    if (
        min(cfg.w_semantic, cfg.w_ecosystem, cfg.w_anchor) < 0
        or (cfg.w_semantic + cfg.w_ecosystem + cfg.w_anchor) <= 0
    ):
        raise ConfigError(f"{path}: poids_confiance invalides")
    if cfg.max_iter < 1:
        raise ConfigError(f"{path}: max_iter doit être >= 1")
    if cfg.crossref.min_citers < 1 or cfg.crossref.min_ecosystems < 1:
        raise ConfigError(f"{path}: crossref.min_citers et min_ecosystems doivent être >= 1")
    if len(cfg.csv_separator) != 1:
        raise ConfigError(f"{path}: csv.separator doit être un caractère")
    bad = set(cfg.entity_types.values()) - {"person", "group", "site"}
    if bad:
        raise ConfigError(f"{path}: types d'entité inconnus {sorted(bad)}")
    return cfg


def load_sources(path: Path) -> SourcesConfig:
    d = _load_yaml(path)
    return SourcesConfig(
        defaults=_weights(d.get("defaults"), f"{path}:defaults"),
        overrides=_weights(d.get("overrides"), f"{path}:overrides"),
    )


def load_grappe(path: Path) -> Grappe:
    d = _load_yaml(path)
    gid = d.get("id")
    if not isinstance(gid, str) or not gid.strip():
        raise ConfigError(f"{path}: `id` manquant")
    lex = d.get("lexicon") or {}
    terms = _weights(lex.get("terms"), f"{path}:lexicon.terms")
    if not terms:
        raise ConfigError(f"{path}: lexique vide")
    negative = _weights(lex.get("negative"), f"{path}:lexicon.negative")
    scale = float(d.get("scale", 3.0))
    if scale <= 0:
        raise ConfigError(f"{path}: scale doit être > 0")
    return Grappe(
        grappe_id=gid.strip(),
        label=str(d.get("label", gid)),
        lexicon=Lexicon(terms=terms, negative=negative),
        anchors=tuple(str(a) for a in d.get("anchors") or ()),
        oppositions=tuple(str(o) for o in d.get("oppositions") or ()),
        scale=scale,
    )


def load_config(config_dir: str | Path = "config") -> Config:
    root = Path(config_dir)
    if not root.is_dir():
        raise ConfigError(f"dossier de configuration introuvable : {root}")
    scoring_path, sources_path = root / "scoring.yaml", root / "sources.yaml"
    scoring = load_scoring(scoring_path) if scoring_path.exists() else ScoringConfig()
    sources = load_sources(sources_path) if sources_path.exists() else SourcesConfig()
    files = sorted((root / "grappes").glob("*.yaml"))
    grappes = tuple(load_grappe(p) for p in files)
    ids = [g.grappe_id for g in grappes]
    if len(set(ids)) != len(ids):
        raise ConfigError("identifiants de grappe dupliqués")
    if not grappes:
        raise ConfigError(f"aucune grappe dans {root / 'grappes'}")
    for g in grappes:
        for o in g.oppositions:
            if ":" not in o and o not in ids:
                raise ConfigError(f"{g.grappe_id}: opposition vers une grappe inconnue {o!r}")
    # empreinte : contenu brut de tous les fichiers pris en compte, dans l'ordre
    h = hashlib.sha256()
    for p in [p for p in (scoring_path, sources_path) if p.exists()] + files:
        h.update(p.name.encode())
        h.update(p.read_bytes())
    return Config(scoring, sources, grappes, h.hexdigest()[:16])


def config_summary(cfg: Config) -> str:
    return json.dumps(
        {"hash": cfg.config_hash, "grappes": [g.grappe_id for g in cfg.grappes]}, ensure_ascii=False
    )
