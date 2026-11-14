"""robots.txt : lu une fois par hôte et par exécution, respecté strictement."""

from __future__ import annotations

from collections.abc import Callable
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser

# fetch(url) -> (statut HTTP ou 0 si erreur réseau, corps[, adresse de redirection])
Fetch = Callable[[str], tuple]
MAX_REDIRECTIONS = 5  # RFC 9309 § 2.3.1.2 : suivre au moins cinq redirections de robots.txt, même vers un autre hôte
MAX_CRAWL_DELAY_S = 60.0  # au-delà, le site demande un rythme que la collecte ne tient pas : il n'est pas visité
_REDIRECTIONS = (301, 302, 303, 307, 308)


class RobotsCache:
    def __init__(self, fetch: Fetch, user_agent: str):
        self._fetch = fetch
        self._token = user_agent.split("/")[0].split()[0] if user_agent.strip() else "*"
        self._cache: dict[tuple[str, str], RobotFileParser | bool] = {}

    def _load(self, scheme: str, netloc: str) -> RobotFileParser | bool:
        url = f"{scheme}://{netloc}/robots.txt"
        status, body = 0, b""
        for _ in range(MAX_REDIRECTIONS + 1):
            status, body, *reste = self._fetch(url)
            cible = str(reste[0]) if reste and reste[0] else ""
            if status not in _REDIRECTIONS or not cible:
                break
            # `exemple.org/robots.txt` renvoie très souvent vers `www.exemple.org` ou vers https : sans suivre, tout le
            # site passait pour interdit et aucune de ses pages n'était lue
            try:
                url = urljoin(url, cible)
            except ValueError:
                return False
            if urlsplit(url).scheme not in ("http", "https"):
                return False
        if status in (404, 410):
            return True  # pas de robots.txt : rien n'est interdit
        if status == 200:
            rp = RobotFileParser()
            rp.parse(body.decode("utf-8", "replace").splitlines())
            return rp
        return False  # 401/403/429/5xx/erreur : par prudence, on ne visite pas cet hôte

    def check(self, url: str) -> tuple[bool, float]:
        """(autorisé ?, délai demandé en secondes par `Crawl-delay`)."""
        parts = urlsplit(url)
        key = (parts.scheme, parts.netloc)
        if key not in self._cache:
            self._cache[key] = self._load(*key)
        rp = self._cache[key]
        if rp is True:
            return True, 0.0
        if rp is False:
            return False, 0.0
        delay = float(rp.crawl_delay(self._token) or rp.crawl_delay("*") or 0)
        if delay > MAX_CRAWL_DELAY_S:  # respecté en ne visitant pas, jamais en dormant des heures verrou tenu
            return False, 0.0
        return rp.can_fetch(self._token, url), delay
