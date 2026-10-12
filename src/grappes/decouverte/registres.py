"""Découvrir des acteurs nommés dans les registres et bases structurées (chantier 1, D63).

Sources (activables une à une dans `config/decouverte.yaml`) :
* `wikidata` : éléments de la classe retenue dans le pays (P31, option sous-classes P279*), avec site officiel (P856),
  SIREN (P1616) et commune (P159 siège, sinon P131) ;
* `sirene` : annuaire des entreprises (SIRENE et RNA, `recherche-entreprises.api.gouv.fr`), établissements ACTIFS,
  par code NAF recouvrant la phrase, sinon par nom ; commune du siège donnée par le registre.

Jamais de déduction : une commune absente du registre reste vide. Un nom est celui du registre, tel quel.
"""

from __future__ import annotations

import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path

from grappes.decouverte.client import DecouverteError, Http
from grappes.decouverte.traduction import (
    ClasseWikidata,
    CodeNaf,
    charger_naf,
    classe_wikidata,
    code_naf,
    mots,
    noyau,
    racine,
)

API_ENTREPRISES = "https://recherche-entreprises.api.gouv.fr/search"


@dataclass(slots=True)
class Decouvert:
    nom: str
    registre: str  # "wikidata" | "sirene"
    identifiant: str  # QID ou SIREN
    ville: str = ""
    domaine: str = ""  # site officiel quand le registre le donne
    siren: str = ""
    requete: str = ""  # trace de la traduction (classe retenue, code NAF...)
    liens: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DecouverteConfig:
    sources: tuple[str, ...] = ("wikidata", "sirene")
    pays_wikidata: str = "Q142"
    min_instances: int = 3
    sous_classes: bool = False
    limite_wikidata: int = 3000
    seuil_naf: float = 0.6
    pages_sirene: int = 8
    par_page: int = 25
    repli_nom: bool = True  # sans code NAF fiable : recherche par nom, filtrée sur les mots de la phrase
    naf: str = "config/naf_rev2.csv"


def wikidata(cls: ClasseWikidata, http: Http, cfg: DecouverteConfig) -> list[Decouvert]:
    lien = "wdt:P31/wdt:P279*" if cfg.sous_classes else "wdt:P31"
    q = (
        "SELECT ?item ?itemLabel ?site ?siren ?villeLabel WHERE { ?item %s wd:%s ; wdt:P17 wd:%s . "
        "OPTIONAL { ?item wdt:P856 ?site } OPTIONAL { ?item wdt:P1616 ?siren } "
        "OPTIONAL { ?item wdt:P159|wdt:P131 ?ville } "
        'SERVICE wikibase:label { bd:serviceParam wikibase:language "fr,en" } } LIMIT %d'
        % (lien, cls.qid, cfg.pays_wikidata, cfg.limite_wikidata)
    )
    par: dict[str, Decouvert] = {}
    for r in http.sparql(q):
        qid = r["item"]
        nom = r.get("itemLabel", "")
        if not nom or nom == qid:  # pas de libellé lisible : rien à rendre
            continue
        d = par.setdefault(qid, Decouvert(nom, "wikidata", qid, requete=f"{cls.qid} « {cls.libelle} »"))
        if r.get("site") and not d.domaine:
            d.domaine = r["site"]
        if r.get("siren") and not d.siren:
            d.siren = r["siren"].replace(" ", "")
        v = r.get("villeLabel", "")
        if v and not v.startswith("Q") and not d.ville:
            d.ville = v
    return sorted(par.values(), key=lambda d: d.identifiant)


def _filtre_nom(nom_registre: str, requis: list[str]) -> bool:
    """Le nom contient au moins la moitié (arrondie en haut) des mots distinctifs demandés (racines)."""
    lm = {racine(m) for m in mots(nom_registre)}
    return sum(1 for m in requis if racine(m) in lm) >= max(1, -(-len(requis) // 2))


def sirene(phrase: str, naf: CodeNaf | None, http: Http, cfg: DecouverteConfig) -> list[Decouvert]:
    """Établissements actifs (sièges) : par code NAF si fiable, sinon par nom (repli)."""
    params: dict[str, str] = {"etat_administratif": "A", "per_page": str(cfg.par_page)}
    requis: list[str] = []
    if naf is not None:
        params["activite_principale"] = naf.code
        if naf.reste:
            params["q"] = " ".join(naf.reste)
            requis = naf.reste
        trace = f"NAF {naf.code} « {naf.libelle} »" + (f" + nom « {params['q']} »" if "q" in params else "")
    elif cfg.repli_nom:
        requis = noyau(phrase)
        if not requis:
            return []
        params["q"] = " ".join(requis)
        trace = f"nom « {params['q']} »"
    else:
        return []
    out: dict[str, Decouvert] = {}
    for page in range(1, cfg.pages_sirene + 1):
        url = API_ENTREPRISES + "?" + urllib.parse.urlencode({**params, "page": str(page)})
        try:
            d = http.get_json(url)
        except DecouverteError:
            break
        res = d.get("results", []) if isinstance(d, dict) else []
        for e in res:
            nom = e.get("nom_complet") or e.get("nom_raison_sociale") or ""
            siren = e.get("siren", "")
            if not nom or not siren or (requis and not _filtre_nom(nom, requis)):
                continue
            ident = (e.get("complements") or {}).get("identifiant_association") or siren
            out.setdefault(
                siren,
                Decouvert(
                    nom, "sirene", ident, (e.get("siege") or {}).get("libelle_commune") or "",
                    siren=siren, requete=trace,
                ),
            )  # fmt: skip
        if len(res) < cfg.par_page or page >= (d.get("total_pages") or page):
            break
    return sorted(out.values(), key=lambda x: x.siren)


def decouvrir(phrase: str, http: Http, cfg: DecouverteConfig | None = None) -> list[Decouvert]:
    cfg = cfg or DecouverteConfig()
    out: list[Decouvert] = []
    if "wikidata" in cfg.sources:
        cls = classe_wikidata(phrase, http, cfg.pays_wikidata, cfg.min_instances)
        if cls is not None:
            try:
                out += wikidata(cls, http, cfg)
            except DecouverteError:
                pass
    if "sirene" in cfg.sources:
        naf = code_naf(phrase, charger_naf(Path(cfg.naf)), cfg.seuil_naf)
        out += sirene(phrase, naf, http, cfg)
    return out
