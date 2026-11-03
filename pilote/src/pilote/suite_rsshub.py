"""RSSHub (3.8.10) : transforme l'adresse d'un site sans flux RSS natif en adresse de flux RSS, via une instance
RSSHub auto-hébergée (`suite.rsshub_url` dans `pilote.yaml`) — projet libre existant, pas réinventé. Le flux
obtenu est ensuite suivi exactement comme un flux RSS ajouté à la main (`flux_rss.py`, `moteur_sources.definition_flux`).

Contrat vérifié contre une vraie instance (image Docker officielle, 03/11/2026) : RSSHub n'a PAS de point d'entrée
« transforme cette adresse ». Il publie ses règles « Radar » (`/api/radar/rules` : domaine -> sous-domaine -> motifs
de chemin -> route), celles qu'utilise l'extension RSSHub Radar ; on y cherche la route de l'adresse donnée, puis on
lit le flux une fois pour vérifier qu'il rend des articles. Les lectures passent par `flux_rss.telecharger` et
`flux_rss.lire_flux` : rien de dupliqué."""

from __future__ import annotations

import json
import re
import urllib.parse
from typing import Any

from pilote import flux_rss
from pilote.refus import ConfigRefusee


def identifiant(site: str) -> str:
    """Identifiant de la prise de grappes qui suit le flux RSSHub d'un site : tiré du SITE (l'adresse du flux est celle
    de l'instance, 127.0.0.1, qui ne dit rien), lisible dans le journal ; `nom_prise` en tire le nom affiché."""
    return "rsshub-" + flux_rss.identifiant(site if "//" in site else f"https://{site}").removeprefix("rss-")


def nom_prise(ident: str) -> str | None:
    """« rsshub-www-lemonde-fr-1a2b3c » -> « RSSHub (www.lemonde.fr) » ; None si ce n'est pas une prise RSSHub."""
    if not ident.startswith("rsshub-"):
        return None
    hote = ident.removeprefix("rsshub-").rsplit("-", 1)[0].replace("-", ".")
    return f"RSSHub ({hote})"


def regles(rsshub_url: str) -> dict[str, Any]:
    """Les règles Radar de l'instance. Lève OSError si elle ne répond pas ou rend autre chose que ces règles."""
    try:
        d = json.loads(flux_rss.telecharger(rsshub_url.rstrip("/") + "/api/radar/rules"))
    except ConfigRefusee as exc:
        raise OSError(f"L'instance RSSHub ne répond pas ({exc}).") from exc
    except ValueError as exc:
        raise OSError("L'instance RSSHub n'a pas rendu ses règles Radar.") from exc
    if not isinstance(d, dict):
        raise OSError("L'instance RSSHub n'a pas rendu ses règles Radar.")
    return d


def _motif(source: str) -> tuple[re.Pattern[str], list[str]] | None:
    """Motif de chemin RSSHub (« /:user/:repo », « /:id? », « /* ») -> expression régulière et noms des paramètres."""
    if not source.startswith("/"):
        return None
    noms: list[str] = []
    expr = ""
    for seg in [s for s in source.split("/") if s]:
        if not seg.startswith(":") and ("?" in seg or ":" in seg):
            return None  # motif avec requête ou paramètre collé (« /search?q=:q », « /a-:b ») : pas pris en charge, ignoré
        if seg == "*":
            expr += r"(?:/.*)?"
        elif seg.startswith(":"):
            optionnel = seg.endswith("?")
            noms.append(seg[1:].rstrip("?"))
            g = rf"/(?P<p{len(noms) - 1}>[^/]+)"
            expr += f"(?:{g})?" if optionnel else g
        else:
            expr += "/" + re.escape(seg)
    return re.compile(rf"^{expr}/?$"), noms


def _remplir(cible: str, valeurs: dict[str, str]) -> str | None:
    """La route cible avec ses paramètres ; None si un paramètre obligatoire manque."""
    out = []
    for seg in [s for s in cible.split("/") if s]:
        if seg.startswith(":"):
            nom = seg[1:].rstrip("?")
            if valeurs.get(nom):
                out.append(urllib.parse.quote(valeurs[nom], safe=""))
            elif not seg.endswith("?"):
                return None
        else:
            out.append(seg)
    return "/" + "/".join(out)


def routes(regles_: dict[str, Any], site: str) -> list[dict[str, str]]:
    """Les routes RSSHub qui correspondent à l'adresse `site`, dans l'ordre des règles : [{titre, route}]."""
    u = urllib.parse.urlsplit(site.strip() if "//" in site else f"https://{site.strip()}")
    hote = (u.hostname or "").lower()
    etiquettes = hote.split(".")
    for i in range(len(etiquettes) - 1):  # le domaine connu le plus long (« www.lemonde.fr » -> « lemonde.fr »)
        domaine = ".".join(etiquettes[i:])
        if domaine in regles_:
            break
    else:
        return []
    sous = hote[: -len(domaine)].rstrip(".") or "."
    entree = regles_[domaine]
    lot = entree.get(sous) or (entree.get(".") if sous == "www" else None) or []
    chemin = urllib.parse.unquote(u.path) or "/"
    out = []
    for r in lot:
        cible = r.get("target")
        if not isinstance(cible, str):
            continue
        for source in r.get("source") or []:
            m = _motif(source) if isinstance(source, str) else None
            if not m or not (trouve := m[0].match(chemin)):
                continue
            route = _remplir(cible, {nom: trouve.group(f"p{k}") or "" for k, nom in enumerate(m[1])})
            if route and not any(x["route"] == route for x in out):
                out.append({"titre": str(r.get("title", "")), "route": route})
            break
    return out


def resoudre(rsshub_url: str, site: str) -> dict[str, Any]:
    """Le flux RSSHub de `site`, lu une fois : {url, titre, articles, format}. Lève OSError si l'instance ne répond
    pas, ValueError si RSSHub ne connaît pas de route pour ce site ou si aucune ne rend d'article (limite connue de
    RSSHub, dite clairement, jamais un échec silencieux)."""
    trouvees = routes(regles(rsshub_url), site)
    if not trouvees:
        raise ValueError(f"RSSHub ne connaît pas de route pour « {site} ».")
    raisons = []
    for r in trouvees:
        url = rsshub_url.rstrip("/") + r["route"]
        try:
            format_, articles = flux_rss.lire_flux(flux_rss.telecharger(url, delai_s=60))
        except (ConfigRefusee, ValueError) as exc:
            raisons.append(f"{r['route']} : {exc}")
            continue
        if articles:
            return {"url": url, "titre": r["titre"], "articles": len(articles), "format": format_}
        raisons.append(f"{r['route']} : aucun article")
    raise ValueError(f"RSSHub connaît « {site} », mais aucune de ses routes n'a rendu d'article ({' ; '.join(raisons)[:300]}).")
