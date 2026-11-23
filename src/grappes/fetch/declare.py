"""Ce qu'une page déclare d'elle-même (spec 914, volet A) : numéro officiel, nom, ville, téléphone, comptes.

Deux sources, toutes deux dans la page téléchargée, sans aucune requête en plus :

* les données structurées schema.org (JSON-LD, microdonnées, RDFa), lues par la bibliothèque `extruct` ;
* les numéros officiels écrits dans le texte, seulement juste après le mot qui les annonce (« SIREN », « SIRET », « RCS »,
  « RNA », « TVA »…). Un SIREN ou un SIRET n'est gardé que si sa clé de contrôle est juste (algorithme de Luhn, celui de
  l'INSEE). Un numéro d'hébergeur (« hébergé par … RCS … ») n'est pas celui du site : il est écarté.

Prudence avant tout : quand la page donne plusieurs numéros différents, ou plusieurs organisations différentes, on ne garde
rien de ce côté-là (on ne sait pas lequel est celui du site). Ce qui est relevé n'est jamais une preuve d'existence : c'est
l'acteur qui parle de lui (spec 914, choix 1)."""

from __future__ import annotations

import json
import logging
import re
import unicodedata
from typing import Any

from grappes.canon import canonical_domain, site_key

log = logging.getLogger(__name__)

LA_POSTE = "356000000"  # SIREN de La Poste : ses SIRET ont un autre contrôle (somme des chiffres multiple de 5)

# types schema.org retenus comme « l'organisation qui publie la page » ; les autres (Event, Product, Person…) sont ignorés
_TYPES_ORG = {
    "organization", "localbusiness", "sportsorganization", "sportsteam", "sportsclub", "ngo", "corporation",
    "educationalorganization", "governmentorganization", "newsmediaorganization", "performinggroup", "musicgroup",
    "medicalorganization", "researchorganization", "workersunion", "politicalparty", "cooperative", "consortium",
    "onlinebusiness", "fundingscheme", "librarysystem", "store", "restaurant", "hotel", "project",
}  # fmt: skip

_ANNONCE = re.compile(
    r"\b(siren|siret|r\.?\s?c\.?\s?s\.?|rna|n°\s*(?:d['’]\s*)?association|num[ée]ro\s+(?:d['’]\s*)?association|tva(?:\s+intracommunautaire)?)\b",
    re.IGNORECASE,
)
_HEBERGEUR = re.compile(r"h[ée]berg|hosting|hosted by", re.IGNORECASE)
_RNA = re.compile(r"\bW\s?\d{9}\b", re.IGNORECASE)
_TVA = re.compile(r"\bFR\s?([0-9A-Z]{2})\s?(\d{3}\s?\d{3}\s?\d{3})\b", re.IGNORECASE)
_CHIFFRES = re.compile(r"(?<![\dA-Za-z])(\d(?:[\s. ]?\d){8,13})(?![\dA-Za-z])")


def luhn(numero: str) -> bool:
    """Clé de Luhn (SIREN, SIRET) : vraie si le numéro est bien formé."""
    if not numero.isdigit():
        return False
    total = 0
    for i, ch in enumerate(reversed(numero)):
        d = int(ch)
        if i % 2:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def numero_valide(numero: str) -> str:
    """« siren », « siret » ou « » (rejeté). La Poste : contrôle propre à ses SIRET."""
    if len(numero) == 9 and luhn(numero):
        return "siren"
    if len(numero) == 14:
        if numero.startswith(LA_POSTE):
            return "siret" if sum(int(c) for c in numero) % 5 == 0 else ""
        return "siret" if luhn(numero) and luhn(numero[:9]) else ""
    return ""


def _chiffres(v: str) -> str:
    return re.sub(r"\D", "", v)


def numeros_du_texte(texte: str) -> list[tuple[str, str]]:
    """(type, numéro) annoncés dans le texte, sans doublon, numéros d'hébergeur écartés. Types : siren, siret, rna."""
    out: list[tuple[str, str]] = []
    for m in _ANNONCE.finditer(texte):
        if _HEBERGEUR.search(texte[max(0, m.start() - 150) : m.start()]):
            continue  # « Hébergé par … RCS … » : le numéro de l'hébergeur, pas celui du site
        mot = m.group(1).casefold()
        suite = texte[m.end() : m.end() + 60]
        trouve: tuple[str, str] | None = None
        if mot.startswith("tva"):
            t = _TVA.search(suite)
            if t and numero_valide(_chiffres(t.group(2))) == "siren":
                trouve = ("siren", _chiffres(t.group(2)))
        elif mot == "rna" or "association" in mot:
            r = _RNA.search(suite)
            if r:
                trouve = ("rna", "W" + _chiffres(r.group(0)))
            else:
                c = _CHIFFRES.search(suite)  # « n° d'association » suivi d'un SIREN : accepté s'il est valide
                if c and (genre := numero_valide(_chiffres(c.group(1)))):
                    trouve = (genre, _chiffres(c.group(1)))
        else:
            c = _CHIFFRES.search(suite)
            if c and (genre := numero_valide(_chiffres(c.group(1)))):
                trouve = (genre, _chiffres(c.group(1)))
        if trouve and trouve not in out:
            out.append(trouve)
    return out


def _texte(v: Any) -> str:
    if isinstance(v, list):
        v = next((x for x in v if isinstance(x, str | dict)), "")
    if isinstance(v, dict):
        v = v.get("@value") or v.get("name") or ""
    return re.sub(r"\s+", " ", str(v or "")).strip()[:200]


def _types(item: dict) -> set[str]:
    t = item.get("@type") or []
    t = t if isinstance(t, list) else [t]
    return {str(x).rsplit("/", 1)[-1].casefold() for x in t}


def _aplatir(items: list[Any]) -> list[dict]:
    out: list[dict] = []
    for it in items:
        if isinstance(it, dict):
            out.append(it)
            graphe = it.get("@graph")
            if isinstance(graphe, list):
                out.extend(_aplatir(graphe))
    return out


def organisations(body: bytes, base_url: str) -> list[dict]:
    """Les objets schema.org de type organisation de la page (niveau haut et `@graph` seulement : une organisation citée DANS un
    article, comme auteur ou partenaire, n'est pas celle qui publie la page). Une page mal formée rend une liste vide."""
    try:
        import extruct
    except ImportError:  # dépendance du moteur ; absente : rien de relevé, jamais une panne
        log.warning("extruct absent : données structurées non relevées")
        return []
    try:
        data = extruct.extract(body, base_url=base_url, syntaxes=["json-ld", "microdata", "rdfa"], uniform=True, errors="ignore")
    except Exception as exc:  # noqa: BLE001 - une page mal formée ne doit jamais arrêter la collecte
        log.debug("extruct : %s", exc)
        return []
    items = _aplatir([x for syntaxe in ("json-ld", "microdata", "rdfa") for x in data.get(syntaxe) or []])
    return [it for it in items if _types(it) & _TYPES_ORG]


def _nom_norme(v: str) -> str:
    v = "".join(c for c in unicodedata.normalize("NFKD", v.casefold()) if not unicodedata.combining(c))
    return re.sub(r"\W+", " ", v).strip()


def relever(body: bytes, texte: str, url: str) -> dict[str, Any]:
    """Ce que la page déclare d'elle-même, en champs typés ; {} si rien de sûr. Clés possibles : `numero`, `type_numero`
    (siren, siret, rna), `methode` (schema.org, texte), `nom`, `ville`, `code_postal`, `telephone`, `comptes` (liste d'URL)."""
    site = site_key(canonical_domain(url))
    orgs = []
    for o in organisations(body, url):
        u = _texte(o.get("url"))
        if u and site_key(canonical_domain(u)) != site:
            continue  # une organisation d'un autre site (partenaire, fédération) : pas celle qui publie
        orgs.append(o)
    noms = {_nom_norme(_texte(o.get("legalName") or o.get("name"))) for o in orgs} - {""}
    out: dict[str, Any] = {}
    numeros_schema: set[tuple[str, str]] = set()
    if len(noms) <= 1 and orgs:  # plusieurs organisations différentes : on ne sait pas laquelle est le site
        for o in orgs:
            for champ in ("taxID", "vatID", "identifier", "leiCode"):
                brut = _texte(o.get(champ))
                tva = _TVA.search(brut)
                n = _chiffres(tva.group(2)) if tva else _chiffres(brut)
                if genre := numero_valide(n):
                    numeros_schema.add((genre, n))
                elif r := _RNA.search(brut):
                    numeros_schema.add(("rna", "W" + _chiffres(r.group(0))))
            adresse = o.get("address")
            adresse = adresse[0] if isinstance(adresse, list) and adresse else adresse
            if isinstance(adresse, dict):
                if v := _texte(adresse.get("addressLocality")):
                    out.setdefault("ville", v)
                if v := _texte(adresse.get("postalCode")):
                    out.setdefault("code_postal", v)
            if v := _texte(o.get("legalName") or o.get("name")):
                out.setdefault("nom", v)
            if v := _texte(o.get("telephone")):
                out.setdefault("telephone", v)
            comptes = o.get("sameAs") or []
            comptes = comptes if isinstance(comptes, list) else [comptes]
            urls = [str(c) for c in comptes if isinstance(c, str) and c.startswith(("http://", "https://"))][:20]
            if urls:
                out.setdefault("comptes", urls)
    numeros_texte = set(numeros_du_texte(texte))
    # un seul numéro pour la page : sinon on ne sait pas lequel est celui du site (choix prudent, spec 914)
    tous = numeros_schema | numeros_texte
    sirens = {n[:9] for g, n in tous if g in ("siren", "siret")}
    rnas = {n for g, n in tous if g == "rna"}
    if len(sirens) == 1 and len(rnas) <= 1:
        genre, n = max((x for x in tous if x[0] in ("siren", "siret")), key=lambda x: len(x[1]))
        if genre == "siret" and len({n for g, n in tous if g == "siret"}) > 1:
            genre, n = "siren", n[:9]  # deux SIRET du même SIREN : deux établissements, seul le SIREN est sûr
        out.update(numero=n, type_numero=genre, methode="schema.org" if (genre, n) in numeros_schema or ("siren", n[:9]) in numeros_schema else "texte")
    elif not sirens and len(rnas) == 1:
        n = next(iter(rnas))
        out.update(numero=n, type_numero="rna", methode="schema.org" if ("rna", n) in numeros_schema else "texte")
    return out


def depuis_meta(v: str | None) -> dict[str, Any]:
    """La déclaration rangée dans une observation (JSON) ; {} si absente ou illisible."""
    if not v:
        return {}
    try:
        d = json.loads(v)
    except ValueError:
        return {}
    return d if isinstance(d, dict) else {}
