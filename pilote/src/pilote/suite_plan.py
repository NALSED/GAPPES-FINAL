"""Le plan de travail APPLIQUÉ par le moteur (spécification 08 : « on tire les liens soi-même » — et le moteur obéit).

Deux temps, tous deux sans réseau et sans modèle :
 * `compiler(plan, …)` lit le plan (tuiles + liens) et en tire des consignes : quelles sources partent (celles dont un chemin va de « Ta saisie » à
   « Grappes »), quelles sources de vérification agissent sur les résultats de quelles sources, quelles étapes s'appliquent sur chaque
   branche (filtre, condition, script), quelle langue de requête chaque source reçoit. Ce qui n'est pas appliqué est DIT avec sa raison ;
   un plan incohérent est refusé avant tout appel.
 * `appliquer(lignes, consignes)` joue les étapes sur les noms trouvés. Règle de lecture d'un plan : un nom est gardé si AU MOINS UNE des sources
   qui l'ont trouvé a un chemin jusqu'à « Grappes » dont toutes les étapes le laissent passer. Un nom trouvé par une source qui n'est pas sur le
   plan (page d'un moteur de recherche, par exemple) n'est pas jugé : il est gardé, et compté à part.

Ce module n'importe rien de grappes : il tourne dans le service et dans le pont."""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from pilote import formats as _formats
from pilote.refus import ConfigRefusee

CHAMPS = {
    "nom": "nom", "ville": "ville", "pays": "pays", "genre": "genre_de_chose", "categorie": "genre_de_chose", "type": "genre_de_chose",
    "origine": "genre_source", "site": "site", "numero": "numero_officiel", "numero officiel": "numero_officiel", "fonction": "fonction",
}  # fmt: skip
LANGUES = {
    "francais": "fr", "anglais": "en", "allemand": "de", "espagnol": "es", "italien": "it", "neerlandais": "nl", "portugais": "pt", "polonais": "pl", "russe": "ru",
    "finnois": "fi", "suedois": "sv", "norvegien": "no", "danois": "da", "tcheque": "cs", "estonien": "et", "arabe": "ar", "turc": "tr", "chinois": "zh", "japonais": "ja",
}  # fmt: skip
NON_APPLIQUES = {
    "budget": "le plafond de dépense est celui de Réglages (en crédits) : un budget propre à la recherche n'est pas encore branché",
}  # fmt: skip
MAX_CHEMINS = 300
# Fusion / doublons (3.8.05) : trois crans de sensibilité, sur le modèle des crans de profondeur de recherche —
# mêmes mots (Large/Normal/Strict), remplace le SEUIL fixé en dur dans rapprochements.py.
SEUILS_FUSION = {"large": 0.10, "normal": 0.20, "strict": 0.40}


def norme(t: Any) -> str:
    return re.sub(
        r"[^a-z0-9]+", " ", unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode().lower()
    ).strip()


def codes_langues(texte: str) -> list[str]:
    out = []
    for mot in re.split(r"[,;/]|\bet\b", texte):
        n = norme(mot)
        if not n:
            continue
        code = LANGUES.get(n) or (n if re.fullmatch(r"[a-z]{2,3}", n) else None)
        if not code:
            raise ConfigRefusee(
                f"« {mot.strip()} » n'est pas une langue connue : écris son nom (français, anglais…) ou son code (fr, en…)."
            )
        out.append(code)
    return list(dict.fromkeys(out))


def _niveau_ia(opts_map: dict[str, Any]) -> int:
    """908, point 13 : le niveau du curseur de l'Assistant IA (« Niveau », ex. « 1 — Reformuler »). Le chiffre
    de tête ; absent ou illisible, niveau 1 (le seul branché — jamais un refus sur un réglage ancien)."""
    txt = str(opts_map.get("Niveau", "") or "").strip()
    chiffre = txt.split()[0] if txt else "1"
    return int(chiffre) if chiffre.isdigit() and chiffre in "1234" else 1


def _option(opts: list, indice: int, mot: str = "") -> str:
    """La valeur d'une option de tuile : celle dont le libellé contient `mot`, sinon la n-ième (une tuile copie les options de sa fiche)."""
    for lib, v in opts:
        if mot and mot in norme(lib):
            return str(v)
    return str(opts[indice][1]) if len(opts) > indice else ""


# --- Condition « si » (3.8.03) et Filtre (3.8.06) : le même moteur de lignes de condition pour les deux tuiles.
_COMPARATEURS_MOTS = {
    "est egal a": "egal", "est different de": "different", "ne contient pas": "ne_contient_pas", "contient": "contient",
    "commence par": "commence_par", "finit par": "finit_par", "n est pas vide": "non_vide", "est vide": "vide",
}  # fmt: skip  (l'ordre compte : « ne contient pas » doit matcher avant « contient »)
_LETTRES_FIABILITE = "ABCDEF"  # code Admiralty : A est la meilleure


def _comparateur_de(txt: str) -> str:
    n = norme(txt)
    for mot, cle in _COMPARATEURS_MOTS.items():
        if mot in n:
            return cle
    return "egal"  # repli : le seul comparateur d'avant le 02/11/2026, jamais une erreur sur une donnée ancienne


def _ligne_condition(nom: str, champ_txt: str, comp_txt: str, valeur_txt: str) -> dict[str, Any]:
    champ = norme(champ_txt)
    if champ == "nombre de sources":  # Filtre seulement (3.8.06) : corroboration, pas un champ de candidat
        if not valeur_txt.strip().isdigit():
            raise ConfigRefusee(f"« {nom} » : « Nombre de sources » doit être un nombre.")
        return {"champ": "_corroboration", "comparateur": "min", "valeurs": [valeur_txt.strip()]}
    if champ == "fiabilite minimale":  # Filtre seulement (3.8.06)
        lettre = valeur_txt.strip().upper()[:1]
        if lettre not in _LETTRES_FIABILITE:
            raise ConfigRefusee(f"« {nom} » : « Fiabilité minimale » est une lettre de A à F.")
        return {"champ": "_fiabilite", "comparateur": "min", "valeurs": [lettre]}
    if champ not in CHAMPS:
        raise ConfigRefusee(
            f"« {nom} » : le champ « {champ or '(vide)'} » n'existe pas. Champs : {', '.join(sorted({k for k in CHAMPS if k not in ('type', 'numero officiel', 'categorie')}))}."
        )
    comparateur = _comparateur_de(comp_txt)
    valeurs = [v.strip() for v in re.split(r"[,;]", valeur_txt) if v.strip()]
    if comparateur not in ("vide", "non_vide") and not valeurs:
        raise ConfigRefusee(f"« {nom} » : dis à quoi le champ « {champ} » doit être comparé.")
    return {"champ": CHAMPS[champ], "comparateur": comparateur, "valeurs": valeurs}


def _lignes_conditions(nom: str, opts: list) -> tuple[list[dict[str, Any]], str]:
    """Plusieurs lignes {champ, comparateur, valeurs}, combinées par et/ou (3.8.03). Reconnaît aussi l'ancien
    format à une seule ligne (deux options, « (Si/Garder si) le champ » + « est égal à ») des tuiles déjà
    enregistrées avant cette spécification."""
    brutes = []
    i = 1
    while any(norme(lib) == norme(f"Champ {i}") for lib, _ in opts):
        brutes.append((_option(opts, 0, f"champ {i}"), _option(opts, 0, f"comparateur {i}"), _option(opts, 0, f"valeur {i}")))
        i += 1
    if not brutes:
        brutes = [(_option(opts, 0, "champ"), "est égal à", _option(opts, 1, "egal"))]
    lignes = [_ligne_condition(nom, *b) for b in brutes]
    mode = "ou" if norme(_option(opts, 0, "combinateur")) == "ou" else "et"
    return lignes, mode


def _etapes_conditions(nom: str, opts: list, tuile: str, op: str) -> list[dict[str, Any]]:
    lignes, mode = _lignes_conditions(nom, opts)
    etapes = [{"op": op, "lignes": lignes, "mode": mode, "tuile": tuile, "nom": nom}]
    maximum = _option(opts, 0, "garder au maximum")
    if op == "garder" and maximum.strip().isdigit():  # Filtre seulement (3.8.06) : une troncature, pas une ligne de condition
        etapes.append({"op": "tronquer", "maximum": int(maximum), "tuile": tuile, "nom": nom})
    return etapes


def _genre_outil(o: dict[str, Any]) -> str:
    """Ce que fait un outil : son identifiant s'il est livré, le modèle dont il part s'il est créé, « script » s'il est collé."""
    if o.get("nature") == "script":
        return "script"
    return str(o.get("modele") or o["id"])


def compiler(plan: dict[str, Any], sources: list[dict[str, Any]], outils: list[dict[str, Any]], *, pays_equiv: dict[str, list[str]] | None = None,
             langue_saisie: str | None = None, traduction_disponible: bool = False, ia_disponible: bool = False, rsshub_disponible: bool = False, cfg: Any = None) -> dict[str, Any]:  # fmt: skip
    nodes = {n["id"]: n for n in plan.get("nodes", [])}
    edges = [e for e in plan.get("edges", []) if e["from"] in nodes and e["to"] in nodes]
    par_source = {s["id"]: s for s in sources}
    par_outil = {o["id"]: o for o in outils}
    succ: dict[str, list[dict[str, Any]]] = {i: [] for i in nodes}
    pred: dict[str, list[str]] = {i: [] for i in nodes}
    for e in edges:
        succ[e["from"]].append(e)
        pred[e["to"]].append(e["from"])
    departs = [i for i, n in nodes.items() if n["role"] == "ENTREE"]
    arrivees = {i for i, n in nodes.items() if n["role"] == "GRAPPES"}
    if not departs or not arrivees:
        raise ConfigRefusee("Le plan n'a pas sa tuile « Ta saisie » ou sa tuile « Grappes ».")

    def atteint(depart: list[str], voisins: dict[str, list[str]]) -> set[str]:
        vus, pile = set(), list(depart)
        while pile:
            n = pile.pop()
            for m in voisins.get(n, []):
                if m not in vus:
                    vus.add(m)
                    pile.append(m)
        return vus

    avant = atteint(departs, {i: [e["to"] for e in v] for i, v in succ.items()})  # ce qui part de la saisie
    apres = atteint(list(arrivees), pred)  # ce qui peut arriver aux grappes
    for i in nodes:  # une boucle dans le plan : on ne sait pas dans quel ordre jouer ses étapes
        if i in avant and _dans_un_cycle(i, succ):
            raise ConfigRefusee(
                f"Le plan tourne en rond autour de « {nodes[i]['nom']} » : un lien doit toujours aller vers l'avant."
            )
    utiles = {
        i for i in nodes if (i in avant or i in departs) and (i in apres or i in arrivees)
    }  # sur un chemin de la saisie aux grappes
    ref = lambda i: nodes[i].get("ref")
    # dans l'ordre du plan, jamais dans celui d'un ensemble (aléatoire d'un processus à l'autre) : « une seule tuile jouée,
    # les suivantes ignorées » (Fusion, Attente, Assistant IA) désignait sinon une tuile au hasard (revue 902)
    chemin_sources = [i for i in nodes if i in utiles and ref(i) in par_source]
    chemin_outils = [i for i in nodes if i in utiles and ref(i) in par_outil]
    appliques: list[dict[str, Any]] = []
    non_appliques: list[dict[str, Any]] = []

    def dire_non(i: str, raison: str) -> None:
        non_appliques.append({"tuile": i, "nom": nodes[i]["nom"], "raison": raison})

    # --- quelles sources partent, et lesquelles vérifient quoi
    ancetres_sources = {i: {a for a in atteint([i], pred) if ref(a) in par_source} for i in nodes}
    cherchent, verifient = [], []
    for i in chemin_sources:
        s = par_source[ref(i)]
        if s["role"] in ("VERIFIER", "ENRICHIR"):  # elles ne cherchent pas : elles travaillent sur les noms trouvés avant elles
            verifient.append(
                {
                    "id": s["id"],
                    "tuile": i,
                    "fonction": "enrichir" if s["role"] == "ENRICHIR" else "verifier",
                    "en_amont": sorted(
                        {ref(a) for a in ancetres_sources[i] if par_source[ref(a)]["role"] not in ("VERIFIER", "ENRICHIR")}
                    )
                    or None,
                }
            )
        else:
            cherchent.append(s["id"])
    # --- les étapes de chaque branche : tous les chemins d'une source jusqu'à « Grappes », avec les étapes des tuiles rencontrées
    chemins: list[dict[str, Any]] = []

    def etapes_de(m: str, sortie: dict[str, Any]) -> list[dict[str, Any]]:
        """Ce que la tuile `m` fait aux noms qui la traversent en sortant par le lien `sortie` (une condition n'a pas la même étape selon sa sortie)."""
        o = par_outil.get(ref(m))
        if o is None:
            return []
        node = nodes[m]
        genre = _genre_outil(o)
        opts = node.get("opts") or o.get("options") or []
        if genre == "filtre":
            return _etapes_conditions(node["nom"], opts, m, "garder")
        if genre == "si":
            if sortie.get("label") not in ("oui", "non"):
                raise ConfigRefusee(
                    f"« {node['nom']} » a deux sorties : dis laquelle est « oui » et laquelle est « non » (dans la fenêtre de la tuile)."
                )
            return _etapes_conditions(node["nom"], opts, m, "garder" if sortie["label"] == "oui" else "ecarter")
        if genre == "script":
            return [{"op": "script", "code": o.get("code", ""), "tuile": m, "nom": node["nom"]}]
        if genre == "ia":  # passage sans filtre : marque les noms qui ATTEIGNENT la tuile, les seuls que l'IA traitera (3.8.09)
            return [{"op": "ia", "tuile": m, "nom": node["nom"]}]
        return []

    def visiter(m: str, etapes: list[dict[str, Any]], vu: tuple[str, ...], source: str) -> None:
        if m in arrivees:
            chemins.append({"source": source, "etapes": etapes})
            if len(chemins) > MAX_CHEMINS:
                raise ConfigRefusee(
                    "Le plan a trop de chemins différents entre les sources et « Grappes » : simplifie-le."
                )
            return
        for e in succ[m]:
            if e["to"] in utiles and e["to"] not in vu:
                visiter(e["to"], etapes + etapes_de(m, e), vu + (m,), source)

    for i in chemin_sources:
        if par_source[ref(i)]["role"] not in ("VERIFIER", "ENRICHIR"):
            visiter(i, [], (i,), par_source[ref(i)]["id"])
    # --- la sortie, les outils sans effet réel, ceux qu'on ne branche pas
    formats: list[str] | None = None
    traductions: dict[str, dict[str, Any]] = {}
    fusion: dict[str, Any] | None = None
    attente: dict[str, Any] | None = None
    ia: dict[str, Any] | None = None
    rsshub: list[dict[str, Any]] = []  # 3.8.10 : un site par tuile ; son flux est trouvé au lancement (réseau), pas ici
    budget_alerte: dict[str, Any] | None = None  # 2.3 : le seuil/l'action du Compteur budget, pour l'alerte du Tableau de bord
    requetes: dict[str, list[dict[str, Any]]] = {}  # 909 §3 : qualificatifs ajoutés par source, pour les sources qui les comprennent
    effets: dict[str, str] = {}  # tuile -> effet dans le Tableau de bord (1.1 §5) : lu par ExecuteurGrappes pour « tuile_passee »
    for i in chemin_outils:
        node, o = nodes[i], par_outil[ref(i)]
        genre = _genre_outil(o)
        opts = node.get("opts") or o.get("options") or []
        effets[i] = o.get("effet", "rien")
        if o["etat"] == "off":
            raise ConfigRefusee(f"L'outil « {node['nom']} » est éteint dans Réglages : allume-le, ou retire sa tuile.")
        if genre in ("filtre", "si", "script"):
            appliques.append(
                {"tuile": i, "nom": node["nom"], "texte": "joué sur les résultats de chaque branche où il se trouve"}
            )
        elif genre == "fusion":
            if fusion is not None:
                dire_non(i, "une seule tuile Fusion / doublons est jouée par recherche ; les suivantes sont ignorées")
            else:
                opts_map = {lib: v for lib, v in opts}
                niveau_txt = opts_map.get("Même entité si", "Normal")
                seuil = SEUILS_FUSION.get(norme(niveau_txt), SEUILS_FUSION["normal"])
                garder_txt = opts_map.get("En cas de doublon, garder", "la plus fiable")
                garder_n = norme(garder_txt)
                garder = "recente" if "recente" in garder_n else "premiere" if "premiere" in garder_n else "fiable"
                fusion = {"tuile": i, "seuil": seuil, "garder": garder}
                appliques.append({"tuile": i, "nom": node["nom"], "texte": f"« {niveau_txt} » (seuil {seuil}) ; en cas de doublon confirmé, garde {garder_txt} à l'export"})
        elif genre == "attente":
            if attente is not None:
                dire_non(i, "une seule tuile « Quand une source est à court » est jouée par recherche ; les suivantes sont ignorées")
            else:
                opts_map = {lib: v for lib, v in opts}
                choix = norme(opts_map.get("Quand le quota est atteint", "Sauter cette source, continuer les autres"))
                action = "arreter" if "arreter" in choix else "sauter"
                attente = {"tuile": i, "action": action}
                texte = "arrête toute la recherche" if action == "arreter" else "saute la source à court et continue les autres (comportement déjà par défaut)"
                appliques.append({"tuile": i, "nom": node["nom"], "texte": f"quand une source épuise son quota externe : {texte}"})
        elif genre == "format":
            formats_connus = {f["id"]: f for f in _formats.vue(cfg)}  # le registre réel (3.8.01), plus seulement CSV/JSON en dur
            opts_map = {lib: v for lib, v in opts}
            valeur = norme(opts_map.get("Format de sortie", ""))
            choisis = [f for f in formats_connus if f in valeur.split()]
            if not choisis:
                raise ConfigRefusee(
                    f"« {node['nom']} » : choisis au moins un format de sortie ({', '.join(sorted(f['nom'] for f in formats_connus.values()))})."
                )
            formats = list(dict.fromkeys([*(formats or []), *choisis]))
            noms = [formats_connus[f]["nom"] for f in choisis]
            appliques.append({"tuile": i, "nom": node["nom"], "texte": f"sortie {', '.join(noms)}"})
        elif genre == "traduction":
            _traduction(
                i,
                node,
                opts,
                ancetres_sources,
                nodes,
                par_source,
                cherchent,
                avant,
                pred,
                traductions,
                appliques,
                dire_non,
                langue_saisie,
                traduction_disponible,
            )
        elif genre == "requete_avancee":
            _requete_avancee(i, node, opts, nodes, par_source, pred, requetes, appliques, dire_non)
        elif genre == "boucle":
            dire_non(i, _raison_boucle(node["nom"], opts))
        elif genre == "ia":
            opts_map_ia = {lib: v for lib, v in opts}
            niveau_ia = _niveau_ia(opts_map_ia)
            if ia is not None:
                dire_non(i, "une seule tuile Assistant IA est jouée par recherche ; les suivantes sont ignorées")
            elif not ia_disponible:
                dire_non(i, "l'agent Claude Code n'est pas installé sur cette machine : rien de ce qu'elle produirait n'entre dans une grappe")
            elif niveau_ia > 1:
                # 908, point 13 (retour du 08/11/2026) : le curseur à quatre niveaux existe (options_outils.js),
                # mais seul le niveau 1 (Reformuler) a un mécanisme réel aujourd'hui — les niveaux 2 à 4 touchent
                # le Tri (spec à venir de Sednal), la construction de requêtes et l'extraction par page réelle
                # (5.2), et surtout le garde-fou du niveau 4 (candidat IA à zéro point de confirmation) : rien
                # de tout cela n'est construit, et ce n'est pas deviné ici. Même discipline que la Boucle (9.1).
                dire_non(i, f"le niveau {niveau_ia} de l'Assistant IA n'est pas encore branché dans le moteur — seul le niveau 1 (Reformuler) l'est")
            else:
                from pilote import operations_ia as _operations_ia
                from pilote.suite_ia import EFFORTS

                ops_connues = _operations_ia.decouvrir()
                opts_map = opts_map_ia
                op_id = next((oid for oid, d in ops_connues.items() if norme(d["nom"]) == norme(opts_map.get("Opération", ""))), None)
                if op_id is None:
                    raise ConfigRefusee(
                        f"« {node['nom']} » : choisis une opération connue ({', '.join(sorted(d['nom'] for d in ops_connues.values()))})."
                    )
                effort_txt = norme(opts_map.get("Effort", "") or "par défaut")
                effort = next((v for mot, v in EFFORTS.items() if norme(mot) == effort_txt), None)
                if effort is None:
                    raise ConfigRefusee(f"« {node['nom']} » : l'effort est l'un de : {', '.join(EFFORTS)}.")
                marquer = norme(opts_map.get("Marquer les résultats", "oui")) != "non"
                plafond_txt = str(opts_map.get("Traiter au maximum", "") or "").strip()
                plafond = int(plafond_txt) if plafond_txt.isdigit() else None
                categories = str(opts_map.get("Catégories", "") or "").strip()
                if op_id == "classer" and not categories:
                    raise ConfigRefusee(f"« {node['nom']} » : donne la liste des catégories (séparées par une virgule) — « Classer / catégoriser » ne range rien dans « autre » faute de mieux.")
                ia = {"tuile": i, "operation": op_id, "modele": str(opts_map.get("Modèle", "") or "").strip(), "effort": effort, "marquer": marquer, "plafond": plafond, "categories": categories}
                appliques.append({
                    "tuile": i, "nom": node["nom"],
                    "texte": f"applique « {ops_connues[op_id]['nom']} » aux résultats qui atteignent la tuile"
                    + (f", {plafond} au maximum" if plafond is not None else "")
                    + (" (résultats marqués « IA »)" if marquer else ""),
                })  # fmt: skip
        elif genre == "rsshub":
            site = str({lib: v for lib, v in opts}.get("Site à transformer", "") or "").strip()
            if not rsshub_disponible:
                dire_non(i, "aucune instance RSSHub n'est réglée (suite.rsshub_url dans pilote.yaml)")
            elif not re.fullmatch(r"(https?://)?[\w.-]+\.[a-z]{2,}(/\S*)?", site, re.IGNORECASE):
                raise ConfigRefusee(f"« {node['nom']} » : donne l'adresse du site à transformer (par exemple https://www.exemple.fr/rubrique).")
            else:
                rsshub.append({"tuile": i, "nom": node["nom"], "site": site})
        elif genre == "budget":
            # 2.3 (retour du 08/11/2026) : le plafond propre à la recherche n'est toujours pas appliqué (NON_APPLIQUES,
            # inchangé) — seul son seuil d'ALERTE est désormais extrait, pour que « À partir de … % » et « Prévenir »
            # produisent une vraie ligne dans le Tableau de bord (exécuteur_grappes, à la fin de la recherche).
            opts_map = {lib: v for lib, v in opts}
            seuil_txt = str(opts_map.get("À partir de", "80") or "80").strip().replace(",", ".")
            seuil_pct = float(seuil_txt) if re.fullmatch(r"\d+(\.\d+)?", seuil_txt) else 80.0
            prevenir = norme(opts_map.get("Action", "Prévenir")) != "ne rien faire"
            if "pourcentage" in norme(opts_map.get("Budget maximum", "Montant fixe")):
                pourcentage_txt = str(opts_map.get("Pourcentage du plafond mensuel", "20") or "20").strip().replace(",", ".")
                pourcentage = float(pourcentage_txt) if re.fullmatch(r"\d+(\.\d+)?", pourcentage_txt) else 20.0
                budget_alerte = {"tuile": i, "nom": node["nom"], "type": "pourcentage", "pourcentage": pourcentage, "seuil_pct": seuil_pct, "prevenir": prevenir}
            else:
                montant_txt = str(opts_map.get("Montant (crédits)", "5") or "5").strip().replace(",", ".")
                montant = float(montant_txt) if re.fullmatch(r"\d+(\.\d+)?", montant_txt) else 5.0
                budget_alerte = {"tuile": i, "nom": node["nom"], "type": "montant", "montant": montant, "seuil_pct": seuil_pct, "prevenir": prevenir}
            dire_non(i, NON_APPLIQUES["budget"])
        elif genre in NON_APPLIQUES:
            dire_non(i, NON_APPLIQUES[genre])
        else:
            dire_non(i, "cet outil n'a pas de comportement connu du moteur")
    for v in verifient:
        appliques.append(
            {
                "tuile": v["tuile"],
                "nom": nodes[v["tuile"]]["nom"],
                "texte": ("vérifie " if v["fonction"] == "verifier" else "enrichit ")
                + ("les résultats des sources placées avant elle" if v["en_amont"] else "tous les résultats"),
            }
        )
    ordre = {i: k for k, i in enumerate(nodes)}
    return {
        "sources": sorted(dict.fromkeys(cherchent), key=lambda s: min(ordre[i] for i in chemin_sources if ref(i) == s)), "verificateurs": _verificateurs_uniques(verifient),
        "chemins": chemins, "traductions": traductions, "format": formats, "fusion": fusion, "attente": attente, "ia": ia, "rsshub": rsshub, "budget_alerte": budget_alerte, "requetes": requetes, "effets": effets, "appliques": appliques, "non_appliques": non_appliques,
        "pays_equiv": pays_equiv or {},
    }  # fmt: skip


# Boucle (3.8.04) : seule la boucle « pour chaque » est spécifiée (pas de « tant que », décidé avec Sednal — forcer une
# recherche à atteindre un chiffre irait contre la priorité de grappes, la fiabilité avant le volume). Le réglage se lit
# et se valide ici (origine de la liste, élément à remplacer, maximum de tours) ; ce document le dit encore une fois :
# la relance réelle de la recherche une fois par élément n'est PAS câblée dans l'exécuteur (exécuteur_grappes.py) —
# plusieurs mécanismes du programme (ex. mentions.py::sources_de_la_recherche) supposent un seul dossier de travail par
# recherche, pas un par tour, et le faire sans le revoir risquait une régression silencieuse ailleurs. Noté dans
# QUESTIONS.md pour une session dédiée.
def _raison_boucle(nom: str, opts: list) -> str:
    opts_map = {lib: v for lib, v in opts}
    origine = norme(opts_map.get("Origine de la liste", "Liste collée"))
    base = "répéter une recherche pour chaque élément d'une liste n'est pas encore branché dans le moteur"
    if "fichier" in origine:
        return f"{base} (et la lecture d'un fichier importé ne l'est pas non plus)"
    if "precedente" in origine or "resultat" in origine:
        return f"{base} (et prendre la liste depuis une tuile précédente ne l'est pas non plus)"
    elements = [v.strip() for v in (opts_map.get("Liste") or "").splitlines() if v.strip()]
    return base + (f" ({len(elements)} élément(s) prêt(s) dès que ce sera fait)" if elements else "")


def _verificateurs_uniques(verifient: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Une source de vérification posée sur plusieurs tuiles n'est appelée qu'une fois (sinon chaque nom était payé deux fois), sur l'union de ce que ses tuiles
    couvrent : `None` veut dire « tous les résultats », et une seule tuile sans restriction suffit à l'emporter."""
    par_id: dict[str, dict[str, Any]] = {}
    for v in verifient:
        deja = par_id.get(v["id"])
        if deja is None:
            par_id[v["id"]] = {"id": v["id"], "en_amont": v["en_amont"], "fonction": v["fonction"]}
        elif deja["en_amont"] is None or v["en_amont"] is None:
            deja["en_amont"] = None
        else:
            deja["en_amont"] = sorted({*deja["en_amont"], *v["en_amont"]})
    return list(par_id.values())


def _dans_un_cycle(i: str, succ: dict[str, list[dict[str, Any]]]) -> bool:
    vus, pile = set(), [e["to"] for e in succ[i]]
    while pile:
        n = pile.pop()
        if n == i:
            return True
        if n in vus:
            continue
        vus.add(n)
        pile += [e["to"] for e in succ[n]]
    return False


# « Ne pas traduire » (3.8.02) : mots des presets (la liste fermée côté interface) vers les clés de `suite_traduction.PRESETS`.
_PRESETS_MOTS = {
    "guillemets": "guillemets", "majuscules": "majuscules", "nombres": "nombres_dates", "dates": "nombres_dates",
    "urls": "urls_emails", "mail": "urls_emails", "adresses mail": "urls_emails",
}  # fmt: skip


def mots_vers_presets(mots: list[str]) -> list[str]:
    """Les mots d'option « Ne pas traduire » (un ou plusieurs libellés de presets) vers les clés de `suite_traduction.PRESETS` —
    réutilisé tel quel par la route de test en direct (3.8.02, point 6), pour que la même règle s'applique partout."""
    brut = norme(" ".join(mots))
    trouves: list[str] = []
    for mot, cle in _PRESETS_MOTS.items():
        if mot in brut and cle not in trouves:
            trouves.append(cle)
    return trouves


def _presets_ne_pas_traduire(opts: list) -> list[str]:
    if norme(_option(opts, 3, "proteger")) in ("non", "", "0"):
        return []
    return mots_vers_presets([_option(opts, 2, "ne pas traduire")])


def _sources_apres(i: str, nodes: dict[str, Any], par_source: dict[str, Any], pred: dict[str, list[str]]) -> list[str]:
    """Les tuiles de sources qui cherchent, placées après la tuile `i`. Dans l'ordre du plan, jamais dans celui d'un ensemble (aléatoire d'un processus à l'autre)."""
    succ_de: dict[str, list[str]] = {}
    for n_id in nodes:
        for p in pred[n_id]:
            succ_de.setdefault(p, []).append(n_id)
    descendants: set[str] = set()
    pile = [i]
    while pile:
        for m in succ_de.get(pile.pop(), []):
            if m not in descendants:
                descendants.add(m)
                pile.append(m)
    return [m for m in nodes if m in descendants and nodes[m].get("ref") in par_source and par_source[nodes[m]["ref"]]["role"] not in ("VERIFIER", "ENRICHIR")]


def _traduction(
    i,
    node,
    opts,
    ancetres_sources,
    nodes,
    par_source,
    cherchent,
    avant,
    pred,
    traductions,
    appliques,
    dire_non,
    langue_saisie,
    disponible,
) -> None:
    """Une Traduction AVANT une source traduit la requête vers la langue de cette source (son champ Langue, d'où l'intérêt du champ). Après une
    source, elle traduirait les résultats : pas branché. Et sans reconnaissance d'entités nommées, la protection des noms propres n'est pas possible."""
    sources_apres = _sources_apres(i, nodes, par_source, pred)
    if not sources_apres:
        dire_non(i, "placée après les sources, elle traduirait les résultats : ce n'est pas encore branché")
        return
    if "propre" in norme(_option(opts, 2, "ne pas traduire")):
        dire_non(
            i,
            "« ne pas traduire les noms propres » demande une reconnaissance d'entités nommées, pas encore branchée : décoche cette option pour traduire toute la saisie",
        )
        return
    if not disponible:
        dire_non(i, "aucun moteur de traduction n'est réglé (suite.traduction_url dans pilote.yaml)")
        return
    cibles = codes_langues(_option(opts, 1, "traduire vers"))
    # 7.3 (retour du 08/11/2026) : « Langue d'entrée » est devenue multiple, au sens « détecte uniquement parmi
    # ces langues-là » — la détection reste faite par le moteur (un seul appel, jamais plusieurs langues à la fois),
    # mais restreinte à l'ensemble coché, pour qu'un texte français ne soit pas pris pour du portugais. Rien de
    # coché = aucune restriction, comme avant.
    entree_brut = _option(opts, 0, "entree")
    entree_choisies = [] if norme(entree_brut) in ("", "detecter", "auto") else codes_langues(entree_brut)
    detectee = langue_saisie if (not entree_choisies or langue_saisie in entree_choisies) else None
    # « Détecter » (par défaut) : la langue déjà détectée sur la saisie si elle a réussi et respecte la restriction,
    # sinon « auto » — le moteur de traduction sait lui-même détecter la langue à la volée (3.8.02).
    entree = detectee or "auto"
    presets = _presets_ne_pas_traduire(opts)
    faites = []
    for m in sources_apres:
        s = par_source[nodes[m]["ref"]]
        if s["langue"] in cibles and s["langue"] != entree:
            traductions[s["id"]] = {"tuile": i, "de": entree, "vers": s["langue"], "presets": presets}
            faites.append(s["nom"])
    appliques.append(
        {
            "tuile": i,
            "nom": node["nom"],
            "texte": ("requête traduite pour " + ", ".join(faites))
            if faites
            else f"aucune source après elle ne cherche dans une autre langue que {entree} parmi {', '.join(cibles)}",
        }
    )


# ---------------------------------------------------------------- jouer les étapes


OPERATEURS_DORKING = {
    "limiter a un site domaine": "site", "limiter a un type de fichier": "filetype", "mot dans le titre": "titre",
    "phrase exacte": "phrase", "exclure un mot": "exclure",
}  # fmt: skip
_TYPES_DE_DOCUMENT = {"pdf", "doc", "docx", "odt", "rtf", "txt", "csv", "xls", "xlsx", "ods", "ppt", "pptx", "odp"}


def _valeur_qualificatif(nom: str, qtype: str, v: str) -> str:
    """La valeur libre de la tuile ne doit pas rouvrir ce que le vocabulaire fermé écarte : un seul terme (« x inurl:admin » ajouterait un
    opérateur, « -deux mots » n'exclurait que le premier) et, pour un type de fichier, seulement des documents (ni `env`, ni `sql`…)."""
    if qtype == "phrase":
        if '"' in v:
            raise ConfigRefusee(f"« {nom} » : une phrase exacte ne contient pas de guillemet droit.")
        return v
    if re.search(r'[\s:"]', v):
        raise ConfigRefusee(f"« {nom} » : donne un seul terme, sans espace ni deux-points (par exemple linkedin.com/in/).")
    if qtype == "filetype":
        v = v.removeprefix(".").lower()
        if v not in _TYPES_DE_DOCUMENT:
            raise ConfigRefusee(f"« {nom} » : le type de fichier est un type de document ({', '.join(sorted(_TYPES_DE_DOCUMENT))}).")
    return v


def _requete_avancee(i, node, opts, nodes, par_source, pred, requetes, appliques, dire_non) -> None:
    """909 §3 : une tuile AVANT une source ajoute un qualificatif à sa requête (site, type de fichier, phrase
    exacte, mot exclu). Posée après les sources, elle n'a rien à enrichir : jamais branché (cohérent avec
    Traduction, 3.8.02). Chaque source décide elle-même si elle comprend ce qualificatif (`Declaration.operateurs`) ;
    une source qui ne le comprend pas reçoit la requête sans lui — jamais une syntaxe inventée pour elle."""
    sources_apres = _sources_apres(i, nodes, par_source, pred)
    if not sources_apres:
        dire_non(i, "placée après les sources, elle n'a rien à enrichir : ce n'est pas encore branché")
        return
    type_txt = norme(_option(opts, 0, "type de qualificatif"))
    qtype = OPERATEURS_DORKING.get(type_txt)
    valeur_q = _option(opts, 1, "valeur").strip()
    if qtype is None:
        raise ConfigRefusee(f"« {node['nom']} » : le type de qualificatif « {type_txt or '(vide)'} » n'existe pas. Types : {', '.join(OPERATEURS_DORKING)}.")
    if not valeur_q:
        dire_non(i, "aucune valeur n'est donnée au qualificatif : la tuile ne fait rien")
        return
    valeur_q = _valeur_qualificatif(node["nom"], qtype, valeur_q)
    comprises, ignorees = [], []
    for sid in dict.fromkeys(nodes[m]["ref"] for m in sources_apres):  # une source posée sur deux tuiles part une seule fois : son qualificatif aussi
        s = par_source[sid]
        if qtype in (s.get("operateurs") or []):
            requetes.setdefault(s["id"], []).append({"type": qtype, "valeur": valeur_q})
            comprises.append(s["nom"])
        else:
            ignorees.append(s["nom"])
    appliques.append({
        "tuile": i, "nom": node["nom"],
        "texte": (f"qualificatif « {qtype} : {valeur_q} » ajouté pour : {', '.join(comprises)}" if comprises else f"« {qtype} : {valeur_q} » : aucune source après elle ne comprend ce qualificatif")
        + (f" (ignoré, non compris, par : {', '.join(ignorees)})" if ignorees else ""),
    })  # fmt: skip


def valeur(ligne: dict[str, Any], champ: str) -> str:
    if champ == "fonction":
        return str((ligne.get("faits") or {}).get("fonction") or "")
    return str(ligne.get(champ) or "")


def _egal(v: str, valeurs: list[str], equiv: dict[str, list[str]]) -> bool:
    cibles = {norme(x) for x in valeurs}
    for c in list(cibles):
        cibles |= set(equiv.get(c, ()))
    n = norme(v)
    return n in cibles or any(n in equiv.get(c, ()) for c in cibles)


def _teste_ligne(ligne: dict[str, Any], lc: dict[str, Any], equiv: dict[str, list[str]], fiabilites_sources: dict[str, str] | None) -> bool:
    champ, valeurs = lc["champ"], lc["valeurs"]
    if champ == "_corroboration":  # Filtre (3.8.06) : « trouvé par N sources ou plus »
        return len({s for s in (ligne.get("trouve_par") or [])}) >= int(valeurs[0])
    if champ == "_fiabilite":  # Filtre (3.8.06) : la meilleure fiabilité parmi les sources qui ont trouvé ce nom
        lettres = [(fiabilites_sources or {}).get(s, _LETTRES_FIABILITE[-1]) for s in (ligne.get("trouve_par") or [])]
        meilleure = min(lettres) if lettres else _LETTRES_FIABILITE[-1]  # A est la meilleure, alphabétique
        return meilleure <= valeurs[0]
    v = valeur(ligne, champ)
    nv = norme(v)
    comp = lc["comparateur"]
    if comp == "vide":
        return nv == ""
    if comp == "non_vide":
        return nv != ""
    if comp == "egal":
        return _egal(v, valeurs, equiv)
    if comp == "different":
        return not _egal(v, valeurs, equiv)
    if comp == "contient":
        return any(norme(x) in nv for x in valeurs)
    if comp == "ne_contient_pas":
        return not any(norme(x) in nv for x in valeurs)
    if comp == "commence_par":
        return any(nv.startswith(norme(x)) for x in valeurs)
    return any(nv.endswith(norme(x)) for x in valeurs)  # "finit_par"


def _teste_lignes(ligne: dict[str, Any], lignes_cond: list[dict[str, Any]], mode: str, equiv: dict[str, list[str]], fiabilites_sources: dict[str, str] | None) -> bool:
    resultats = [_teste_ligne(ligne, lc, equiv, fiabilites_sources) for lc in lignes_cond]
    return all(resultats) if mode == "et" else any(resultats)


def _entree_script(ligne: dict[str, Any]) -> dict[str, Any]:
    return {"nom": ligne["nom"], "ville": ligne.get("ville", ""), "pays": ligne.get("pays", ""), "genre": ligne.get("genre_de_chose", ""), "origine": ligne.get("genre_source", ""),
            "site": ligne.get("site", ""), "numero": ligne.get("numero_officiel", ""), "fonction": valeur(ligne, "fonction"), "sources": list(ligne.get("trouve_par") or [])}  # fmt: skip


def appliquer(
    lignes: list[dict[str, Any]], consignes: dict[str, Any], lancer_script=None, fiabilites_sources: dict[str, str] | None = None, jetons: dict[str, str] | None = None
) -> tuple[list[dict[str, Any]], dict[str, Any]]:  # fmt: skip
    """Garde les noms que le plan laisse passer. `lancer_script(code, entree_json) -> {ok, sortie, erreur}` joue un script d'outil dans son bac à sable.
    `fiabilites_sources` (identifiant de source -> lettre A-F) sert au comparateur « Fiabilité minimale » de Filtre (3.8.06).
    `jetons` (étiquette de prise -> identifiant de source) : `trouve_par` garde l'étiquette d'une prise (un flux RSS y est « rss-… »), le plan parle en sources déclarées.
    Rend (noms gardés, bilan) ; le bilan dit, par tuile, combien de noms elle a retirés (et lesquels, en partie), et ce qui n'a pas pu être jugé."""
    import json

    jetons = jetons or {}
    if fiabilites_sources:  # « Fiabilité minimale » lit `trouve_par` : la lettre d'une source vaut aussi pour ses prises
        fiabilites_sources = {**{j: fiabilites_sources[s] for j, s in jetons.items() if s in fiabilites_sources}, **fiabilites_sources}

    def sources_de(ligne: dict[str, Any]) -> set[str]:
        return {jetons.get(t, t) for t in ligne.get("trouve_par") or []}

    equiv = consignes.get("pays_equiv") or {}
    plan_sources = set(consignes.get("sources") or [])
    gardes: set[int] = set()
    retires_par_tuile: dict[str, dict[str, Any]] = {}
    tombes: dict[int, list[tuple[str, str]]] = {}  # nom -> les étapes où il est tombé SUR UNE BRANCHE ; il n'est « retiré » que si aucune branche ne l'a gardé
    erreurs: list[str] = []
    # Compteur par tuile (1.1, §8) : un nom qui traverse la même tuile par plusieurs branches ne compte qu'une fois
    # (ensembles d'index, pas de somme) — « entrées » et « sorties » depuis le début de la recherche.
    par_tuile: dict[str, dict[str, Any]] = {}
    tuile_ia = (consignes.get("ia") or {}).get("tuile")
    atteint_ia: set[int] = set()  # noms qui atteignent la tuile Assistant IA jouée (3.8.09)
    for ch in consignes.get("chemins", []):
        courant = [k for k, ligne in enumerate(lignes) if ch["source"] in sources_de(ligne)]
        for etape in ch["etapes"]:
            pt = par_tuile.setdefault(etape["tuile"], {"nom": etape["nom"], "entrees": set(), "sorties": set()})
            pt["entrees"] |= set(courant)
            if etape["op"] in ("garder", "ecarter"):
                passe = [
                    k
                    for k in courant
                    if _teste_lignes(lignes[k], etape["lignes"], etape["mode"], equiv, fiabilites_sources) == (etape["op"] == "garder")
                ]
            elif etape["op"] == "tronquer":
                passe = courant[: etape["maximum"]]
            elif etape["op"] == "ia":
                passe = courant
                if etape["tuile"] == tuile_ia:
                    atteint_ia |= set(courant)
            else:
                res = (
                    lancer_script(
                        etape["code"], json.dumps([_entree_script(lignes[k]) for k in courant], ensure_ascii=False)
                    )
                    if lancer_script
                    else {"ok": False, "erreur": "aucun bac à sable"}
                )
                rendu = None
                if res["ok"]:
                    try:
                        rendu = json.loads(res["sortie"])
                    except ValueError:  # une sortie illisible ne juge aucun nom : elle ne doit pas faire perdre toute la recherche
                        res = {"ok": False, "erreur": "sa sortie n'est pas un JSON lisible"}
                if not res["ok"]:
                    erreurs.append(
                        f"« {etape['nom']} » : {res.get('erreur', 'le script a échoué')}. Les noms n'ont pas été jugés par ce script."
                    )
                    passe = courant
                else:
                    gardes_noms = {norme(x.get("nom")) for x in rendu if isinstance(x, dict)}
                    passe = [k for k in courant if norme(lignes[k]["nom"]) in gardes_noms]
            pt["sorties"] |= set(passe)
            for k in set(courant) - set(passe):
                tombes.setdefault(k, []).append((etape["tuile"], etape["nom"]))
            courant = passe
        gardes |= set(courant)
    non_attribues = [k for k, ligne in enumerate(lignes) if not (sources_de(ligne) & plan_sources)]
    gardes |= set(non_attribues)
    for k, etapes_tombees in tombes.items():
        if k in gardes:
            continue  # tombé sur une branche mais gardé par une autre : pas retiré, et le journal ne le dit pas retiré
        for tuile, nom in dict.fromkeys(etapes_tombees):
            t = retires_par_tuile.setdefault(tuile, {"nom": nom, "n": 0, "noms": []})
            t["n"] += 1
            if lignes[k]["nom"] not in t["noms"] and len(t["noms"]) < 30:
                t["noms"].append(lignes[k]["nom"])
    gardees = [ligne for k, ligne in enumerate(lignes) if k in gardes]
    rang_garde = [k for k in range(len(lignes)) if k in gardes]
    bilan = {
        "ia": [pos for pos, k in enumerate(rang_garde) if k in atteint_ia],  # positions dans les noms gardés
        "gardes": len(gardees),
        "retires": len(lignes) - len(gardees),
        "non_attribues": len(non_attribues),
        "par_tuile": retires_par_tuile,
        "erreurs": erreurs,
        "tuiles": {tuile: {"nom": v["nom"], "entrees": len(v["entrees"]), "sorties": len(v["sorties"])} for tuile, v in par_tuile.items()},
    }
    return gardees, bilan
