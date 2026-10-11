"""Collecte et ingestion automatique (FINAL.md §§ 6 et 7).

Pour chaque sujet : la multiprise de recherche rapporte des candidats ; un candidat est ingéré
automatiquement s'il est **public**, respecte les règles générales de visite, n'est pas dans les
**INTERDITS** et atteint une **proximité minimale** avec un sujet. Pas de validation humaine.
Profondeur d'exploration et nombres de requêtes, de pages, de nouvelles sources et d'observations par
cycle sont plafonnés. Le recoupement continue de décider : une source non recoupée reste « probable »
au mieux. Les réseaux sociaux ne sont jamais lus (leurs liens sont des citations).
"""

from __future__ import annotations

from collections import Counter, deque
from collections.abc import Callable
from dataclasses import dataclass, field, replace

from grappes.autonomy import Autonomy
from grappes.canon import canonical_domain, canonical_url, link_target
from grappes.config import Config
from grappes.fetch import PageFetcher
from grappes.ingestion import get_fetcher
from grappes.models import Grappe
from grappes.search.config import SearchConfig
from grappes.search.engine import run_search
from grappes.semantic.scoring import score_proximity
from grappes.storage.db import Database

MAX_PAGES_PER_DOMAIN = 5  # par cycle : explorer un site, pas l'aspirer
TOP_TERMS = 4  # termes du lexique ajoutés à la phrase comme mots-clés de recherche


@dataclass(slots=True)
class Ingested:
    url: str
    domain: str
    subject: str  # identifiant de la grappe du sujet
    score: float
    depth: int
    new_source: bool


@dataclass(slots=True)
class CollectReport:
    dry_run: bool = False
    requests: int = 0
    candidates: int = 0
    pages_attempted: int = 0
    observations_new: int = 0
    ingested: list[Ingested] = field(default_factory=list)
    refused: Counter = field(default_factory=Counter)  # motif -> nombre
    providers: dict[str, str] = field(default_factory=dict)
    blocked_domains: list[str] = field(default_factory=list)
    skipped_subjects: list[str] = field(default_factory=list)
    stopped: bool = False

    @property
    def new_sources(self) -> list[str]:
        return [i.domain for i in self.ingested if i.new_source]


def lexicon_terms(g: Grappe) -> dict[str, float]:
    return {**g.lexicon.terms, **{k: -v for k, v in g.lexicon.negative.items()}}


def proximity(text: str, grappe: Grappe) -> float:
    """Proximité (0 à 100) d'un texte avec le lexique d'un sujet : même fonction que le scoring."""
    return score_proximity(text, lexicon_terms(grappe), scale=grappe.scale) if text.strip() else 0.0


def best_subject(text: str, subjects: list[Grappe]) -> tuple[Grappe | None, float]:
    best: tuple[Grappe | None, float] = (None, 0.0)
    for g in subjects:
        s = proximity(text, g)
        if s > best[1]:
            best = (g, s)
    return best


def collect(
    db: Database,
    cfg: Config,
    scfg: SearchConfig,
    auto: Autonomy,
    fetcher: PageFetcher,
    *,
    execute: bool,
    should_stop: Callable[[], bool] = lambda: False,
    log: bool = True,
    search_kwargs: dict | None = None,
) -> CollectReport:
    """Un passage de collecte. `execute` faux : aucun appel, rien d'écrit (dry-run)."""
    rep = CollectReport(dry_run=not execute)
    subjects = [g for g in cfg.grappes if g.subject]
    ready = [g for g in subjects if g.lexicon.terms]
    rep.skipped_subjects = [g.grappe_id for g in subjects if not g.lexicon.terms]
    if not execute or not ready:
        return rep

    # 1. recherche : phrase + meilleurs termes de chaque sujet, quota de requêtes partagé
    found: dict[str, tuple[float, str, object]] = {}  # url -> (score, id de grappe, candidat)
    used = 0
    for g in ready:
        remaining = max(auto.requetes_par_cycle - used, 0)
        if remaining == 0 or should_stop():
            break
        top = sorted(g.lexicon.terms, key=lambda t: (-g.lexicon.terms[t], t))[:TOP_TERMS]
        res = run_search(
            replace(scfg, quota_total=min(scfg.quota_total, remaining)),
            [g.subject, *top],
            execute=True,
            sujet=g.subject,
            journaliser=log,
            **(search_kwargs or {}),
        )
        used += res.requests
        rep.providers.update(res.status)
        for m in res.raw:  # un candidat par résultat (URL), pas par entité fusionnée
            rep.candidates += 1
            reason = _screen_candidate(m, scfg, fetcher)
            if reason:
                rep.refused[reason] += 1
                continue
            owner, score = best_subject(m.text, ready)
            if owner is None or score < auto.seuil_ingestion:
                rep.refused["proximité insuffisante avec les sujets"] += 1
                continue
            if m.url not in found or score > found[m.url][0]:
                found[m.url] = (score, owner.grappe_id, m)
    rep.requests = used

    # 2. récupération et ingestion, du plus proche au moins proche, jusqu'aux plafonds
    known_sources = {
        r[0] for r in db.conn.execute("SELECT ident FROM sources WHERE ecosystem='web'")
    }
    queue: deque[tuple[float, str, int]] = deque(
        (score, url, 0)
        for url, (score, _gid, _m) in sorted(found.items(), key=lambda kv: -kv[1][0])
    )
    web = get_fetcher("web")
    seen_urls: set[str] = set()
    per_domain: Counter = Counter()
    new_domains: set[str] = set()
    while queue:
        if should_stop():
            rep.stopped = True
            break
        if rep.pages_attempted >= auto.pages_par_cycle:
            rep.refused["plafond de pages par cycle atteint"] += len(queue)
            break
        if rep.observations_new >= auto.elements_par_cycle:
            rep.refused["plafond d'observations par cycle atteint"] += len(queue)
            break
        _, url, depth = queue.popleft()
        key = canonical_url(url)
        if key in seen_urls:
            continue
        seen_urls.add(key)
        domain = canonical_domain(key)
        if db.conn.execute("SELECT 1 FROM observations WHERE raw_ref=?", (key,)).fetchone():
            rep.refused["page déjà ingérée"] += 1
            continue
        if per_domain[domain] >= MAX_PAGES_PER_DOMAIN:
            rep.refused["plafond de pages par domaine atteint"] += 1
            continue
        is_new = domain not in known_sources and domain not in new_domains
        if is_new and len(new_domains) >= auto.nouvelles_sources_par_cycle:
            rep.refused["plafond de nouvelles sources atteint"] += 1
            continue
        rep.pages_attempted += 1
        per_domain[domain] += 1
        res = fetcher.fetch(url)
        if res.domain_blocked:
            rep.blocked_domains.append(domain)
        if not res.ok or res.record is None:
            rep.refused[res.reason or res.status] += 1
            continue
        obs, _ = web.parse_many([res.record])
        if not obs:
            rep.refused["page illisible"] += 1
            continue
        owner, score = best_subject(obs[0].text, ready)
        if owner is None or score < auto.seuil_ingestion:
            rep.refused["page trop éloignée des sujets"] += 1
            continue
        weights = {o.source.key: cfg.sources.weight(o.source.key) for o in obs}
        added = db.add_observations(obs, weights)
        if not added:
            rep.refused["observation déjà connue"] += 1
            continue
        for o in obs:
            db.set_origin(o.source.key, "recherche" if depth == 0 else "exploration")
        rep.observations_new += added
        if is_new:
            new_domains.add(domain)
        rep.ingested.append(Ingested(key, domain, owner.grappe_id, round(score, 2), depth, is_new))
        if depth < auto.profondeur:  # exploration : liens sortants web des pages ingérées
            for link in res.links:
                if link_target(link).startswith("web:") and canonical_url(link) not in seen_urls:
                    queue.append((0.0, link, depth + 1))
    return rep


def _screen_candidate(m, scfg: SearchConfig, fetcher: PageFetcher) -> str | None:
    """Motif de refus d'un candidat avant toute requête, ou `None` s'il peut être visité."""
    if m.ecosystem != "web" or not m.url:
        return "réseau social ou identité sans page : citation seulement, jamais lu"
    spec = scfg.providers.get(m.provider)
    if spec is not None and not spec.public:
        return "fournisseur non public"
    return fetcher.rules.check_url(m.url) or fetcher.rules.check_text(m.text)
