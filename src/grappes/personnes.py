"""Personne physique ou compte institutionnel : seulement par des indices explicites.

Un compte (X, Instagram) est une personne par défaut. Il devient « institutionnel » (type `group`)
seulement si son nom lisible contient un indice explicite (association, journal, radio, mairie...).
En cas de doute, ou sans nom, on le traite comme une personne (FINAL.md § 9).
"""

from __future__ import annotations

import re

from grappes.semantic.scoring import normalize

DEFAULT_INSTITUTION_HINTS = (
    "association", "assoc", "ministère", "mairie", "ville de", "préfecture", "gouvernement",
    "journal", "quotidien", "gazette", "revue", "magazine", "média", "medias", "presse", "news",
    "radio", "tv", "télévision", "chaîne", "agence", "éditions", "université", "école", "lycée",
    "institut", "fondation", "fédération", "syndicat", "collectif", "coopérative", "ong",
    "société", "entreprise", "compagnie", "musée", "bibliothèque", "hôpital", "club",
    "official", "officiel", "officielle", "ministry", "newspaper", "university", "foundation",
    "association", "agency", "council", "city of", "department", "museum", "library", "company",
)  # fmt: skip


def _words(text: str) -> list[str]:
    return re.sub(r"[^\w]+", " ", normalize(text)).split()


def is_institution(name: str | None, hints: tuple[str, ...] = DEFAULT_INSTITUTION_HINTS) -> bool:
    """Vrai si `name` contient un indice institutionnel (mot entier ou suite de mots entiers)."""
    if not name:
        return False
    words = _words(name)
    padded = f" {' '.join(words)} "
    return any(f" {' '.join(_words(h))} " in padded for h in hints if _words(h))
