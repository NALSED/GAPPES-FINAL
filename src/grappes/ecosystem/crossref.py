"""Citations et recoupement (le recoupement lui-même arrive en phase 4)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from grappes.canon import canonical_domain, telegram_channel
from grappes.models import Observation


@dataclass(frozen=True, slots=True)
class Citation:
    citer: str  # clé canonique de la source citante
    cited: str  # clé canonique de l'élément cité (web:domaine, x:handle, ...)
    ecosystem: str  # écosystème de la source citante
    obs_id: str
    ts: datetime | None


def build_citations(observations: list[Observation]) -> list[Citation]:
    """Une citation par (observation, élément cité) ; auto-citations ignorées.

    Les liens sont rattachés au domaine (`web:domaine`), sauf les liens `t.me/<canal>` qui
    citent le canal Telegram (`telegram:canal`). Tri stable pour la reproductibilité.
    """
    out: dict[tuple[str, str, str], Citation] = {}
    for o in observations:
        cited_keys = [m.key for m in o.mentions]
        for u in o.links:
            channel = telegram_channel(u)
            if channel:
                cited_keys.append(f"telegram:{channel}")
            elif d := canonical_domain(u):
                cited_keys.append(f"web:{d}")
        for cited in cited_keys:
            if cited == o.source.key:
                continue
            out.setdefault(
                (o.source.key, cited, o.obs_id),
                Citation(o.source.key, cited, o.source.ecosystem, o.obs_id, o.ts),
            )
    return [out[k] for k in sorted(out)]


@dataclass(frozen=True, slots=True)
class CrossRefRule:
    min_citers: int = 3  # X : nombre minimal de sources citantes distinctes
    min_ecosystems: int = 2  # croisement d'écosystèmes
    min_weight_sum: float = 3.0  # somme minimale des poids des citants
    min_citer_confidence: float = 50.0  # un citant ne compte que s'il est déjà membre
    window_days: int | None = 180  # fenêtre temporelle (filtre appliqué en amont)


@dataclass(frozen=True, slots=True)
class ValidationRecord:
    cited: str
    grappe_id: str
    citers: tuple[str, ...]
    ecosystems: tuple[str, ...]
    weight_sum: float
    validated: bool
    reasons: tuple[str, ...]  # explicabilité : pourquoi validé / pourquoi refusé


def filter_window(citations: list[Citation], window_days: int | None) -> list[Citation]:
    """Garde les citations dans la fenêtre, relative à la plus récente (pas à l'horloge)."""
    stamped = [c.ts for c in citations if c.ts is not None]
    if window_days is None or not stamped:
        return citations
    cut = max(stamped).timestamp() - window_days * 86400
    return [c for c in citations if c.ts is None or c.ts.timestamp() >= cut]


def validate_crossref(
    citations: list[Citation],
    grappe_id: str,
    is_member: Callable[[str], bool],
    weight: Callable[[str], float],
    rule: CrossRefRule,
) -> dict[str, ValidationRecord]:
    """Validation par recoupement pour une grappe. Un citant = une voix ; un record par
    élément cité (y compris les refus, avec leurs raisons). `is_member` reflète l'état de
    l'itération précédente : un élément validé ici ne sert pas de citant dans la même passe."""
    by_cited: dict[str, set[str]] = {}
    for c in citations:
        if c.citer != c.cited:  # auto-citations ignorées
            by_cited.setdefault(c.cited, set()).add(c.citer)
    out: dict[str, ValidationRecord] = {}
    for cited in sorted(by_cited):
        raw = by_cited[cited]
        citers = tuple(sorted(x for x in raw if is_member(x)))
        ecos = tuple(sorted({x.split(":", 1)[0] for x in citers}))
        wsum = round(sum(weight(x) for x in citers), 6)
        reasons: list[str] = []
        if len(citers) < rule.min_citers:
            reasons.append(f"citants membres {len(citers)} < {rule.min_citers}")
        if len(ecos) < rule.min_ecosystems:
            reasons.append(f"écosystèmes {len(ecos)} < {rule.min_ecosystems}")
        if wsum < rule.min_weight_sum:
            reasons.append(f"poids {wsum:g} < {rule.min_weight_sum:g}")
        if len(raw) > len(citers):
            reasons.append(f"{len(raw) - len(citers)} citant(s) non membres ignorés")
        validated = not any("<" in r for r in reasons)
        if validated:
            reasons.insert(0, "validé : seuils atteints")
        out[cited] = ValidationRecord(
            cited, grappe_id, citers, ecos, wsum, validated, tuple(reasons)
        )
    return out
