"""Score de confiance et affectation aux grappes.

Phase 3 (sémantique seule) : confiance = S. Les composantes E (recoupement) et A (ancrage)
sont à 0 et seront branchées en phase 4 avec la formule complète de MISSION §11.
"""

from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

from grappes.config import Config
from grappes.ecosystem.crossref import Citation, build_citations
from grappes.models import Entity, EntityType, Observation
from grappes.semantic.scoring import score_proximity

NON_CLASSE = "non_classé"
CLASSE = "classé"
AMBIGU = "ambigu"
SECONDAIRE = "secondaire"


@dataclass(slots=True)
class EntityStats:
    ecosystems: set[str] = field(default_factory=set)
    n_observations: int = 0
    citing: set[str] = field(default_factory=set)
    first_seen: datetime | None = None
    last_seen: datetime | None = None

    def see(self, ts: datetime | None) -> None:
        if ts is None:
            return
        if self.first_seen is None or ts < self.first_seen:
            self.first_seen = ts
        if self.last_seen is None or ts > self.last_seen:
            self.last_seen = ts


@dataclass(slots=True)
class AssignResult:
    entities: list[Entity]
    memberships: list[dict]
    stats: dict[str, EntityStats]  # clé = entity_id
    citations: list[Citation]


def entity_id_for(primary_ref: str) -> str:
    return "E-" + hashlib.sha1(primary_ref.encode()).hexdigest()[:12]


def level(confidence: float, cfg: Config) -> str:
    if confidence >= cfg.scoring.niveau_confirme:
        return "confirmé"
    if confidence >= cfg.scoring.niveau_probable:
        return "probable"
    return "faible"


def _top_mean(scores: list[float], n: int) -> float:
    best = sorted(scores, reverse=True)[:n]
    return round(sum(best) / len(best), 2) if best else 0.0


def assign(observations: list[Observation], cfg: Config) -> AssignResult:
    citations = build_citations(observations)
    texts_own: dict[str, list[Observation]] = defaultdict(list)
    for o in observations:
        texts_own[o.source.key].append(o)
    obs_by_id = {o.obs_id: o for o in observations}
    texts_cited: dict[str, list[Observation]] = defaultdict(list)
    stats_by_ref: dict[str, EntityStats] = defaultdict(EntityStats)

    for ref, obs_list in texts_own.items():
        st = stats_by_ref[ref]
        st.ecosystems.add(ref.split(":", 1)[0])
        for o in obs_list:
            st.n_observations += 1
            st.see(o.ts)
    for c in citations:
        st = stats_by_ref[c.cited]
        st.ecosystems.add(c.cited.split(":", 1)[0])
        st.citing.add(c.citer)
        texts_cited[c.cited].append(obs_by_id[c.obs_id])
        if c.cited not in texts_own:
            st.see(c.ts)

    entities: list[Entity] = []
    memberships: list[dict] = []
    stats: dict[str, EntityStats] = {}
    for ref in sorted(stats_by_ref):
        eco = ref.split(":", 1)[0]
        etype = EntityType(cfg.scoring.entity_types.get(eco, "person"))
        eid = entity_id_for(ref)
        entities.append(Entity(eid, etype, ref, ref.split(":", 1)[1]))
        stats[eid] = stats_by_ref[ref]
        # texte propre ; à défaut, contexte des citations (jamais de texte inventé, §9.2)
        context = texts_own.get(ref) or texts_cited.get(ref, [])
        scored: list[tuple[str, float]] = []
        for g in cfg.grappes:
            kw = {**g.lexicon.terms, **{k: -v for k, v in g.lexicon.negative.items()}}
            s = _top_mean(
                [score_proximity(o.text, kw, scale=g.scale) for o in context],
                cfg.scoring.top_n_observations,
            )
            scored.append((g.grappe_id, s))
        # meilleure grappe d'abord ; égalité départagée par l'id (déterminisme)
        scored.sort(key=lambda t: (-t[1], t[0]))
        best_id, best = scored[0]
        second = scored[1][1] if len(scored) > 1 else 0.0
        classed = best >= cfg.scoring.seuil_min
        ambiguous = classed and (best - second) < cfg.scoring.marge_ambiguite and second > 0
        for gid, s in scored:
            if s <= 0:
                continue
            if gid == best_id:
                status = (AMBIGU if ambiguous else CLASSE) if classed else NON_CLASSE
            else:
                status = SECONDAIRE
            memberships.append(
                {
                    "entity_id": eid,
                    "grappe_id": gid,
                    "semantic": s,
                    "ecosystem": 0.0,
                    "anchor": 0.0,
                    "confidence": s,
                    "via": "semantique",
                    "status": status,
                }
            )
    return AssignResult(entities, memberships, stats, citations)
