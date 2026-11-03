"""RSSHub (3.8.10) : transforme l'adresse d'un site sans flux RSS natif en adresse de flux RSS, via une instance
RSSHub auto-hébergée (`suite.rsshub_url` dans `pilote.yaml`) — projet libre existant, pas réinventé. Le flux
obtenu est ensuite suivi exactement comme un flux RSS ajouté à la main (`flux_rss.py`).

Contrat RSSHub non vérifié dans ce bac à sable (aucune instance accessible ici) : RSSHub expose des routes
PROPRES à chaque site (`/twitter/user/x`, `/github/issue/...`), pas un point d'entrée générique « transforme
cette adresse ». La fonction ci-dessous suppose une route de la forme `{rsshub_url}/site/<domaine>` — à
confirmer (ou corriger) une fois une vraie instance posée ; voir QUESTIONS.md."""

from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.request

DELAI_S = 20


def route_pour(site: str) -> str:
    """Le chemin RSSHub supposé pour transformer `site` — à vérifier contre une vraie instance (voir le docstring
    du module)."""
    domaine = urllib.parse.urlsplit(site if "//" in site else f"//{site}").netloc or site
    return f"/site/{domaine}"


def resoudre(rsshub_url: str, site: str) -> str:
    """L'adresse du flux RSS produit par RSSHub pour `site`. Lève OSError si l'instance ne répond pas,
    ValueError si elle ne connaît aucune route pour ce site (limite connue de RSSHub, pas un bug de grappes)."""
    url = rsshub_url.rstrip("/") + route_pour(site)
    req = urllib.request.Request(url, headers={"User-Agent": "pilote/0.1 (RSSHub)"})
    try:
        with urllib.request.urlopen(req, timeout=DELAI_S) as r:
            if r.status == 404:
                raise ValueError(f"RSSHub ne connaît pas de route pour « {site} ».")
            r.read(1)  # juste vérifier que l'adresse répond ; flux_rss.py la relira pour de vrai
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise ValueError(f"RSSHub ne connaît pas de route pour « {site} ».") from exc
        raise OSError(f"RSSHub a répondu une erreur ({exc.code}).") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise OSError("L'instance RSSHub ne répond pas.") from exc
    return url
