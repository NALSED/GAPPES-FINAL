"""Vérification des candidats par les sources « vérifier » (adresse d'un site, liste de sanctions...). Séparé de `executer.py` pour pouvoir
être essayé sans la bibliothèque grappes : il ne reçoit que les candidats, la déclaration du lancement et la fonction d'avancement."""

from __future__ import annotations

import time

CHAMPS_DE_CONCORDANCE = ("ville", "numero", "site")  # A2 (spec 912) : ce qui, en plus du nom, fait une confirmation


def concordance(ligne: dict, rendu: dict) -> dict[str, str]:
    """Compare la fiche et ce que la source a rendu, champ par champ (accord / desaccord / absence), avec la comparaison de l'onglet Tri
    (`rapprochements.comparer`) : aucune seconde règle. Un site se compare par son nom de domaine ; le « numero » d'une vérification est
    souvent l'adresse de la preuve (une capture, une fiche en ligne) : une adresse n'est pas un numéro officiel, elle ne se compare pas."""
    from pilote.lancement import nom_de_domaine
    from pilote.rapprochements import comparer

    numero = str(rendu.get("numero") or "")
    paires = {
        "ville": (str(ligne.get("ville") or ""), str(rendu.get("ville") or "")),
        "numero": (str(ligne.get("numero_officiel") or ""), "" if numero.lower().startswith(("http://", "https://")) else numero),
        "site": (nom_de_domaine(str(ligne.get("site") or "")), nom_de_domaine(str(rendu.get("site") or ""))),
    }
    return {champ: comparer(champ, *paires[champ]) for champ in CHAMPS_DE_CONCORDANCE}


def relever_niveaux(lignes: list[dict]) -> None:
    """A3 (spec 912) : une confirmation au sens de A2 (le nom ET un autre champ concordent) rend le nom « sur ». Rien ne redescend."""
    for ligne in lignes:
        faits = ligne.get("faits") or {}
        if faits.get("niveau") == "a_verifier" and any(v.get("signal") == "confirmation" for v in faits.get("verifications") or []):
            faits["niveau"] = "sur"


def fiabilite_effective(lignes: list[dict], spec: dict) -> None:
    """909 § 1.2.d : une CONFIRMATION par une source de première main relève la fiabilité effective du candidat. A2 (spec 912) : seule une
    confirmation au sens strict compte (le nom et un autre champ concordent) ; un « meme_nom » s'affiche dans la fiche, sans effet."""
    mains = spec.get("mains_sources") or {}
    fiabilites = spec.get("fiabilites_sources") or {}
    for ligne in lignes:
        meilleure = None
        for v in (ligne.get("faits") or {}).get("verifications") or []:
            if v.get("signal") == "confirmation" and mains.get(v.get("source"), "") == "premiere":
                f = fiabilites.get(v.get("source"), "F")
                if meilleure is None or f < meilleure:
                    meilleure = f
        if meilleure is not None:
            ligne.setdefault("faits", {})["fiabilite_effective"] = meilleure


def verifier_candidats(lignes: list[dict], spec: dict, secrets: dict[str, str], doit_s_arreter, limite_source: float, signaler, arret_local=None) -> list[dict]:
    """Appelle chaque source « vérifier » sur chaque candidat à vérifier, APRÈS le classement. Une vérification ne trouve rien et ne compte
    pas comme endroit de plus : elle s'ajoute dans `faits.verifications` ({source, origine, preuve, signal} ; signal = « confirmation »
    ou « alerte »). Une source qui échoue ou dépasse son temps est laissée de côté pour le reste de la recherche ; un arrêt demandé coupe
    la vérification, les candidats restent.

    Rend un BILAN par source ({source, examines, a_verifier, trouves, complete, raison}) : une vérification coupée au milieu ne doit pas
    ressembler à une vérification qui n'a rien trouvé, sinon l'absence de preuve se lirait comme une preuve d'absence."""
    from pilote import adaptateurs

    bilans: list[dict] = []
    arret_general = doit_s_arreter
    for v in spec.get("verificateurs", []):
        doit_s_arreter = arret_local if (v.get("local") and arret_local) else arret_general  # une copie locale n'est pas bornée par la limite d'appels
        source, debut, hors_service = v["source"], time.time(), ""
        cle_ligne = v.get("verifie_sur", "site")  # ce qui sert de clé : l'adresse, le nom ou (enrichir) la ville de la fiche
        enrichit = v.get("fonction") == "enrichir"
        sur_le_nom = cle_ligne == "nom"
        client = adaptateurs.Client(source, doit_s_arreter, signaler=signaler, delai_s=v.get("delai_s", 0.2))
        parametres = {**v.get("parametres", {}), **({"_cle": secrets.get(v["cles_noms"][0], ""), "_cles": {n: secrets.get(n, "") for n in v["cles_noms"]}} if v.get("cles_noms") else {})}
        signaler("prise_debut", prise=source)
        a_verifier = [l for l in lignes if sur_le_nom or l.get(cle_ligne if cle_ligne in ("site", "ville") else "site")]
        faits_ok, examines, coupee = 0, 0, ""
        if v.get("en_amont") is not None:  # posée après certaines sources sur le plan, ou restreinte dans Réglages : elle ne vérifie que les noms que ces sources ont trouvés
            # `trouve_par` garde l'étiquette d'une prise (un flux RSS est « rss-… ») ; `en_amont` parle en sources déclarées : on compare dans la même langue.
            jetons = spec.get("jetons") or {}
            eligibles = a_verifier
            a_verifier = [l for l in eligibles if {jetons.get(t, t) for t in l.get("trouve_par") or []} & set(v["en_amont"])]
            if eligibles and not a_verifier:  # rien d'examiné à cause de la restriction : à dire, sinon « 0 sur 0 » se lit comme une vérification sans trouvaille
                coupee = "aucun nom n'a été trouvé par les sources auxquelles cette vérification est restreinte"
        plafond = int(v.get("parametres", {}).get("max_candidats") or 0)  # source à crédits comptés : on n'examine que les premiers (les mieux classés)
        for ligne in a_verifier:
            if hors_service:
                break
            if doit_s_arreter():
                coupee = "arrêt ou limite d'appels atteinte"
                break
            if plafond and examines >= plafond:
                coupee = f"plafond de {plafond} noms examinés par recherche pour cette source (sa part des appels, ou ses crédits)"
                break
            if time.time() - debut > limite_source:
                coupee = f"limite de temps de la source atteinte ({limite_source:g} s)"
                break
            try:
                trouves = adaptateurs.charger(v["module"]).chercher({"site": ligne.get("site", ""), "nom": ligne["nom"], "quoi": ligne["nom"], "pays": ligne.get("pays", ""), "ville": ligne.get("ville", ""), "fonction": v.get("fonction", "verifier")}, client, parametres)
            except adaptateurs.LimiteAtteinte:
                coupee = "arrêt ou limite d'appels atteinte"
                break
            except Exception as exc:  # noqa: BLE001 - une vérification qui échoue n'arrête ni la recherche ni les autres sources
                hors_service = f"{type(exc).__name__} : {str(exc)[:150]}"
                signaler("source_echec", prise=source, raison=hors_service)
                continue
            examines += 1
            if sur_le_nom and (v.get("parametres") or {}).get("correspondance_exacte"):
                # A6 (spec 912) : un registre interrogé par mots rend aussi des noms approchants. Seul le nom exactement rendu compte (outil
                # existant : `api_json._exactes`, casse, accents et ponctuation à part ; un alias déclaré par le registre est admis).
                from pilote.adaptateurs.api_json import _exactes

                trouves = _exactes([t for t in trouves if t.get("nom")], {"correspondance_exacte": True}, {"nom": ligne["nom"]})
            if trouves and enrichit:
                faits_ok += 1
                champs = {k: trouves[0][k] for k in ("ville", "site", "numero", "pays", "genre", "coordonnees", "detail") if trouves[0].get(k) and trouves[0][k] != ligne.get(k)}
                if champs:  # jamais écraser (règle 1) : l'information en plus vit à côté de la fiche, avec sa source
                    ligne.setdefault("faits", {}).setdefault("enrichissements", []).append({"source": source, "origine": str(trouves[0].get("origine", "")), "champs": champs})
            elif trouves:
                faits_ok += 1
                retenu = next((t for t in trouves if t.get("signal") == "alerte"), None)  # une alerte n'est jamais masquée par un homonyme rangé devant elle
                fait = {}
                if retenu is None and sur_le_nom:
                    # A2 (spec 912) : la source a rendu le NOM. Ce n'est une confirmation que si un autre champ concorde (ville, numéro officiel ou
                    # site) ; sinon c'est « meme_nom » (un homonyme possible), affiché avec ses accords et désaccords, sans effet sur la fiabilité.
                    etats = [concordance(ligne, t) for t in trouves]
                    i = next((k for k, e in enumerate(etats) if "accord" in e.values()), 0)  # parmi plusieurs homonymes, celui qui concorde
                    retenu, fait = trouves[i], {"champs": etats[i]}
                    signal = "confirmation" if "accord" in etats[i].values() else "meme_nom"
                    if str(retenu.get("signal") or "confirmation") != "confirmation":  # « information » et autres signaux propres à la source : gardés
                        signal = str(retenu["signal"])
                else:
                    retenu = retenu or trouves[0]  # vérification sur l'adresse du site : la clé interrogée EST le second champ
                    signal = str(retenu.get("signal") or "confirmation")
                ligne.setdefault("faits", {}).setdefault("verifications", []).append(
                    {"source": source, "origine": str(retenu.get("origine", "")), "preuve": str(retenu.get("numero", "")), "signal": signal, **fait})
        # Aucun nom examiné = la source n'a pas été interrogée : ce n'est pas une réponse. Sans cela, le « ok » levait sa pause et effaçait une panne de la phase de recherche.
        if not hors_service and examines:
            signaler("source_ok", prise=source)
        complete = not hors_service and not coupee
        signaler("prise_fin", prise=source, trouves=faits_ok, noms=0, examines=examines, a_verifier=len(a_verifier),
                 statut="erreur : défaut" if hors_service else f"non appelée : {coupee or 'aucun nom à examiner'}" if not examines else "ok" if complete else "partielle")  # fmt: skip
        bilans.append({"source": source, "fonction": v.get("fonction", "verifier"), "examines": examines, "a_verifier": len(a_verifier), "trouves": faits_ok,
                       "complete": complete, "raison": hors_service or coupee})  # fmt: skip
    return bilans
