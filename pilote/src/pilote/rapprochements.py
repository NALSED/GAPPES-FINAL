"""L'onglet Tri (spécification 16) : la file des rapprochements que Splink propose et qu'une PERSONNE tranche.

Patron d'Aleph et de Splink (15 § 1) : rappel large, score, validation humaine. Ici :
 * `proposer` compare les noms (Candidat) d'une recherche terminée et range en file les paires dont la confiance atteint `SEUIL` ; la confiance est le
   score de Splink (`rapprochement_splink`), jamais une saisie ;
 * `file` rend les cartes, du moins certain au plus certain, avec la comparaison champ par champ calculée ici (accord / désaccord / absence) ;
 * `trancher` enregistre la décision. CONFIRMER écrit un lien « même entité » des deux côtés (`Candidat.relations`) ; SÉPARER n'écrit rien, il empêche
   seulement de reproposer la paire. Ni l'un ni l'autre n'efface une fiche, une source ou un fichier, et les deux se refont.

Règle 8 : une fiche de genre « personne » n'entre jamais dans un rapprochement, et seuls nom d'entité, ville, numéro officiel et site servent de clé."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from pilote import mentions, suite, tri
from pilote.base import Candidat, Journal, Rapprochement, Recherche
from pilote.config import Config

SEUIL = 0.2  # en dessous, la paire n'est pas proposée : trop incertaine pour mériter l'attention d'une personne
DELAI_S = 120
SRC = Path(__file__).resolve().parents[1]
ETATS_DE_COMPARAISON = ("accord", "desaccord", "absence")
GENRES = {"association": "d'association", "entreprise": "d'entreprise", "club": "de club", "administration": "d'administration", "lieu": "de lieu", "evenement": "d'événement"}


class Indisponible(RuntimeError):
    """Le moteur de rapprochement n'a pas pu tourner : la raison est donnée en français, jamais avalée."""


def _fiche(c: Candidat) -> dict[str, Any]:
    return {"id": c.id, "nom": c.nom, "ville": c.ville or "", "numero": c.numero_officiel or "", "site": c.site or "", "alias": list((c.faits or {}).get("alias") or [])}


def _scorer(fiches: list[dict[str, Any]], seuil: float) -> list[dict[str, Any]]:
    env = {**os.environ, "PYTHONPATH": os.pathsep.join([str(SRC), os.environ.get("PYTHONPATH", "")]).rstrip(os.pathsep)}
    try:
        p = subprocess.run([sys.executable, "-m", "pilote.rapprochement_splink"], input=json.dumps({"fiches": fiches, "seuil": seuil}), capture_output=True, text=True, timeout=DELAI_S, env=env, check=False)
    except subprocess.TimeoutExpired as exc:
        raise Indisponible(f"Le moteur de rapprochement a dépassé {DELAI_S} secondes.") from exc
    if p.returncode != 0:
        derniere = (p.stderr.strip().splitlines() or ["il s'est arrêté sans message"])[-1][:200]
        raise Indisponible(f"Le moteur de rapprochement (Splink) n'a pas pu tourner : {derniere}")
    try:
        return json.loads(p.stdout)
    except ValueError as exc:
        raise Indisponible("Le moteur de rapprochement a rendu une réponse illisible.") from exc


def _deja_liees(cands: list[Candidat]) -> set[tuple[int, int]]:
    """Deux noms que les sources ont elles-mêmes liés (siège et établissement, maison mère) sont des entités DIFFÉRENTES : on ne les propose pas."""
    from pilote.rapprochement import nom_nu

    par_nom: dict[str, list[int]] = {}
    for c in cands:
        par_nom.setdefault(nom_nu(c.nom), []).append(c.id)
    out: set[tuple[int, int]] = set()
    for c in cands:
        for r in c.relations or []:
            if not isinstance(r, dict) or r.get("type") == "meme_entite":
                continue
            for j in par_nom.get(nom_nu(str(r.get("vers", ""))), []):
                if j != c.id:
                    out.add((min(c.id, j), max(c.id, j)))
    return out


def proposer(cfg: Config, fabrique: sessionmaker[Session], rid: str, seuil: float | None = None) -> dict[str, Any]:
    """Range en file les rapprochements d'une recherche. `seuil` : réglage « Même entité si » de la tuile Fusion
    posée sur le plan (3.8.05) ; absent, celui de la tuile Fusion de CETTE recherche, sinon le réglage par défaut (SEUIL). Rend
    {proposes, comparees}. Lève `Indisponible` si le moteur ne tourne pas."""
    with fabrique() as s:
        if seuil is None:  # relancé depuis Tri : la tuile posée au lancement vaut toujours
            r = s.get(Recherche, rid)
            fusion = (((r.parametres if r else None) or {}).get("plan") or {}).get("fusion") or {}
            seuil = float(fusion.get("seuil", SEUIL))
        # Règle 8 : une fiche de genre « personne » n'entre pas dans un rapprochement, SAUF si une personne a explicitement levé la règle sur
        # cette fiche-là (`tri.marquer_personne_morale`, trace dans `faits.regle8_leve`). Le genre n'est jamais réécrit : il dit ce que la
        # collecte a constaté, la levée dit ce qu'une personne a décidé, et les deux restent lisibles côte à côte.
        cands = [c for c in s.scalars(select(Candidat).where(Candidat.recherche_id == rid))
                 if (c.genre_de_chose or "").strip().lower() != "personne" or (c.faits or {}).get("regle8_leve")]  # fmt: skip
        deja = {(r.a, r.b) for r in s.scalars(select(Rapprochement).where(Rapprochement.recherche_id == rid))}
        liees = _deja_liees(cands)
    reunis = _reunir_par_numero(fabrique, rid, cands, deja, liees)  # A7 (spec 912) : avant Splink, et même s'il ne tourne pas
    deja |= reunis
    par_site = _proposer_par_numero_declare(fabrique, rid, cands, deja, liees)  # 914/A : proposé, jamais réuni d'office
    deja |= par_site
    if len(cands) < 2:
        return {"proposes": len(par_site), "comparees": len(cands), **({"reunis": len(reunis)} if reunis else {})}  # `reunis` (A7) seulement quand il y en a : le bilan d'avant reste le même
    paires = [p for p in _scorer([_fiche(c) for c in cands], seuil) if (p["a"], p["b"]) not in deja and (p["a"], p["b"]) not in liees and p["confiance"] >= seuil]
    with fabrique.begin() as s:
        for p in paires:
            s.add(Rapprochement(recherche_id=rid, a=p["a"], b=p["b"], confiance=p["confiance"], pourquoi=p["pourquoi"]))
        if paires:
            s.add(Journal(recherche_id=rid, qui="pilote", evenement="rapprochements_proposes", detail={"n": len(paires)}))
    return {"proposes": len(paires) + len(par_site), "comparees": len(cands), **({"reunis": len(reunis)} if reunis else {})}


def cle_numero(numero: str) -> str:
    """Le numéro officiel sous une forme comparable. Un SIREN (9 chiffres) ou un SIRET (14 chiffres) rend le SIREN : un SIRET du même SIREN
    est la même entité juridique. Tout autre numéro (RNA, LEI…) se compare tel quel, sans espaces ni casse. Trop court (moins de 5 signes) : rien."""
    brut = re.sub(r"[\s.\-]", "", str(numero or "")).upper()
    if brut.isdigit() and len(brut) in (9, 14):
        return brut[:9]
    return brut if len(brut) >= 5 else ""


def _reunir_par_numero(fabrique: sessionmaker[Session], rid: str, cands: list[Candidat], deja: set[tuple[int, int]], liees: set[tuple[int, int]]) -> set[tuple[int, int]]:
    """A7 (spec 912) : deux fiches qui portent le MÊME numéro officiel (même SIREN, ou un SIREN et un SIRET de ce SIREN ; jamais deux SIRET
    différents : deux établissements) sont réunies d'office (rapprochement confirmé par « pilote », confiance 1).
    Rien d'autre n'est réuni sans une personne. Jamais : une paire déjà tranchée ou déjà proposée (la décision d'une personne tient), ni deux noms
    que la source a elle-même liés comme siège et établissement (`_deja_liees` : entités distinctes). Les fiches de personnes n'arrivent pas ici
    (`cands` les a déjà écartées, règle 8). Se défait comme tout rapprochement (« séparer »)."""
    par_cle: dict[str, list[int]] = {}
    for c in cands:
        if cle := cle_numero(c.numero_officiel or ""):
            par_cle.setdefault(cle, []).append(c.id)
    complet = {c.id: re.sub(r"\D", "", c.numero_officiel or "") for c in cands}

    def deux_etablissements(i: int, j: int) -> bool:  # deux SIRET différents d'un même SIREN : deux établissements, jamais la même fiche (cas réel Danone)
        return len(complet[i]) == 14 and len(complet[j]) == 14 and complet[i] != complet[j]

    paires = {(min(i, j), max(i, j)): cle for cle, ids in par_cle.items() for n, i in enumerate(ids) for j in ids[n + 1 :]}
    paires = {p: cle for p, cle in paires.items() if p not in deja and p not in liees and not deux_etablissements(*p)}
    if not paires:
        return set()
    with fabrique.begin() as s:
        for (i, j), cle in sorted(paires.items()):
            r = Rapprochement(recherche_id=rid, a=i, b=j, confiance=1.0, pourquoi={"numero_officiel": f"même numéro officiel ({cle})"})
            s.add(r)
            s.flush()
            _appliquer(s, r, "confirme", "pilote")
        s.add(Journal(recherche_id=rid, qui="pilote", evenement="rapprochements_reunis_par_numero", detail={"n": len(paires)}))
    return set(paires)


def _proposer_par_numero_declare(fabrique: sessionmaker[Session], rid: str, cands: list[Candidat], deja: set[tuple[int, int]], liees: set[tuple[int, int]]) -> set[tuple[int, int]]:
    """914/A, choix 2 : deux fiches dont les SITES déclarent le même numéro officiel (même SIREN, ou un SIREN et un SIRET de ce SIREN ; jamais
    deux SIRET différents) sont PROPOSÉES à une personne, jamais réunies d'office : un site peut se tromper ou recopier le numéro d'un autre.
    A7 (numéro donné par un registre) reste seul à réunir d'office. Mêmes exclusions que A7 : paire déjà tranchée ou proposée, noms liés."""
    numeros = {c.id: str(((c.faits or {}).get("declare") or {}).get("numero") or "") for c in cands}
    par_cle: dict[str, list[int]] = {}
    for i, n in numeros.items():
        if cle := cle_numero(n):
            par_cle.setdefault(cle, []).append(i)

    def deux_etablissements(i: int, j: int) -> bool:
        return len(numeros[i]) == 14 and len(numeros[j]) == 14 and numeros[i] != numeros[j]

    paires = {(min(i, j), max(i, j)): cle for cle, ids in par_cle.items() for n, i in enumerate(ids) for j in ids[n + 1 :]}
    paires = {p: cle for p, cle in paires.items() if p not in deja and p not in liees and not deux_etablissements(*p)}
    if not paires:
        return set()
    with fabrique.begin() as s:
        for (i, j), cle in sorted(paires.items()):
            s.add(Rapprochement(recherche_id=rid, a=i, b=j, confiance=1.0, pourquoi={"numero_declare": f"leurs sites déclarent le même numéro officiel ({cle})"}))
        s.add(Journal(recherche_id=rid, qui="pilote", evenement="rapprochements_proposes_par_numero_du_site", detail={"n": len(paires)}))
    return set(paires)


def _recompter(s: Session, cand: Candidat) -> None:
    """A7 (spec 912) : le nombre d'endroits d'une fiche réunie à d'autres compte les preuves de TOUTES ces fiches, chaque endroit une seule fois
    (`pont.faits.endroits_comptes`, la règle de la collecte). Le compte de la fiche seule est gardé (`faits.nb_endroits_seul`) : séparer le rend."""
    from pilote.pont.faits import endroits_comptes, niveau_de

    faits = dict(cand.faits or {})
    seul = int(faits.get("nb_endroits_seul") or cand.nb_endroits or 1)
    niveau_seul = faits.get("niveau_seul") or faits.get("niveau")  # 913/N4 : le niveau suit la réunion comme le nombre d'endroits
    liens = s.scalars(select(Rapprochement).where(Rapprochement.recherche_id == cand.recherche_id, Rapprochement.etat == "confirme", (Rapprochement.a == cand.id) | (Rapprochement.b == cand.id))).all()
    autres = [x for x in (s.get(Candidat, r.b if r.a == cand.id else r.a) for r in liens) if x is not None]
    if not autres:
        cand.nb_endroits = seul
        faits.pop("nb_endroits_seul", None)
        if niveau_seul:  # séparer rend le niveau de la fiche seule
            faits["niveau"] = niveau_seul
            faits.pop("niveau_seul", None)
    else:
        preuves = [p for f in (cand, *autres) for p in ((f.faits or {}).get("preuves") or []) if isinstance(p, dict) and "lieu" in p and "main" in p]
        faits["nb_endroits_seul"] = seul
        cand.nb_endroits = max(seul, endroits_comptes(preuves) if preuves else seul)
        if niveau_seul:
            # La même entité : sûre si l'une des fiches l'était seule (registre, confirmation A2), ou si leurs preuves réunies suffisent.
            seuls = [niveau_seul, *((f.faits or {}).get("niveau_seul") or (f.faits or {}).get("niveau") for f in autres)]
            faits["niveau_seul"] = niveau_seul
            faits["niveau"] = "sur" if "sur" in seuls or niveau_de(preuves, cand.nb_endroits) == "sur" else "a_verifier"
    cand.faits = faits


def _appliquer(s: Session, r: Rapprochement, action: str, qui: str) -> tuple[Candidat, Candidat]:
    a, b = s.get(Candidat, r.a), s.get(Candidat, r.b)
    assert a is not None and b is not None
    for cand, autre in ((a, b), (b, a)):  # on repart toujours des liens SANS ce rapprochement : changer d'avis ne laisse rien derrière
        cand.relations = [x for x in (cand.relations or []) if not (isinstance(x, dict) and x.get("rapprochement") == r.id)]
        if action == "confirme":
            cand.relations = [*cand.relations, {"type": "meme_entite", "vers": autre.nom, "source": "tri", "rapprochement": r.id}]
    r.etat, r.decide_par, r.decide_le = action, qui, datetime.now(UTC)
    s.flush()
    for cand in (a, b):
        _recompter(s, cand)
    return a, b


# ---------------------------------------------------------------- la file


_ARRONDISSEMENT = re.compile(r"\s+\d{1,2}\s*(?:e|er|eme|ieme)?(?:\s+arrondissement)?$")


def _ville(v: str) -> str:
    """913/N2 : une ville sans casse, sans accents, sans tirets ni apostrophes, sans numéro d'arrondissement. Les registres écrivent
    « SAINT-ETIENNE » ou « PARIS 11 » : c'est la même ville que « Saint-Étienne » ou « Paris »."""
    import unicodedata

    v = "".join(c for c in unicodedata.normalize("NFKD", v.lower()) if not unicodedata.combining(c))
    v = re.sub(r"\s+", " ", re.sub(r"[-'’.]", " ", v)).strip()
    return _ARRONDISSEMENT.sub("", v)


def _norme(champ: str, v: str) -> str:
    v = re.sub(r"\s+", " ", (v or "").strip().lower())
    if champ == "ville":
        return _ville(v)
    return re.sub(r"[\s.\-]", "", v) if champ == "numero" else v  # un numéro s'écrit avec ou sans espaces : « 412 345 678 » et « 412345678 » sont le même


def _numeros(a: str, b: str) -> bool:
    """913/N3 : un SIREN et un SIRET de ce SIREN désignent la même entreprise (`cle_numero`, la règle de A7). Deux SIRET différents sont
    deux établissements : ils ne concordent pas, comme A7 refuse de les réunir. Tout autre numéro se compare tel quel."""
    da, db = re.sub(r"\D", "", a), re.sub(r"\D", "", b)
    if len(da) == 14 and len(db) == 14:
        return da == db
    ka, kb = cle_numero(a), cle_numero(b)
    return ka == kb if ka and kb else _norme("numero", a) == _norme("numero", b)


def comparer(champ: str, a: str, b: str) -> str:
    """accord / desaccord / absence, calculé champ par champ : une valeur absente d'un côté n'est JAMAIS une différence (il n'y a rien à comparer)."""
    if not (a or "").strip() or not (b or "").strip():
        return "absence"
    if champ == "numero":
        return "accord" if _numeros(a, b) else "desaccord"
    return "accord" if _norme(champ, a) == _norme(champ, b) else "desaccord"


def _titre(a: Candidat, b: Candidat) -> str:
    nom, num = comparer("nom", a.nom, b.nom), comparer("numero", a.numero_officiel, b.numero_officiel)
    genre = (a.genre_de_chose or b.genre_de_chose or "").strip().lower()
    quoi = f"deux fiches {GENRES[genre]}" if genre in GENRES else "deux fiches"
    if num == "accord":
        return f"{quoi}, identifiant officiel identique"
    if nom == "accord":
        return f"{quoi}, nom identique" + (", un identifiant manquant" if num == "absence" else ", identifiants différents")
    return f"{quoi}, nom proche"


def _source_principale(c: Candidat, nom_source, fiabilites: dict[str, str]) -> tuple[str, str]:
    """La source la plus fiable parmi celles qui ont trouvé ce nom, et sa lettre : c'est la colonne que la personne lit en premier."""
    jetons = sorted(set(c.trouve_par or []), key=lambda t: (fiabilites.get(t, "F"), t))
    if not jetons:
        return "source inconnue", "F"
    return nom_source(jetons[0]), fiabilites.get(jetons[0], "F")


def _carte(r: Rapprochement, a: Candidat, b: Candidat, nom_source, fiabilites: dict[str, str]) -> dict[str, Any]:
    champs = [("nom", "Nom", a.nom, b.nom), ("ville", "Ville", a.ville, b.ville), ("numero", "Identifiant", a.numero_officiel, b.numero_officiel), ("site", "Site", a.site, b.site), ("genre", "Genre", a.genre_de_chose, b.genre_de_chose)]
    lignes = [(c, lib, va or "", vb or "", comparer(c, va or "", vb or "")) for c, lib, va, vb in champs if c == "nom" or (va or "").strip() or (vb or "").strip()]  # une ligne par propriété que l'une des fiches porte
    fiches = []
    for cand, cote in ((a, 2), (b, 3)):
        source, lettre = _source_principale(cand, nom_source, fiabilites)
        fiches.append({"candidat": cand.id, "source": source, "fiabilite": lettre, "lignes": [{"champ": c, "libelle": lib, "valeur": ligne[cote], "etat": ligne[4]} for ligne in lignes for c, lib in [(ligne[0], ligne[1])]]})
    return {
        "id": r.id, "recherche": r.recherche_id, "titre": _titre(a, b), "confiance": round(r.confiance * 100), "pourquoi": r.pourquoi, "fiches": fiches, "etat": r.etat,
        "decide_par": r.decide_par, "decide_le": r.decide_le.replace(tzinfo=UTC).isoformat() if r.decide_le else None,
    }  # fmt: skip


def file(cfg: Config, fabrique: sessionmaker[Session]) -> dict[str, Any]:
    """{a_examiner: du moins certain au plus certain, tranches: les plus récentes d'abord}. Rien ne disparaît : une décision reste lisible."""
    nom_source = tri.noms_de_sources(cfg)
    fiabilites = {s["id"]: s["fiabilite"] for s in suite.charger(cfg)["sources"]}
    with fabrique() as s:
        rapps = list(s.scalars(select(Rapprochement)))
        ids = {i for r in rapps for i in (r.a, r.b)}
        cands = {c.id: c for c in s.scalars(select(Candidat).where(Candidat.id.in_(ids)))} if ids else {}
        par_recherche = {rid: mentions.fiabilites_par_jeton(cfg.dossier_recherche(rid), fiabilites) for rid in {r.recherche_id for r in rapps}}
        cartes = [_carte(r, cands[r.a], cands[r.b], nom_source, par_recherche[r.recherche_id]) for r in rapps if r.a in cands and r.b in cands]
    a_examiner = sorted((c for c in cartes if c["etat"] == "a_examiner"), key=lambda c: (c["confiance"], c["id"]))
    tranches = sorted((c for c in cartes if c["etat"] != "a_examiner"), key=lambda c: c["decide_le"] or "", reverse=True)
    return {"a_examiner": a_examiner, "tranches": tranches}


def trancher(cfg: Config, fabrique: sessionmaker[Session], ident: int, action: str, qui: str) -> dict[str, Any]:
    """CONFIRMER : écrit le lien « même entité » des deux côtés (relations des deux fiches). SÉPARER : l'ôte s'il y était, sans rien effacer d'autre."""
    if action not in ("confirme", "separe"):
        raise ValueError("Une décision est « confirmer » ou « séparer ».")
    with fabrique.begin() as s:
        r = s.get(Rapprochement, ident)
        if r is None:
            raise LookupError("Ce rapprochement n'existe pas.")
        a, b = _appliquer(s, r, action, qui)
        s.add(Journal(recherche_id=r.recherche_id, qui=qui, evenement=f"rapprochement_{action}", detail={"rapprochement": r.id, "a": a.nom, "b": b.nom, "confiance": r.confiance}))
    return {"id": ident, "etat": action}
