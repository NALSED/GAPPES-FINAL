"""Fetcher Telegram (schéma d'entrée minimal : voir docs/conception/formats_json.md)."""

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
class TelegramFetcher(BaseFetcher):
    ecosystem = "telegram"

    def parse(self, raw: Mapping[str, Any]) -> Iterable[Observation]:
        if not isinstance(raw, Mapping):
            raise FetcherError("enregistrement non objet")
        channel = raw.get("channel")
        if not isinstance(channel, str) or not canonical_handle(channel):
            raise FetcherError("canal manquant")
        native_id = str(raw.get("message_id", ""))
        text = raw.get("text")
        text = text if isinstance(text, str) else ""
        if not native_id and not text:
            raise FetcherError("ni message_id ni texte")

        mention_handles = list(extract_mentions(text))
        fwd = raw.get("forwarded_from")
        if isinstance(fwd, str) and canonical_handle(fwd):
            mention_handles.append(fwd)
        urls = []
        for e in raw.get("entities") or []:
            if isinstance(e, Mapping):
                if e.get("type") == "mention" and isinstance(e.get("text"), str):
                    mention_handles.append(e["text"])
                elif e.get("type") in ("url", "text_link"):
                    url = e.get("url") or e.get("text")
                    if isinstance(url, str) and url.strip():
                        urls.append(canonical_url(url))
        source = SourceRef("telegram", canonical_handle(channel))
        yield Observation(
            obs_id=make_obs_id("telegram", f"{source.ident}/{native_id}", text),
            source=source,
            ts=parse_ts(raw.get("date")),
            text=text,
            mentions=dedup(
                SourceRef("telegram", h) for h in map(canonical_handle, mention_handles) if h
            ),
            links=dedup(u for u in urls if u),
            hashtags=dedup(extract_hashtags(text)),
            engagement=to_int(raw.get("views")) + to_int(raw.get("reactions")),
            raw_ref=f"{source.ident}/{native_id}" if native_id else None,
        )
