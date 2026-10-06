"""Citations et recoupement (le recoupement lui-même arrive en phase 4)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from grappes.canon import canonical_domain
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

    Les liens sont rattachés au domaine (`web:domaine`). Tri stable pour la reproductibilité.
    """
    out: dict[tuple[str, str, str], Citation] = {}
    for o in observations:
        cited_keys = [m.key for m in o.mentions]
        cited_keys += [f"web:{d}" for d in (canonical_domain(u) for u in o.links) if d]
        for cited in cited_keys:
            if cited == o.source.key:
                continue
            out.setdefault(
                (o.source.key, cited, o.obs_id),
                Citation(o.source.key, cited, o.source.ecosystem, o.obs_id, o.ts),
            )
    return [out[k] for k in sorted(out)]
