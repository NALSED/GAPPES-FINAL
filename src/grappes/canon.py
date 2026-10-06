"""Canonicalisation des URLs, handles et domaines. Aucune résolution réseau."""

from __future__ import annotations

import re
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
_X_HOSTS = {"x.com", "twitter.com", "mobile.twitter.com"}
_IG_HOSTS = {"instagram.com"}
_SHORTENERS = {"t.co"}  # cible inconnaissable sans résolution réseau : jamais citée
_TME_RESERVED = {"joinchat", "c", "addstickers", "share", "iv", "proxy", "socks", "login"}
_X_RESERVED = {
    "i", "home", "hashtag", "search", "intent", "share", "explore", "settings", "messages",
    "notifications", "compose", "login", "signup", "tos", "privacy", "about", "account",
}  # fmt: skip
_IG_RESERVED = {
    "p", "reel", "reels", "tv", "explore", "stories", "accounts", "direct", "about",
    "developer", "legal", "web",
}  # fmt: skip


def link_target(url: str) -> str:
    """Clé canonique (`ecosysteme:ident`) de l'élément cité par un lien ; `""` si aucun.

    * `t.me/<canal>[/<id>]`, `t.me/s/<canal>` -> `telegram:canal` ;
    * `x.com|twitter.com/<compte>[/...]` -> `x:compte` ;
    * `instagram.com/<compte>` -> `instagram:compte` ;
    * autre site -> `web:domaine`.

    Rien n'est cité (`""`) quand la cible ne peut pas être identifiée sans résolution réseau ni
    ré-identification : invitations Telegram (`t.me/+...`, `joinchat`), messages de groupes
    privés (`t.me/c/...`), publications Instagram (`/p/...`, `/reel/...`), raccourcisseur `t.co`,
    pages d'outils de plateforme (`x.com/i/...`, `x.com/search`...). Aucun lien ne devient donc
    une entité `web:t.me`, `web:x.com` ou `web:instagram.com`.
    """
    url = url.strip()
    if not url:
        return ""
    if "://" not in url:
        url = "https://" + url
    parts = urlsplit(url)
    host = (parts.hostname or "").casefold().removeprefix("www.")
    if not host:
        return ""
    segments = [seg for seg in parts.path.split("/") if seg]
    first = segments[0] if segments else ""
    if host in _SHORTENERS:
        return ""
    if host in _TME_HOSTS:
        if first.casefold() == "s" and len(segments) > 1:  # aperçu web d'un canal public
            first = segments[1]
        if not first or first.startswith("+") or first.casefold() in _TME_RESERVED | {"s"}:
            return ""
        handle = canonical_handle(first)
        return f"telegram:{handle}" if handle else ""
    if host in _X_HOSTS:
        if not first or first.casefold() in _X_RESERVED:
            return ""
        return f"x:{canonical_handle(first)}"
    if host in _IG_HOSTS:
        if not first or first.casefold() in _IG_RESERVED:
            return ""
        return f"instagram:{canonical_handle(first)}"
    return f"web:{host}"


_URL_RE = re.compile(r"https?://[^\s<>\"')\]]+", re.IGNORECASE)


def extract_urls(text: str) -> list[str]:
    """URLs `http(s)://` d'un texte libre (légende, message), sans ponctuation finale."""
    return [u.rstrip(".,;:!?") for u in _URL_RE.findall(text)]


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
