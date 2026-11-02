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
    "attente": "faire patienter une recherche quand un quota est atteint n'est pas encore branché : le moteur s'arrête à la limite d'appels",
    "budget": "le plafond de dépense est celui de Réglages (en dollars) : un budget propre à la recherche n'est pas encore branché",
    "ia": "l'Assistant IA ne s'exécute pas encore : rien de ce qu'il produirait n'entre dans une grappe",
    "rsshub": "transformer un site en flux RSS n'est pas encore branché",
}  # fmt: skip
MAX_CHEMINS = 300


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
             langue_saisie: str | None = None, traduction_disponible: bool = False, cfg: Any = None) -> dict[str, Any]:  # fmt: skip
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
    chemin_sources = [i for i in utiles if ref(i) in par_source]
    chemin_outils = [i for i in utiles if ref(i) in par_outil]
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
    for i in chemin_outils:
        node, o = nodes[i], par_outil[ref(i)]
        genre = _genre_outil(o)
        opts = node.get("opts") or o.get("options") or []
        if o["etat"] == "off":
            raise ConfigRefusee(f"L'outil « {node['nom']} » est éteint dans Réglages : allume-le, ou retire sa tuile.")
        if genre in ("filtre", "si", "script"):
            appliques.append(
                {"tuile": i, "nom": node["nom"], "texte": "joué sur les résultats de chaque branche où il se trouve"}
            )
        elif genre == "fusion":
            appliques.append(
                {
                    "tuile": i,
                    "nom": node["nom"],
                    "texte": "le moteur regroupe déjà les doublons ; la règle « même entité si » n'est pas réglable",
                }
            )
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
        elif genre == "boucle":
            dire_non(i, _raison_boucle(node["nom"], opts))
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
        "sources": sorted(dict.fromkeys(cherchent), key=lambda s: min(ordre[i] for i in chemin_sources if ref(i) == s)), "verificateurs": [{"id": v["id"], "en_amont": v["en_amont"], "fonction": v["fonction"]} for v in verifient],
        "chemins": chemins, "traductions": traductions, "format": formats, "appliques": appliques, "non_appliques": non_appliques,
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
    descendants = set()
    pile = [i]
    succ_de = {}
    for n_id in nodes:
        for p in pred[n_id]:
            succ_de.setdefault(p, []).append(n_id)
    while pile:
        for m in succ_de.get(pile.pop(), []):
            if m not in descendants:
                descendants.add(m)
                pile.append(m)
    sources_apres = [
        m
        for m in descendants
        if nodes[m].get("ref") in par_source and par_source[nodes[m]["ref"]]["role"] not in ("VERIFIER", "ENRICHIR")
    ]
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
    entree_txt = norme(_option(opts, 0, "entree"))
    entree = None if entree_txt in ("", "detecter", "auto") else (codes_langues(entree_txt) or [None])[0]
    # « Détecter » (par défaut) : la langue déjà détectée sur la saisie si elle a réussi, sinon « auto » — le moteur de
    # traduction sait lui-même détecter la langue à la volée (3.8.02), la tuile ne refuse plus de fonctionner.
    entree = entree or langue_saisie or "auto"
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
    lignes: list[dict[str, Any]], consignes: dict[str, Any], lancer_script=None, fiabilites_sources: dict[str, str] | None = None
) -> tuple[list[dict[str, Any]], dict[str, Any]]:  # fmt: skip
    """Garde les noms que le plan laisse passer. `lancer_script(code, entree_json) -> {ok, sortie, erreur}` joue un script d'outil dans son bac à sable.
    `fiabilites_sources` (identifiant de source -> lettre A-F) sert au comparateur « Fiabilité minimale » de Filtre (3.8.06).
    Rend (noms gardés, bilan) ; le bilan dit, par tuile, combien de noms elle a retirés (et lesquels, en partie), et ce qui n'a pas pu être jugé."""
    import json

    equiv = consignes.get("pays_equiv") or {}
    plan_sources = set(consignes.get("sources") or [])
    gardes: set[int] = set()
    retires_par_tuile: dict[str, dict[str, Any]] = {}
    tombes: dict[int, list[tuple[str, str]]] = {}  # nom -> les étapes où il est tombé SUR UNE BRANCHE ; il n'est « retiré » que si aucune branche ne l'a gardé
    erreurs: list[str] = []
    for ch in consignes.get("chemins", []):
        courant = [k for k, ligne in enumerate(lignes) if ch["source"] in (ligne.get("trouve_par") or [])]
        for etape in ch["etapes"]:
            if etape["op"] in ("garder", "ecarter"):
                passe = [
                    k
                    for k in courant
                    if _teste_lignes(lignes[k], etape["lignes"], etape["mode"], equiv, fiabilites_sources) == (etape["op"] == "garder")
                ]
            elif etape["op"] == "tronquer":
                passe = courant[: etape["maximum"]]
            else:
                res = (
                    lancer_script(
                        etape["code"], json.dumps([_entree_script(lignes[k]) for k in courant], ensure_ascii=False)
                    )
                    if lancer_script
                    else {"ok": False, "erreur": "aucun bac à sable"}
                )
                if not res["ok"]:
                    erreurs.append(
                        f"« {etape['nom']} » : {res.get('erreur', 'le script a échoué')}. Les noms n'ont pas été jugés par ce script."
                    )
                    passe = courant
                else:
                    gardes_noms = {norme(x.get("nom")) for x in json.loads(res["sortie"]) if isinstance(x, dict)}
                    passe = [k for k in courant if norme(lignes[k]["nom"]) in gardes_noms]
            for k in set(courant) - set(passe):
                tombes.setdefault(k, []).append((etape["tuile"], etape["nom"]))
            courant = passe
        gardes |= set(courant)
    non_attribues = [k for k, ligne in enumerate(lignes) if not (set(ligne.get("trouve_par") or []) & plan_sources)]
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
    bilan = {
        "gardes": len(gardees),
        "retires": len(lignes) - len(gardees),
        "non_attribues": len(non_attribues),
        "par_tuile": retires_par_tuile,
        "erreurs": erreurs,
    }
    return gardees, bilan
