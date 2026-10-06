"""Fetcher X (schéma d'entrée minimal : voir docs/conception/formats_json.md)."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from grappes.canon import canonical_handle, canonical_url
from grappes.ingestion.base import (
    BaseFetcher,
    FetcherError,
    dedup,
    extract_hashtags,
    extract_mentions,
    make_obs_id,
    parse_ts,
    register,
    to_int,
)
from grappes.models import Observation, SourceRef


@register
class XFetcher(BaseFetcher):
    ecosystem = "x"

    def parse(self, raw: Mapping[str, Any]) -> Iterable[Observation]:
        if not isinstance(raw, Mapping):
            raise FetcherError("enregistrement non objet")
        author = raw.get("author")
        handle = author.get("handle") if isinstance(author, Mapping) else author
        if not isinstance(handle, str) or not canonical_handle(handle):
            raise FetcherError("auteur manquant")
        native_id = str(raw.get("id", ""))
        text = raw.get("text")
        text = text if isinstance(text, str) else ""
        if not native_id and not text:
            raise FetcherError("ni id ni texte")

        ent = raw.get("entities") if isinstance(raw.get("entities"), Mapping) else {}
        mention_handles = [
            m.get("handle", "") if isinstance(m, Mapping) else str(m)
            for m in ent.get("mentions") or []
        ] or extract_mentions(text)
        urls = []
        for u in ent.get("urls") or []:
            url = (u.get("expanded_url") or u.get("url")) if isinstance(u, Mapping) else u
            if isinstance(url, str) and url.strip():
                urls.append(canonical_url(url))
        tags = [str(t).lstrip("#").casefold() for t in ent.get("hashtags") or []] or (
            extract_hashtags(text)
        )

        metrics = raw.get("metrics") if isinstance(raw.get("metrics"), Mapping) else {}
        engagement = sum(to_int(metrics.get(k)) for k in ("likes", "retweets", "replies"))
        source = SourceRef("x", canonical_handle(handle))
        meta = {"lang": str(raw["lang"])} if raw.get("lang") else {}
        yield Observation(
            obs_id=make_obs_id("x", native_id, text),
            source=source,
            ts=parse_ts(raw.get("created_at")),
            text=text,
            mentions=dedup(SourceRef("x", h) for h in map(canonical_handle, mention_handles) if h),
            links=dedup(u for u in urls if u),
            hashtags=dedup(t for t in tags if t),
            engagement=engagement,
            raw_ref=native_id or None,
            meta=meta,
        )
