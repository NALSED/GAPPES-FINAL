"""Construction d'un `Candidate` nettoyé à partir d'un élément brut de réponse."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from grappes.canon import canonical_handle, link_target
from grappes.search.models import Candidate
from grappes.search.paths import resolve_field
from grappes.search.safe import bounded_extra, clean_date, clean_text, clean_url


def build_candidate(
    provider: str, keyword: str, item: Any, fields: Mapping[str, Any], options: Mapping[str, Any]
) -> Candidate | None:
    """`None` si l'élément ne permet d'identifier aucun candidat (ni URL, ni identifiant)."""
    if not isinstance(item, (Mapping, str)):
        return None
    if isinstance(item, str):  # élément scalaire : l'URL elle-même
        item = {"valeur": item}
        fields = {"url": "valeur", "title": "valeur"}
    url = clean_url(resolve_field(item, fields.get("url")))
    title = clean_text(resolve_field(item, fields.get("title")))
    description = clean_text(resolve_field(item, fields.get("description")))
    native = clean_text(resolve_field(item, fields.get("id")), 200)
    key = link_target(url) if url else ""
    if key:
        ecosystem, ident = key.split(":", 1)
    elif url:
        ecosystem, ident = "inconnu", url  # cible non identifiable (invitation, publication...)
    elif native:
        ecosystem = clean_text(options.get("ecosystem"), 40) or "inconnu"
        ident = canonical_handle(native) or native
    else:
        return None
    reason = clean_text(
        str(options.get("raison") or "résultat de recherche pour « {mot_cle} »")
        .replace("{mot_cle}", keyword)
        .replace("{fournisseur}", provider),
        200,
    )
    text = ". ".join(t for t in (title, description) if t)
    return Candidate(
        ecosystem=ecosystem,
        ident=ident,
        url=url,
        keyword=keyword,
        provider=provider,
        reason=reason,
        date=clean_date(resolve_field(item, fields.get("date"))),
        text=text,
        extra=bounded_extra(item),
    )
