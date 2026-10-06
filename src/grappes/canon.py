"""Canonicalisation des URLs, handles et domaines. Aucune résolution réseau."""

from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

_TRACKING_PARAMS = {"fbclid"}


def canonical_handle(handle: str) -> str:
    """Minuscules, sans `@` initial."""
    return handle.strip().lstrip("@").casefold()


def canonical_domain(host: str) -> str:
    """Hôte seul, minuscules, sans `www.` ni port."""
    h = host.strip().casefold()
    if "//" in h:
        h = urlsplit(h).hostname or ""
    h = h.split("/", 1)[0].split(":", 1)[0]
    return h.removeprefix("www.")


_TME_HOSTS = {"t.me", "telegram.me"}
_TME_RESERVED = {"joinchat", "c", "s", "addstickers", "share", "iv", "proxy", "socks"}


def telegram_channel(url: str) -> str:
    """Handle du canal pointé par un lien `t.me/<canal>[/<id>]`, sinon chaîne vide.

    Les liens d'invitation (`+...`, `joinchat`) et les chemins réservés ne désignent pas
    un canal public identifiable : ils donnent une chaîne vide.
    """
    url = url.strip()
    if "://" not in url:
        url = "https://" + url
    parts = urlsplit(url)
    if (parts.hostname or "").casefold().removeprefix("www.") not in _TME_HOSTS:
        return ""
    first = parts.path.strip("/").split("/", 1)[0]
    if not first or first.startswith("+") or first.casefold() in _TME_RESERVED:
        return ""
    return canonical_handle(first)


def canonical_url(url: str) -> str:
    """Schéma + hôte en minuscules, sans `www.`, `utm_*`, `fbclid`, fragment ni `/` final."""
    url = url.strip()
    if not url:
        return ""
    if "://" not in url:
        url = "https://" + url
    parts = urlsplit(url)
    host = (parts.hostname or "").casefold().removeprefix("www.")
    if parts.port:
        host = f"{host}:{parts.port}"
    query = [
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if not k.casefold().startswith("utm_") and k.casefold() not in _TRACKING_PARAMS
    ]
    path = parts.path.rstrip("/")
    return urlunsplit((parts.scheme.casefold(), host, path, urlencode(query), ""))
