"""Fetcher Telegram : export Telegram Desktop (`messages`) et enregistrement plat historique.

Formats : voir docs/conception/formats_json.md.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any

from grappes.canon import canonical_handle, canonical_url
from grappes.ingestion.base import (
    BaseFetcher,
    FetcherError,
    Skip,
    dedup,
    extract_hashtags,
    extract_mentions,
    make_obs_id,
    parse_ts,
    register,
    to_int,
)
from grappes.models import Observation, SourceRef

_NON_WORD = re.compile(r"[^\w]+", re.UNICODE)


def channel_ident(name: str) -> str:
    """Identifiant canonique d'un canal : `@nom_public` tel quel, sinon le nom affiché mis en
    forme (minuscules, espaces et ponctuation -> `_`).

    L'export Telegram Desktop ne donne que le nom affiché (D25) : la mise en forme du nom est
    une heuristique documentée, à confirmer sur de vrais exports (Q16).
    """
    name = name.strip()
    if name.startswith("@"):
        return canonical_handle(name)
    return _NON_WORD.sub("_", name.casefold()).strip("_")


def _flatten(text: Any) -> str:
    """`text` de l'export : chaîne, ou liste de chaînes et d'objets `{type, text}`."""
    if isinstance(text, str):
        return text
    if isinstance(text, list):
        return "".join(
            p if isinstance(p, str) else str(p.get("text", ""))
            for p in text
            if isinstance(p, (str, Mapping))
        )
    return ""


@register
class TelegramFetcher(BaseFetcher):
    ecosystem = "telegram"

    def unwrap(self, doc: Any) -> list[Any]:
        """Export d'un canal : `{name, type, id, messages: [...]}` -> un enregistrement par
        message, le canal étant celui de l'export."""
        if not (isinstance(doc, Mapping) and isinstance(doc.get("messages"), list)):
            return [doc]
        raw_name = doc.get("username") or doc.get("name")
        channel = channel_ident(raw_name) if isinstance(raw_name, str) else ""
        return [
            {**m, "channel": channel, "_chat_name": doc.get("name")}
            if isinstance(m, Mapping) and channel
            else m
            for m in doc["messages"]
        ]

    def parse(self, raw: Mapping[str, Any]) -> Iterable[Observation]:
        if not isinstance(raw, Mapping):
            raise FetcherError("enregistrement non objet")
        if raw.get("type") == "service":
            raise Skip  # création du canal, épinglage... : aucun texte à analyser
        channel = raw.get("channel")
        if not isinstance(channel, str) or not channel_ident(channel):
            raise FetcherError("canal manquant")
        native_id = str(raw.get("message_id", raw.get("id", "")))
        text = _flatten(raw.get("text"))
        if not text and isinstance(raw.get("text_entities"), list):
            text = _flatten(raw["text_entities"])
        if not native_id and not text:
            raise FetcherError("ni identifiant ni texte")

        entities = raw.get("text_entities") or raw.get("entities")
        if not isinstance(entities, list):
            entities = raw["text"] if isinstance(raw.get("text"), list) else []
        mention_handles = list(extract_mentions(text))
        urls: list[str] = []
        for e in entities:
            if not isinstance(e, Mapping):
                continue
            kind = e.get("type")
            if kind == "mention" and isinstance(e.get("text"), str):
                mention_handles.append(e["text"])
            elif kind in ("link", "url"):
                url = e.get("url") or e.get("text")
                if isinstance(url, str) and url.strip():
                    urls.append(canonical_url(url))
            elif kind == "text_link":  # l'URL est dans `href` (à confirmer, Q16) ou `url`
                url = e.get("href") or e.get("url")
                if isinstance(url, str) and url.strip():
                    urls.append(canonical_url(url))
        fwd = raw.get("forwarded_from")
        if isinstance(fwd, str) and channel_ident(fwd):
            mention_handles.append(fwd if fwd.startswith("@") else channel_ident(fwd))

        source = SourceRef("telegram", channel_ident(channel))
        yield Observation(
            obs_id=make_obs_id("telegram", f"{source.ident}/{native_id}", text),
            source=source,
            ts=parse_ts(raw.get("date_unixtime")) or parse_ts(raw.get("date")),
            text=text,
            mentions=dedup(
                SourceRef("telegram", h) for h in (channel_ident(m) for m in mention_handles) if h
            ),
            links=dedup(u for u in urls if u),
            hashtags=dedup(extract_hashtags(text)),
            engagement=to_int(raw.get("views")) + to_int(raw.get("reactions")),
            raw_ref=f"{source.ident}/{native_id}" if native_id else None,
            meta=(
                {"nom": raw["_chat_name"].strip()}
                if isinstance(raw.get("_chat_name"), str) and raw["_chat_name"].strip()
                else {}
            ),
        )
