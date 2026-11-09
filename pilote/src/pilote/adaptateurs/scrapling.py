"""Scrapling (spec 906, complété en 908/5.2) : scraping auto-hébergé et gratuit (licence BSD-3, bibliothèque
`scrapling[fetchers]`, dépendance optionnelle de pilote — `pip install "pilote[scrapling]"`). Deux moyens
d'accès : le client HTTP à empreinte TLS de navigateur (`Fetcher`, par défaut), et le navigateur furtif
(`StealthyFetcher`, `parametres.navigateur: true`) pour les pages dont les résultats n'arrivent qu'en
JavaScript ou sont protégées — plus lourd, choisi PAR SOURCE, jamais le cas général. Rejoint la famille
« prestataire de collecte » (même famille qu'Apify/Bright Data/ZenRows) mais sans clé ni coût : pas soumis au
plafond de budget.

Convention identique à `api_json.py`, en HTML au lieu de JSON : `url` (l'adresse SANS les mots cherchés —
{quoi} etc. n'y sont tolérés que hors paramètres, ex. un chemin), `params` (valeurs avec {quoi}, {mots_cles},
{lieu}, {mots_et_lieu}, {limite}, {pays} — toujours ENCODÉES dans l'adresse, jamais collées dans le texte),
`liste` (sélecteur CSS d'un résultat), `champs` (sélecteurs CSS RELATIFS à un résultat — `::text` pour du
texte, `::attr(href)` pour un attribut), `genre`, `origine_texte`, `site_prefixe` (adresse à placer devant un
`site` qui n'est qu'un lien relatif, même convention qu'api_json).

`parametres.lire_site: true` (5.2 c, rôle ENRICHIR) : change complètement ce qui est lu — pas une recherche
dans une liste de résultats (`liste`/{quoi}), mais LA PROPRE PAGE d'un candidat déjà trouvé (`entree.site`),
pour en tirer ce qu'elle porte (ville, site, numéro, un « detail » libre — ex. une description de page). Une
seule fiche en sortie, jamais une liste ; un site absent ou en panne ne fait pas échouer la vérification, elle
rend juste rien (règle d'ENRICHIR : compléter, ne jamais faire échouer la recherche pour autant)."""

from __future__ import annotations

from typing import Any

from pilote.adaptateurs import Client, ErreurSource, mots_significatifs
from pilote.adaptateurs.mcp_generique import remplir

LIT_PARAMETRES = True  # adaptateur générique (fiche 11, niveau 2) : sa lecture dépend des réglages (`liste`, `champs`) de la source


def _champ(resultat: Any, selecteur: str) -> str:
    """Un sélecteur CSS relatif à un résultat (toujours avec `::text` ou `::attr(nom)` : convention de Scrapling
    et de CSS, jamais devinée ici). `::text` joint tous les nœuds de texte trouvés ; `::attr(...)` rend le premier."""
    if not selecteur:
        return ""
    trouve = resultat.css(selecteur)
    if not trouve:
        return ""
    if selecteur.rstrip().endswith("::text"):
        return " ".join(t.strip() for t in trouve.getall() if t.strip())
    return str(trouve.get() or "").strip()


def convertir(page: Any, parametres: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """`page` : le résultat de `Fetcher.get()`/`StealthyFetcher.fetch()`, ou directement le HTML (texte) d'un
    exemple enregistré (fiche 11, niveau 2) — les deux se parcourent au CSS pareil, une fois le texte passé par
    `scrapling.parser.Selector`."""
    p = parametres or {}
    if isinstance(page, (str, bytes)):
        from scrapling.parser import Selector

        page = Selector(page.decode("utf-8", "replace") if isinstance(page, bytes) else page)
    champs = p.get("champs") or {}
    genre = str(p.get("genre") or "")
    origine = str(p.get("origine_texte") or "Scrapling (scraping auto-hébergé)")
    if p.get("lire_site"):
        # 5.2 c : LA page entière est la fiche (pas une liste de résultats) — aucun champ n'est obligatoire,
        # une page qui ne porte rien d'exploitable rend juste rien (jamais une erreur : ENRICHIR ne doit pas
        # faire échouer la vérification d'un candidat).
        e: dict[str, Any] = {}
        for k in ("nom", "ville", "site", "pays", "numero", "detail"):
            if k in champs:
                v = _champ(page, str(champs[k]))
                if v:
                    e[k] = v
        if not e:
            return []
        e["origine"] = origine
        if genre:
            e["genre"] = genre
        return [e]
    if "nom" not in champs:
        raise ErreurSource("Cette source ne dit pas quel sélecteur CSS contient le nom.")
    liste = str(p.get("liste", "")).strip()
    if not liste:
        raise ErreurSource("Cette source ne dit pas le sélecteur CSS d'un résultat.")
    out: list[dict[str, Any]] = []
    for resultat in page.css(liste):
        nom = _champ(resultat, str(champs["nom"]))
        if not nom:
            continue
        e: dict[str, Any] = {"nom": nom, "origine": origine}
        for k in ("ville", "site", "pays", "numero"):
            if k in champs:
                v = _champ(resultat, str(champs[k]))
                if v:
                    e[k] = v
        if e.get("site") and p.get("site_prefixe") and not e["site"].startswith(("http://", "https://")):
            e["site"] = str(p["site_prefixe"]) + e["site"]  # le résultat ne donne qu'une adresse relative (lien interne) : la page le préfixe, même convention qu'api_json
        if genre:
            e["genre"] = genre
        out.append(e)
    return out


def _page(url: str, navigateur: bool, timeout_s: float) -> Any:
    """Lit `url` par le client HTTP à empreinte TLS (par défaut) ou le navigateur furtif (5.2 a, `navigateur: true`
    — Chromium déjà installé pour les tests de `/suite`, pas une nouvelle dépendance)."""
    try:
        if navigateur:
            from scrapling.fetchers import StealthyFetcher

            return StealthyFetcher.fetch(url, headless=True, timeout=int(timeout_s * 1000))
        from scrapling.fetchers import Fetcher

        return Fetcher.get(url, timeout=timeout_s)
    except ImportError as exc:
        raise ErreurSource(
            "Scrapling n'est pas installé sur cette machine : `pip install \"pilote[scrapling]\"` (spec 906)."
        ) from exc
    except Exception as exc:  # Scrapling lève ses propres exceptions (curl_cffi, Playwright, réseau) : toutes rendues en français
        raise ErreurSource(f"Scrapling n'a pas pu lire la page : {exc}") from exc


def chercher(entree: dict[str, Any], client: Client, parametres: dict[str, Any]) -> list[dict[str, Any]]:
    navigateur = bool(parametres.get("navigateur"))
    if parametres.get("lire_site"):
        # 5.2 c (rôle ENRICHIR) : pas une recherche par mot, la propre page d'un candidat déjà trouvé. Un site
        # absent ou en panne ne fait jamais échouer la vérification — elle ne rend juste rien pour ce candidat.
        url_remplie = str(entree.get("site") or "").strip()
        if not url_remplie:
            return []
        client._avant()
        page = _page(url_remplie, navigateur, client.timeout)
        if page.status >= 400:
            return []
        return convertir(page, parametres)
    url = str(parametres.get("url", "")).strip()
    if not url:
        raise ErreurSource("Cette source n'a pas d'adresse.")
    mots = [str(entree.get("quoi", "")).strip(), *map(str, entree.get("mots_cles") or [])]
    quoi = " ".join(m for m in mots if m).strip() or str(entree.get("sujet", "")).strip()
    if not quoi:
        return []
    limite = min(int(entree.get("limite") or 25), 200)
    valeurs = {
        "quoi": quoi, "mots_cles": " ".join(mots_significatifs(quoi)) or quoi, "lieu": str(entree.get("lieu", "")).strip(),
        "sujet": str(entree.get("sujet", "")).strip(), "limite": limite, "pays": str(entree.get("pays") or "").upper(),
        "mots_et_lieu": f"{quoi} {entree.get('lieu', '')}".strip(),
    }  # fmt: skip
    url_remplie = str(remplir(url, valeurs))
    params = {k: v for k, v in remplir(parametres.get("params") or {}, valeurs).items() if v not in ("", None)}
    if params:  # toujours par paramètres encodés, jamais collés dans le texte de l'adresse (un mot cherché peut avoir une espace ou un « & »)
        import urllib.parse

        url_remplie += ("&" if "?" in url_remplie else "?") + urllib.parse.urlencode(params)
    client._avant()  # pas d'appel HTTP par `client` lui-même (Scrapling fait sa propre requête) : juste l'arrêt et le journal, comme `Client.mcp()`
    page = _page(url_remplie, navigateur, client.timeout)
    if page.status >= 400:
        erreur = ErreurSource(f"La page a répondu une erreur ({page.status}).")
        erreur.code = page.status
        raise erreur
    return convertir(page, parametres)[:limite]
