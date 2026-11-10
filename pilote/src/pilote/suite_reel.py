"""Raccord de la suite aux sources RÉELLES de pilote (`config/sources/*.yaml`) : la liste de la suite n'est plus un catalogue à part, c'est une
vue des déclarations. Rien n'est recopié :
 * nom, coût, origine, pays, description, clé requise, quota gratuit viennent de la déclaration (en lecture seule dans la suite) ;
 * allumer / éteindre écrit les cases « chercher » / « vérifier » de Réglages, par la même fonction que l'ancienne page ;
 * l'état (opérationnelle / à vérifier / éteinte) se déduit du dernier test et du voyant de l'ancienne page ;
 * le test est le test LOCAL de l'ancienne page (il ne consomme rien) ;
 * la clé est rangée sous son vrai nom de variable, dans le fichier de clés de pilote ;
 * seul ce que la suite ajoute est gardé dans la surcouche (`etat.json`, clé `surcouche`) : langue, retrait de la liste, rôle et catégorie
   d'affichage. La déclaration n'est jamais modifiée par l'usage."""

from __future__ import annotations

from typing import Any

from pilote import cles, disjoncteur
from pilote import reglages as rg
from pilote.adaptateurs import base_exterieure
from pilote.api_reglages import adaptateur_manquant, voyant
from pilote.config import Config
from pilote.etat_sources import lire as lire_etat
from pilote.presets import domaine_source
from pilote.refus import ConfigRefusee
from pilote.sources import Declaration, charger_sources

USAGE_VERS_CAT = {
    "associations": "assos", "entreprises": "entreprises", "organisations": "orgs", "web": "web", "reseaux_sociaux": "rs", "lieux": "lieux",
    "presse": "presse", "personnalise": "perso", "culture": "lieux",
}  # fmt: skip
CAT_VERS_USAGE = {
    "assos": "associations",
    "entreprises": "entreprises",
    "orgs": "organisations",
    "web": "web",
    "rs": "reseaux_sociaux",
    "lieux": "lieux",
    "presse": "presse",
    "perso": "personnalise",
}
PAYS_AFFICHE = {"GB": "UK", "monde": "Mondial"}
LANGUE_DU_PAYS = {"FR": "fr", "UK": "en", "US": "en", "AU": "en", "NZ": "en", "FI": "fi", "CH": "de"}  # un pays à langue unique ; « Mondial » et « UE » sont multilingues : langue vide = inconnue, jamais « en » par défaut (le contrôle de langue de l'Aide se tait plutôt que de deviner)
FIABILITES = "ABCDEF"  # code Admiralty, axe « fiabilité de la source » (spécification 05) ; l'axe 1–6 (crédibilité d'un fait) n'est pas construit
FIABILITE_DE_LA_CLASSE = {"registre": "B", "encyclo": "C"}  # par défaut : B pour une source officielle, C pour une encyclopédie, D pour le web, la presse, le reste


def fiabilite_par_defaut(d: Declaration) -> str:
    return d.fiabilite or FIABILITE_DE_LA_CLASSE.get(d.origine, "D")  # la déclaration peut la fixer (SIRENE, RNA : registre officiel de première main = A)


class AvertissementRequis(Exception):
    """Allumer cette source demande d'abord de lire un avertissement (prestataire payant, service à risque) : la page le montre, puis redemande."""

    def __init__(self, avertissements: list[dict[str, str]]):
        super().__init__("avertissement")
        self.avertissements = avertissements


def _pays(d: Declaration) -> list[str]:
    return [PAYS_AFFICHE.get(p, p.upper()) for p in d.pays] or ["Mondial"]


def _cats(d: Declaration) -> list[str]:
    cats = [USAGE_VERS_CAT[u] for u in d.usages if u in USAGE_VERS_CAT]
    if d.famille in ("fichier", "base", "python"):
        cats.append("perso")
    return list(dict.fromkeys(cats)) or ["perso"]


def _quota(d: Declaration, e: dict[str, Any], unites: dict[str, float] | None) -> dict[str, Any] | None:
    """Le quota LU, jamais inventé : celui que le fournisseur a rendu au dernier test, sinon le quota gratuit mensuel de la déclaration avec
    les unités réellement consommées ce mois-ci (sans `unites`, pas de chiffre : on ne dit pas « 0 » faute de savoir)."""
    q = e.get("quota") or {}
    if q.get("total") and q.get("restant") is not None:
        return {"utilise": round(q["total"] - q["restant"]), "plafond": round(q["total"]), "unite": "mois"}
    gratuit = float(d.cout.get("gratuit_par_mois", 0) or 0)
    if gratuit > 0 and unites is not None:
        return {"utilise": round(unites.get(d.id, 0.0)), "plafond": round(gratuit), "unite": "mois"}
    return None


def _copie(cfg: Config, d: Declaration) -> dict[str, Any] | None:
    """Pour une source en copie locale : la copie est-elle installée sur cette machine, de quand, de combien de lignes (document 22). Sinon None."""
    if d.mode.get("en_ligne", True) or d.moteur.get("adaptateur") != "fichier_local":
        return None
    from pilote import fichier_local as fl

    base = str((d.moteur.get("parametres") or {}).get("base") or "")
    try:
        m = fl.meta(cfg.dossier_copies, base)
    except fl.BaseLocaleErreur:
        return {"installee": False, "date": "", "lignes": 0}
    return {"installee": True, "date": m.get("importe_le", ""), "lignes": int(m.get("lignes") or 0)}


def vue_source(
    cfg: Config,
    d: Declaration,
    reg: dict[str, Any],
    e: dict[str, Any],
    sur: dict[str, Any],
    unites: dict[str, float] | None,
    pause: dict[str, Any] | None = None,  # 1.1 §3.2 : la raison, pour le Tableau de bord — None si la source n'est pas en pause
) -> dict[str, Any]:
    ch = rg.choix_source(reg, d)
    allumee = bool(ch["chercher"] or ch["verifier"] or ch["enrichir"])
    manquant = adaptateur_manquant(d)
    couleur, mot = voyant(cfg, d, e, manquant, rg.parametres_donnes(reg, d.id))
    teste = e.get("statut") == "ok"
    if sur.get("nouvelle") and not teste:
        etat = "warn"  # une source que la suite vient d'ajouter démarre « à vérifier » jusqu'à son premier test réussi (spec 05), même éteinte
    elif not allumee:
        etat = "off"
    elif couleur == "ok" and teste:
        etat = "ok"
    else:
        etat = "warn"  # jamais testée, test échoué, clé absente, en pause, adaptateur manquant : « à vérifier »
    copie = _copie(cfg, d)
    base_ext = d.moteur.get("adaptateur") == "base_exterieure"  # Accès : API / Copie locale / Base extérieure (ni quota, ni date de copie, mais une adresse de machine et des identifiants)
    acces = "base_exterieure" if base_ext else "copie_locale" if copie is not None else "api"
    p_ext = (d.moteur.get("parametres") or {}) if base_ext else {}
    machine = f"{p_ext.get('hote', '')}:{p_ext.get('port') or base_exterieure.SYSTEMES.get(str(p_ext.get('systeme', '')), '')}/{p_ext.get('base_nom', '')}" if base_ext else ""
    if copie is not None and not copie["installee"] and etat != "off":
        etat = "warn"  # une source en copie locale sans sa copie ne peut rien rendre : « à vérifier », jamais « ok »
    cats = _cats(d)
    pays = _pays(d)
    role = sur.get("role") or ("CHERCHER" if "chercher" in d.roles else "VERIFIER" if "verifier" in d.roles else "ENRICHIR")
    tests = []
    if e.get("teste_le"):
        tests.append(
            f"{e['teste_le'][:10]} · {'test local réussi' if teste else 'échec : ' + str(e.get('raison', ''))}"
        )
    return {
        "id": d.id, "nom": d.nom, "cat": sur.get("cat") if sur.get("cat") in CAT_VERS_USAGE else cats[0], "cats": cats, "role": role,
        "cout": "payant" if d.payant else "gratuit", "fiabilite": sur.get("fiabilite") if sur.get("fiabilite") in tuple(FIABILITES) else fiabilite_par_defaut(d), "fiabilite_choisie": sur.get("fiabilite") in tuple(FIABILITES), "pays": pays[0], "pays_codes": pays,
        "langue": sur.get("langue") or LANGUE_DU_PAYS.get(pays[0], ""), "etat": etat, "quota": _quota(d, e, unites), "description": d.description,
        "retiree": bool(sur.get("retiree")), "test_reussi": teste, "tests": tests, "declaree": True, "cle_requise": bool(d.cles), "cles_noms": d.cles,
        "parametres_attendus": d.parametres, "parametres": rg.parametres_donnes(reg, d.id),
        "cle": bool(d.cles) and cles.toutes_presentes(cfg, d.cles), "voyant": mot, "domaine": domaine_source(d), "auto_heberge": d.mode.get("auto_heberge", False), "chercher": ch["chercher"], "verifier": ch["verifier"], "enrichir": ch["enrichir"],
        # 909, point 1.1.b : les rôles RÉELLEMENT déclarés (une source peut en avoir plusieurs) — la fiche en fait des cases indépendantes, plus un seul rôle qui en masque les autres.
        "roles_declares": [r.upper() for r in d.roles],
        "emoji": "emoji" in d.consomme, "acces": acces, "machine": machine, "copie": copie, "peut_chercher": "chercher" in d.roles, "verifie_sur": d.verifie_sur if "adaptateur" in d.moteur else "", "avertissement": d.avertissement, "adaptateur_manquant": manquant,
        "operateurs": list(d.operateurs),  # 909 §3 : qualificatifs de Requête avancée que cette source comprend, pour que le plan sache à qui les envoyer
        "en_pause": {"raison": pause["raison"], "reprise_dans_s": disjoncteur.reprise_dans_s(pause)} if pause else None,
    }  # fmt: skip


def sources(cfg: Config, surcouche: dict[str, Any], unites: dict[str, float] | None = None) -> list[dict[str, Any]]:
    decls, _ = charger_sources(cfg)
    reg, _ = rg.charger_tolerant(cfg)
    etats = lire_etat(cfg)
    pauses = disjoncteur.en_pause(cfg, list(decls))  # un seul calcul pour toutes les sources (1.1 §3.2)
    ordre = {c: i for i, c in enumerate(CAT_VERS_USAGE)}
    vues = [
        vue_source(
            cfg,
            d,
            reg,
            etats.get(d.id) or {},
            surcouche.get(d.id) if isinstance(surcouche.get(d.id), dict) else {},
            unites,
            pauses.get(d.id),
        )
        for d in decls.values()
    ]
    return sorted(vues, key=lambda s: (ordre.get(s["cat"], 99), s["nom"].lower()))


def declaration(cfg: Config, ident: str) -> Declaration:
    decls, _ = charger_sources(cfg)
    if ident not in decls:
        raise ConfigRefusee(f"La source « {ident} » n'existe pas.")
    return decls[ident]


def allumer(cfg: Config, ident: str, allumee: bool, confirme: bool = False) -> None:
    """Allume ou éteint par les cases de Réglages (la même fonction que l'ancienne page : mêmes refus, même verrou, mêmes avertissements)."""
    from pilote import presets

    d = declaration(cfg, ident)
    decls, _ = charger_sources(cfg)
    if allumee:
        if adaptateur_manquant(d):
            raise ConfigRefusee(f"La source « {d.nom} » demande un adaptateur : elle ne peut pas être allumée.")
        e = lire_etat(cfg).get(ident) or {}
        if e.get("statut") == "echec":
            raise ConfigRefusee(
                f"La source « {d.nom} » a échoué à son test ({e.get('raison', 'raison inconnue')}) : elle ne peut pas être allumée tant que le test ne passe pas."
            )
    # 909, point 1.1.c (retour du 09/11/2026) : BUG — l'exclusion « verifier seulement si chercher est absent »
    # remettait silencieusement « verifier » à faux, pour toujours, sur une source chercher+verifier (36 sur
    # 79 : wikidata, ror...) rallumée depuis ce bouton. Chaque rôle déclaré suit maintenant « allumee » pour
    # lui-même, indépendamment des autres — plus d'exclusion mutuelle inventée.
    patch: dict[str, Any] = {
        "id": ident,
        "chercher": allumee and "chercher" in d.roles,
        "verifier": allumee and "verifier" in d.roles,
        "enrichir": allumee and "enrichir" in d.roles,
    }
    if not allumee:
        patch.update(chercher=False, verifier=False, enrichir=False)
    requis = rg.avertissements_requis(rg.charger(cfg), decls, {"source": patch})
    if requis and not confirme:
        raise AvertissementRequis(requis)
    if requis:
        patch_global = {
            "source": patch,
            "avertissements_vus": sorted(
                {*rg.charger(cfg).get("avertissements_vus", []), *(a["source"] for a in requis)}
            ),
        }
    else:
        patch_global = {"source": patch}
    rg.appliquer(cfg, decls, presets.ids_connus(cfg), patch_global)


def definir_role(cfg: Config, ident: str, role: str, actif: bool, confirme: bool = False) -> None:
    """909, point 1.1.b (retour du 09/11/2026) : une case INDÉPENDANTE par rôle déclaré (chercher, verifier,
    enrichir) — contrairement à `allumer()`/`eteindre()`, qui restent le raccourci « tous les rôles à la
    fois », celle-ci n'en touche qu'un, sans modifier les autres (`reglages.appliquer` fusionne par clé,
    jamais un remplacement complet). Mêmes refus et même avertissement que `allumer()`, quel que soit le rôle."""
    from pilote import presets

    if role not in ("chercher", "verifier", "enrichir"):
        raise ConfigRefusee("Le rôle est chercher, verifier ou enrichir.")
    d = declaration(cfg, ident)
    decls, _ = charger_sources(cfg)
    if actif:
        if role not in d.roles:
            verbe = "chercher" if role == "chercher" else "vérifier" if role == "verifier" else "enrichir"
            raise ConfigRefusee(f"La source « {d.nom} » ne peut pas servir à {verbe}.")
        if adaptateur_manquant(d):
            raise ConfigRefusee(f"La source « {d.nom} » demande un adaptateur : elle ne peut pas être allumée.")
        e = lire_etat(cfg).get(ident) or {}
        if e.get("statut") == "echec":
            raise ConfigRefusee(
                f"La source « {d.nom} » a échoué à son test ({e.get('raison', 'raison inconnue')}) : elle ne peut pas être allumée tant que le test ne passe pas."
            )
    patch: dict[str, Any] = {"id": ident, role: actif}
    requis = rg.avertissements_requis(rg.charger(cfg), decls, {"source": patch})
    if requis and not confirme:
        raise AvertissementRequis(requis)
    if requis:
        patch_global = {
            "source": patch,
            "avertissements_vus": sorted(
                {*rg.charger(cfg).get("avertissements_vus", []), *(a["source"] for a in requis)}
            ),
        }
    else:
        patch_global = {"source": patch}
    rg.appliquer(cfg, decls, presets.ids_connus(cfg), patch_global)


def tester(cfg: Config, ident: str) -> dict[str, Any]:
    from pilote import tests_source

    return tests_source.tester(cfg, declaration(cfg, ident))


# 3.3 (retour du 08/11/2026) : le test RÉEL (fiche 11) existait déjà, entièrement codé, mais seulement exposé par
# les routes de l'ancienne page (`api_reglages.py`) — portage, pas une écriture : même logique (`tests_source`),
# même coût effectif de Réglages (`rg.choix_source`), depuis `/suite`.
def prix_test_reel(cfg: Config, ident: str, unites_deja: float = 0.0) -> dict[str, Any]:
    """Le PRIX du test réel, dit avant le clic. N'appelle rien."""
    from pilote import tests_source

    d = declaration(cfg, ident)
    reg, _ = rg.charger_tolerant(cfg)
    cout = rg.choix_source(reg, d)["cout"]
    return {"nom": d.nom, "avertissement": d.avertissement, "cout": cout, **tests_source.prix_du_test(d, cout, unites_deja)}


def test_reel(cfg: Config, ident: str, mot: str) -> dict[str, Any]:
    """Facultatif : UNE vraie requête. L'appelant (API) confirme le prix et vérifie le plafond mensuel avant d'appeler ceci."""
    from pilote import tests_source

    d = declaration(cfg, ident)
    reg, _ = rg.charger_tolerant(cfg)
    cout = rg.choix_source(reg, d)["cout"]
    return {**tests_source.test_reel(cfg, d, mot, cout), "nom": d.nom, "cout": cout}


def ecrire_cle(cfg: Config, ident: str, valeurs: dict[str, str]) -> None:
    """Une valeur par nom de variable (`Declaration.cles` — Reddit en déclare deux). Ignore une valeur vide :
    on peut en remplir une seule sans effacer l'autre (03/11/2026, retour de Sednal : 3.6)."""
    d = declaration(cfg, ident)
    if not d.cles:
        raise ConfigRefusee(f"« {d.nom} » n'a pas de clé d'API.")
    inconnues = sorted(set(valeurs) - set(d.cles))
    if inconnues:
        raise ConfigRefusee(f"« {d.nom} » n'a pas de clé nommée « {inconnues[0]} ».")
    for nom, valeur in valeurs.items():
        if valeur:
            cles.ecrire(cfg, nom, valeur)


def definir_parametres(cfg: Config, ident: str, parametres: dict[str, Any]) -> None:
    """Les réglages non-secrets propres à une source (ex. adresse du portail CKAN) : même mécanisme que `allumer`, sur
    le même patch « source » de Réglages — la suite n'a pas sa propre copie de ces valeurs, elle écrit la déclaration
    partagée avec l'ancienne page (02/11/2026, même champ manquant des deux côtés : retour de Sednal)."""
    from pilote import presets

    declaration(cfg, ident)  # refuse une source inconnue
    decls, _ = charger_sources(cfg)
    rg.appliquer(cfg, decls, presets.ids_connus(cfg), {"source": {"id": ident, "parametres": parametres}})


def ajouter_api(cfg: Config, d: dict[str, Any]) -> str:
    """AJOUTER une source : sa déclaration est écrite par la même fonction que l'ancienne page Ajout (type « API »), puis son test local
    tourne. Elle est enregistrée ÉTEINTE ; elle ne s'allume qu'après un test réussi. Les autres types (MCP, fichier, base, programme local,
    flux RSS) gardent leur voie dans l'ancienne page Ajout."""
    from pilote import sources_ajout

    def t(k: str) -> str:
        v = d.get(k, "")
        return v.strip() if isinstance(v, str) else ""

    cat = d.get("cat")
    if cat not in CAT_VERS_USAGE:
        raise ConfigRefusee("Choisis la catégorie de la source.")
    if d.get("role") not in ("CHERCHER", "VERIFIER", "ENRICHIR", "CATALOGUE", "OUTIL", "RAPPROCHER"):
        raise ConfigRefusee("Choisis le rôle de la source.")
    if not t("url"):
        raise ConfigRefusee("Donne l'adresse de la source (https://…).")
    if not t("champ_nom"):
        raise ConfigRefusee("Dis quel champ de la réponse contient le NOM.")
    if not t("parametre_requete"):
        raise ConfigRefusee("Dis sous quel nom la source reçoit ce qu'on cherche (par exemple q).")
    cout: dict[str, Any] = {}
    if d.get("cout") == "payant":
        try:
            prix = float(str(d.get("tarif", "")).replace(",", "."))
        except ValueError:
            prix = 0.0
        if prix <= 0:
            raise ConfigRefusee(
                "Une source payante demande son prix par appel, en dollars (un nombre supérieur à zéro)."
            )
        cout = {"vers_dollar": prix, "par_appel": 1, "unite": "appel"}
    pays = t("pays")
    spec: dict[str, Any] = {
        "nom": t("nom"), "url": t("url"), "parametre_requete": t("parametre_requete"), "champs": {"nom": t("champ_nom")}, "liste": t("liste"),
        "usages": [CAT_VERS_USAGE[cat]], "main": "seconde", "cout": cout,  # une source ajoutée ici est de seconde main : elle ne compte jamais comme un endroit de plus tant qu'on ne l'a pas déclarée autrement
       
        "pays": [{"UK": "GB", "Mondial": "monde"}.get(pays, pays)] if pays else ["monde"], "description": t("description") or f"Source ajoutée par l'utilisateur ({t('nom')}).",
        "roles": ["verifier"] if d.get("role") == "VERIFIER" else ["chercher"],
    }  # fmt: skip
    if d.get("exemple") not in (None, ""):
        spec["exemple"] = d[
            "exemple"
        ]  # la réponse que l'utilisateur a vue : le test local la lit, il n'appelle jamais le service
    if t("cle_valeur"):
        spec.update(cle_valeur=t("cle_valeur"), auth={"type": t("auth") or "bearer"})
    decl, _ = sources_ajout.enregistrer(cfg, "api", spec)
    return decl.id


def _commun_ajout(d: dict[str, Any]) -> dict[str, Any]:
    """Les champs partagés par tous les types de source ajoutée depuis `/suite` (905 §2) : catégorie, rôle, nom,
    pays, description, coût — la même validation que `ajouter_api`, factorisée pour ne pas la répéter six fois."""

    def t(k: str) -> str:
        v = d.get(k, "")
        return v.strip() if isinstance(v, str) else ""

    cat = d.get("cat")
    if cat not in CAT_VERS_USAGE:
        raise ConfigRefusee("Choisis la catégorie de la source.")
    if d.get("role") not in ("CHERCHER", "VERIFIER", "ENRICHIR", "CATALOGUE", "OUTIL", "RAPPROCHER"):
        raise ConfigRefusee("Choisis le rôle de la source.")
    if not t("nom"):
        raise ConfigRefusee("Donne un nom à la source.")
    pays = t("pays")
    return {
        "nom": t("nom"),
        "usages": [CAT_VERS_USAGE[cat]],
        "main": "seconde",
        "pays": [{"UK": "GB", "Mondial": "monde"}.get(pays, pays)] if pays else ["monde"],
        "description": t("description") or f"Source ajoutée par l'utilisateur ({t('nom')}).",
        "roles": ["verifier"] if d.get("role") == "VERIFIER" else ["chercher"],
    }


def ajouter_mcp(cfg: Config, d: dict[str, Any]) -> str:
    """AJOUTER une source de type serveur MCP (905 §2) : même modèle que `ajouter_api`, l'adaptateur générique
    `mcp_generique` de `sources_ajout` fait le travail, rien de nouveau à écrire."""
    from pilote import sources_ajout

    def t(k: str) -> str:
        v = d.get(k, "")
        return v.strip() if isinstance(v, str) else ""

    if not t("mcp"):
        raise ConfigRefusee("Donne l'adresse du serveur MCP (https://…).")
    if not t("outil"):
        raise ConfigRefusee("Dis quel outil du serveur appeler.")
    spec = {
        **_commun_ajout(d),
        "mcp": t("mcp"), "outil": t("outil"), "champs": {"nom": t("champ_nom")} if t("champ_nom") else {},
        "liste": t("liste"), "cle_valeur": t("cle_valeur"),
    }  # fmt: skip
    if d.get("exemple") not in (None, ""):
        spec["exemple"] = d["exemple"]
    decl, _ = sources_ajout.enregistrer(cfg, "mcp", spec)
    return decl.id


def ajouter_fichier(cfg: Config, d: dict[str, Any]) -> str:
    """AJOUTER une source de type fichier local (905 §2) : même modèle que `ajouter_api`, sur l'adaptateur
    générique `api_json`/`fichier` de `sources_ajout`."""
    from pilote import sources_ajout

    def t(k: str) -> str:
        v = d.get(k, "")
        return v.strip() if isinstance(v, str) else ""

    if not t("chemin"):
        raise ConfigRefusee("Donne le chemin du fichier.")
    if not t("champ_nom"):
        raise ConfigRefusee("Dis quel champ ou quelle colonne contient le NOM.")
    spec = {
        **_commun_ajout(d),
        "chemin": t("chemin"), "format": t("format"), "delimiteur": t("delimiteur"),
        "champs": {"nom": t("champ_nom")}, "liste": t("liste"),
    }  # fmt: skip
    decl, _ = sources_ajout.enregistrer(cfg, "fichier", spec)
    return decl.id


def ajouter_base(cfg: Config, d: dict[str, Any]) -> str:
    """AJOUTER une source de type base SQLite locale (905 §2), sur l'adaptateur générique `base_sql`."""
    from pilote import sources_ajout

    def t(k: str) -> str:
        v = d.get(k, "")
        return v.strip() if isinstance(v, str) else ""

    if not t("base"):
        raise ConfigRefusee("Donne le chemin du fichier de base.")
    if not t("requete"):
        raise ConfigRefusee("Donne la requête SQL qui rend les noms.")
    spec = {**_commun_ajout(d), "base": t("base"), "requete": d.get("requete"), "mot_essai": t("mot_essai")}
    decl, _ = sources_ajout.enregistrer(cfg, "base", spec)
    return decl.id


def ajouter_base_exterieure(cfg: Config, d: dict[str, Any]) -> str:
    """AJOUTER une base extérieure (PostgreSQL/MySQL, 905 §2) : identifiants rangés dans le fichier de clés,
    jamais dans la déclaration versionnée (même garde-fou que `sources_ajout._base_exterieure`)."""
    from pilote import sources_ajout

    def t(k: str) -> str:
        v = d.get(k, "")
        return v.strip() if isinstance(v, str) else ""

    if t("systeme").lower() not in ("postgresql", "mysql"):
        raise ConfigRefusee("Le système doit être PostgreSQL ou MySQL.")
    if not t("hote") or not t("base_nom"):
        raise ConfigRefusee("Donne l'adresse de la machine et le nom de la base.")
    spec = {
        **_commun_ajout(d), "systeme": t("systeme"), "hote": t("hote"), "port": d.get("port") or "",
        "base_nom": t("base_nom"), "utilisateur": t("utilisateur"), "mot_de_passe": d.get("mot_de_passe") or "",
        "requete": d.get("requete"), "mot_essai": t("mot_essai"),
    }  # fmt: skip
    decl, _ = sources_ajout.enregistrer(cfg, "base_exterieure", spec)
    return decl.id


def ajouter_programme(cfg: Config, d: dict[str, Any]) -> str:
    """AJOUTER un programme local (905 §2) : même module `programme_local` que l'ancienne page Ajout, rien
    réécrit — un programme qui lit un JSON sur l'entrée standard et rend une liste de noms sur la sortie."""
    from pilote import programme_local

    def t(k: str) -> str:
        v = d.get(k, "")
        return v.strip() if isinstance(v, str) else ""

    commande = [str(c) for c in d.get("commande") or [] if str(c).strip()]
    if not commande:
        raise ConfigRefusee("Indique la commande qui lance le programme.")
    spec = {**_commun_ajout(d), "commande": commande, "delai_s": d.get("delai_s"), "exemple": d.get("exemple")}
    decl, _ = programme_local.enregistrer(cfg, spec)
    return decl.id


### Flux RSS/OPML (905 §2) : rien à ajouter ici — `/suite` appelle directement les routes déjà montées de la
### page Presse (`/api/flux-rss`, `/api/flux-rss/opml`), même backend (`flux_rss.py`), jamais réécrit. Pas une
### Declaration (ni catégorie, ni rôle, ni surcouche) : ça n'a pas sa place dans `ajouter_source`/`TYPES_AJOUT`.
