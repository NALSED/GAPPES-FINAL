"""Faits d'un candidat, tirés de ce que grappes sait (jamais un avis du programme).

Tourne dans l'interpréteur de GRAPPES (importé par `executer.py`) et dans les tests de pilote. N'importe rien de pilote.

Chaque nom est rattaché à des PREUVES : une preuve = une source qui l'a donné (ou la page qu'une source a trouvée et où il a été lu), avec
sa classe d'origine (registre, presse, encyclo, web, texte) et sa main (première : le registre qui détient l'information ; seconde : une
page qui la répète). De là :
* origine : la classe la plus solide des preuves (une seule valeur, le fait qui colore Tri) ;
* trouvé par : les sources, jamais des étiquettes techniques ;
* nombre d'endroits : endroits distincts qui le nomment, sans compter deux fois une page de seconde main qui peut recopier une source de première main ;
* numéro officiel, site, ville, genre : seulement si une source les donne ; jamais déduits.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from pilote.adaptateurs import alias_de

ORIGINES = ("registre", "presse", "encyclo", "web", "texte")  # du plus solide au plus fragile
CLASSE_ECOSYSTEME = {"web": "web", "rss": "presse", "wikipedia": "encyclo"}  # classe d'une page selon son écosystème, faute de mieux


@dataclass(slots=True)
class Provenance:
    jetons: dict[str, str] = field(default_factory=dict)  # étiquette de registre de grappes -> identifiant de source
    origines: dict[str, str] = field(default_factory=dict)  # identifiant de source -> classe
    mains: dict[str, str] = field(default_factory=dict)  # identifiant de source -> premiere / seconde
    eco_par_site: dict[str, str] = field(default_factory=dict)  # site (clé normalisée) -> écosystème de la page
    fournisseurs_par_site: dict[str, set[str]] = field(default_factory=dict)  # site -> identifiants des sources qui ont trouvé cette page
    declare_par_site: dict[str, dict[str, Any]] = field(default_factory=dict)  # 914/A : site -> ce qu'il déclare de lui-même


def est_exclu(nom_norme: str, exclus: list[str]) -> bool:
    """Vrai si le nom (déjà mis à plat) contient un mot à exclure, ou une suite de mots, ENTIER : exclure « art » ne retire pas « Marteau »."""
    return any(f" {m} " in f" {nom_norme} " for m in exclus)


def _ecosysteme(ref: str) -> str:
    return ref.partition(":")[0]


def preuves(c: Any, prov: Provenance, site_key) -> list[dict[str, str]]:
    """Les preuves d'un candidat (sans doublon : une source, un endroit)."""
    out: dict[tuple[str, str], dict[str, str]] = {}

    def ajouter(source: str, classe: str, lieu: str, propre: bool = False) -> None:
        p = {"source": source, "classe": classe, "main": prov.mains.get(source, "seconde"), "lieu": lieu}
        if propre:  # 913/N5 : le site de l'acteur lui-même, gardé comme preuve, jamais compté comme un endroit indépendant
            p["propre"] = "oui"
        out.setdefault((source, lieu), p)

    for jeton in c.registres:
        source = prov.jetons.get(jeton, jeton)
        ajouter(source, prov.origines.get(source, "registre"), f"registre:{source}")
    pages = {site_key(x.partition(":")[2]) if _ecosysteme(x) in ("web", "rss") else x: _ecosysteme(x) for x in c.citants}
    if _ecosysteme(c.ref) in ("web", "rss", "wikipedia"):
        pages.setdefault(site_key(c.ref.partition(":")[2]) if _ecosysteme(c.ref) in ("web", "rss") else c.ref, _ecosysteme(c.ref))
    for site in c.ner_sites:
        pages.setdefault(site, prov.eco_par_site.get(site, ""))
    propre = site_key(c.ref.partition(":")[2]) if _ecosysteme(c.ref) in ("web", "rss") else ""
    for site, eco in pages.items():
        eco = eco or prov.eco_par_site.get(site, "")
        fournisseurs = prov.fournisseurs_par_site.get(site) or set()
        if fournisseurs:
            for f in sorted(fournisseurs):
                ajouter(f, prov.origines.get(f) or CLASSE_ECOSYSTEME.get(eco, "texte"), f"page:{site}", site == propre)
        else:
            ajouter(f"({eco or 'texte'})", CLASSE_ECOSYSTEME.get(eco, "texte"), f"page:{site}", site == propre)
    return sorted(out.values(), key=lambda p: (ORIGINES.index(p["classe"]) if p["classe"] in ORIGINES else 9, p["source"], p["lieu"]))


def endroits_comptes(ps: list[dict[str, str]]) -> int:
    """Les ENDROITS DISTINCTS qui comptent comme confirmations (le nombre affiché dans Tri, à côté de l'origine et jamais
    mélangé avec elle : « 3 endroits » sur le web ne vaut pas « 1 endroit » dans un registre officiel).

    * Une source de première main (un registre) est un endroit.
    * Une page de seconde main peut recopier un registre : dès qu'un nom a au moins une preuve de première main, les pages de seconde main ne
      s'y ajoutent PAS (une confirmation de seconde main qui pointe vers une source déjà comptée ne compte pas deux fois ; on ne sait pas
      toujours vers quoi elle pointe, alors on ne la compte pas du tout, par prudence).
    * Sans preuve de première main, chaque page distincte (un site = un endroit) est un endroit.
    * 913/N5 : le site de l'acteur lui-même (`propre`) n'est pas un endroit indépendant, comme dans le moteur (`production.niveau_de`).
      Un acteur trouvé seulement sur son site compte toujours un endroit."""
    premiers = {p["lieu"] for p in ps if p["main"] == "premiere"}
    return max(1, len(premiers) if premiers else len({p["lieu"] for p in ps if not p.get("propre")}))


def niveau_de(ps: list[dict[str, str]], nb_endroits: int) -> str:
    """A3 (spec 912) : « sur » ou « a_verifier ». Un fait, pas un score. Sûr si le nom est dans un registre de première main, ou s'il a
    été trouvé à deux endroits indépendants au moins (`endroits_comptes`, sans double compte). La troisième voie, une confirmation au
    sens de A2, n'est connue qu'après la vérification : `verification.relever_niveaux` la pose alors. Tout le reste est à vérifier."""
    return "sur" if nb_endroits >= 2 or any(p["main"] == "premiere" for p in ps) else "a_verifier"


def origine_de(ps: list[dict[str, str]]) -> str:
    """La preuve la plus solide (l'ordre est celui de la maquette : du solide au fragile)."""
    return next((o for o in ORIGINES if any(p["classe"] == o for p in ps)), "web")


def numero_officiel(decouverts: list[Any]) -> str:
    """Un numéro d'entreprise ou d'association donné par un registre, jamais l'identifiant d'une encyclopédie."""
    return next((d.siren for d in decouverts if getattr(d, "siren", "")), "")


def site_de(c_ref: str, domaine: str) -> str:
    if domaine:
        return domaine
    eco, _, ident = c_ref.partition(":")
    return ident if eco in ("web", "rss") else ""


def _liens(decouverts: list[Any], cle: str) -> list[Any]:
    out = []
    for d in decouverts:
        v = (getattr(d, "liens", None) or {}).get(cle)
        if v:
            try:
                out.append(json.loads(v))
            except ValueError:
                continue
    return out


def reunir_declarations(ds: list[dict[str, Any]]) -> dict[str, Any]:
    """914/A : les déclarations des pages d'un même site, réunies. Deux pages du site qui donnent des numéros différents (deux SIREN, ou deux
    SIRET différents) : aucun numéro n'est gardé, on ne sait pas lequel est le bon. Les autres champs : le premier connu."""
    from pilote.rapprochements import cle_numero

    out: dict[str, Any] = {}
    for d in ds:
        for k, v in d.items():
            if k not in ("numero", "type_numero", "methode") and v:
                out.setdefault(k, v)
    numeros = {str(d["numero"]) for d in ds if d.get("numero")}
    if numeros and len({cle_numero(n) for n in numeros}) == 1:
        siret = {n for n in numeros if len(n) == 14}
        if len(siret) <= 1:
            n = max(numeros, key=len)
            d = next(x for x in ds if x.get("numero") == n)
            out.update(numero=n, type_numero=d.get("type_numero", ""), methode=d.get("methode", ""))
        else:  # deux établissements du même SIREN : seul le SIREN est sûr
            out.update(numero=next(iter(siret))[:9], type_numero="siren", methode=ds[0].get("methode", ""))
    return out


def declaration(c_ref: str, domaine: str, site_key, prov: Provenance) -> dict[str, Any]:
    """914/A : ce que le site de l'acteur déclare de lui-même (numéro officiel, ville…), ou {}. Jamais une preuve : affiché, et sert
    seulement à PROPOSER un rapprochement (spec 914, choix 1 et 2)."""
    site = site_de(c_ref, domaine)
    return dict(prov.declare_par_site.get(site_key(site), {})) if site else {}


def numero_different(numero_registre: str, declare: dict[str, Any]) -> bool:
    """914/A, choix 3 : le numéro donné par un registre n'est pas celui que le site déclare (alerte affichée, niveau inchangé)."""
    from pilote.rapprochements import cle_numero

    a, b = cle_numero(numero_registre), cle_numero(str(declare.get("numero") or ""))
    return bool(a and b and a != b)


def faits_candidat(c: Any, decouverts_du_nom: list[Any], site_key, pays: str, prov: Provenance | None = None) -> dict[str, Any]:
    prov = prov or Provenance()
    ps = preuves(c, prov, site_key)
    genre = next((d.type_candidat for d in decouverts_du_nom if getattr(d, "type_candidat", "")), "")
    domaine = next((d.domaine for d in decouverts_du_nom if getattr(d, "domaine", "")), "")
    relations = [r for lot in _liens(decouverts_du_nom, "relations") for r in lot]
    coord = next(iter(_liens(decouverts_du_nom, "coordonnees")), None)
    fonction = next(iter(_liens(decouverts_du_nom, "fonction")), "")
    alias = alias_de(c.nom, [a for lot in _liens(decouverts_du_nom, "alias") for a in lot])  # les autres noms déclarés par les sources, sans le nom de la fiche
    declare = declaration(c.ref, domaine, site_key, prov)
    numero = numero_officiel(decouverts_du_nom)
    return {
        "nom": c.nom,
        "genre_source": origine_de(ps),
        "trouve_par": sorted({p["source"] for p in ps}),
        "nb_endroits": endroits_comptes(ps),
        "genre_de_chose": genre,
        "ville": c.ville or "",
        "pays": pays,
        "site": site_de(c.ref, domaine),
        "numero_officiel": numero,
        "relations": relations,
        # `regle8_personne` : le constat posé par `pilote.regle8.est_personne` au moment de la collecte. Il reste vrai même quand un levier
        # a laissé le genre déclaré par la source, et c'est lui que lisent les garde-fous qu'un levier n'ouvre pas (sortie FollowTheMoney).
        "faits": {"ref": c.ref, "preuves": ps, "niveau": niveau_de(ps, endroits_comptes(ps)), **({"regle8_personne": True} if any(_liens(decouverts_du_nom, "regle8")) else {}),
                  **({"coordonnees": coord} if coord else {}), **({"fonction": fonction} if fonction else {}), **({"alias": alias} if alias else {}),
                  **({"declare": declare} if declare else {}), **({"numero_site_different": True} if numero_different(numero, declare) else {})},
    }  # fmt: skip
