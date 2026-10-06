"""Fetcher web (schéma d'entrée minimal : voir docs/conception/formats_json.md)."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from grappes.canon import canonical_domain, canonical_url
from grappes.ingestion.base import (
    BaseFetcher,
    FetcherError,
    dedup,
    make_obs_id,
    parse_ts,
    register,
)
from grappes.models import Observation, SourceRef


@register
class WebFetcher(BaseFetcher):
    ecosystem = "web"

    def parse(self, raw: Mapping[str, Any]) -> Iterable[Observation]:
        if not isinstance(raw, Mapping):
            raise FetcherError("enregistrement non objet")
        url = raw.get("url")
        if not isinstance(url, str) or not canonical_domain(canonical_url(url)):
            raise FetcherError("url manquante")
        page_url = canonical_url(url)
        domain = canonical_domain(page_url)
        title = raw.get("title") if isinstance(raw.get("title"), str) else ""
        body = raw.get("text") if isinstance(raw.get("text"), str) else ""
        text = f"{title}\n{body}".strip()
        links = [canonical_url(u) for u in raw.get("outlinks") or [] if isinstance(u, str)]
        yield Observation(
            obs_id=make_obs_id("web", page_url, text),
            source=SourceRef("web", domain),
            ts=parse_ts(raw.get("fetched_at")),
            text=text,
            links=dedup(u for u in links if u and canonical_domain(u) != domain),
            raw_ref=page_url,
            meta={"page_url": page_url},
        )
