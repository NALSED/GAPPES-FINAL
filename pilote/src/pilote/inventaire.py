"""Inventaire du programme (908, 14.3) : une fonction qui le PARCOURT et rend sa description complète — les
sources, les outils, les formats de sortie, les opérations de l'Assistant IA, les vocabulaires fermés connus,
et les gestes que l'interface permet déjà. C'est le principe déjà écrit en tête de l'ancienne Aide : « tous les
noms de source, de tuile et d'option affichés ici viennent d'un retour de fonction, jamais d'un texte écrit
dans ce fichier ni d'un modèle » — généralisé ici plutôt que répété à la main pour chaque fonction d'Aide.

Aide et l'Assistant IA (14.1/14.2) liront CET inventaire et ne contiendront aucune connaissance en propre : un
11ᵉ outil ou une 80ᵉ source apparaissent tout seuls, personne n'a rien à mettre à jour ici. Le test de
complétude (14.4, `tests/test_inventaire.py`) vérifie que rien n'existe en dehors de ce que cette fonction
décrit."""

from __future__ import annotations

from typing import Any

from pilote.config import Config


def sources(cfg: Config) -> list[dict[str, Any]]:
    """Les déclarations réelles (`config/sources/*.yaml`) : ce qu'une source trouve, consomme, produit, sa
    main et son coût — jamais l'état propre à l'utilisateur (allumée, quota...), qui vit dans `/api/suite/etat`."""
    from pilote.sources import charger_sources

    decls, _ = charger_sources(cfg)
    return [
        {
            "id": d.id, "nom": d.nom, "trouve": d.trouve, "consomme": d.consomme, "produit": d.produit,
            "main": d.main, "cout": "payant" if d.payant else "gratuit", "roles": d.roles, "usages": d.usages,
            "genres": d.genres, "famille": d.famille,
        }
        for d in sorted(decls.values(), key=lambda d: d.id)
    ]  # fmt: skip


def outils(cfg: Config) -> list[dict[str, Any]]:
    """Les outils RÉELLEMENT présents (livrés et ajoutés par l'utilisateur) : `fait`/`recoit`/`renvoie`, le
    genre de modèle (pour relier un outil aux valeurs acceptées de `vocabulaires()`), et ses options actuelles."""
    from pilote import suite

    e = suite.charger(cfg)
    out = []
    for o in e["outils"]:
        genre = o.get("modele") if o["nature"] == "modele" else None
        out.append({
            "id": o["id"], "nom": o["nom"], "nature": o["nature"], "genre": genre, "fait": o["fait"],
            "recoit": o["recoit"], "renvoie": o["renvoie"], "role": o["role"], "effet": o["effet"],
            "options": [lib for lib, _ in o["options"]], "etat": o["etat"],
        })  # fmt: skip
    return out


def formats(cfg: Config) -> list[dict[str, Any]]:
    """Les formats de sortie connus (`pilote.formats.decouvrir`, déjà une découverte — pas une liste tenue à
    la main) : contenus possibles, réglages propres (`besoin`)."""
    from pilote import formats as _formats

    return _formats.vue(cfg)


def operations_ia() -> list[dict[str, Any]]:
    """Les opérations de l'Assistant IA connues (`pilote.operations_ia.vue`, même principe)."""
    from pilote import operations_ia as _operations_ia

    return _operations_ia.vue()


def vocabulaires() -> dict[str, list[str]]:
    """Les vocabulaires fermés connus CÔTÉ MOTEUR — dérivés des constantes réelles de `suite_plan`/`suite_ia`,
    jamais une seconde liste à tenir à jour en parallèle (le risque exact que 10.2/12.2 ont révélé pour le
    registre JS équivalent, `RENDUS_OPTIONS` de `options_outils.js`)."""
    from pilote.suite_ia import EFFORTS
    from pilote.suite_plan import _COMPARATEURS_MOTS, CHAMPS, SEUILS_FUSION

    return {
        "champs_condition": sorted({k for k in CHAMPS if k not in ("type", "numero officiel", "categorie")}),
        "comparateurs_condition": sorted(set(_COMPARATEURS_MOTS.values())),
        "niveaux_fusion": list(SEUILS_FUSION),
        "efforts_ia": list(EFFORTS.values()),
    }


def actions(routes: list[Any] | None = None) -> list[dict[str, str]]:
    """Les gestes que l'interface permet déjà (14.2) : les routes `/api/suite/...` de l'application RÉELLE,
    passées par l'appelant (`app.routes`, déjà construites) — jamais une liste tenue à la main, qui dérive à
    la première route oubliée. `routes` absent (ex. hors d'une application FastAPI montée) : liste vide,
    jamais devinée."""
    def a_plat(rs: list[Any]) -> list[Any]:  # FastAPI imbrique les routes d'un router inclus (`_IncludedRouter`) plutôt que les étaler
        out: list[Any] = []
        for r in rs:
            sous = getattr(r, "original_router", None)
            out.extend(a_plat(sous.routes) if sous is not None else [r])
        return out

    out: list[dict[str, str]] = []
    for r in a_plat(routes or []):
        chemin = getattr(r, "path", "")
        if not isinstance(chemin, str) or not chemin.startswith("/api/suite"):
            continue
        methodes = sorted((getattr(r, "methods", None) or set()) - {"HEAD", "OPTIONS"})
        point = getattr(r, "endpoint", None)
        resume = (point.__doc__ or "").strip().splitlines()[0] if point and point.__doc__ else ""
        for methode in methodes:
            out.append({"methode": methode, "chemin": chemin, "resume": resume})
    return sorted(out, key=lambda a: (a["chemin"], a["methode"]))


def inventaire(cfg: Config, routes: list[Any] | None = None) -> dict[str, Any]:
    return {
        "sources": sources(cfg), "outils": outils(cfg), "formats": formats(cfg),
        "operations_ia": operations_ia(), "vocabulaires": vocabulaires(), "actions": actions(routes),
    }  # fmt: skip
