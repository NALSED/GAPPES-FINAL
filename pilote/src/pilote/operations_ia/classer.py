"""Opération « Classer / catégoriser » (3.8.09) : une catégorie choisie dans une liste donnée par l'utilisateur
(option « Catégories »), jamais une catégorie inventée hors de cette liste."""

from __future__ import annotations

from typing import Any

OPERATION = {
    "id": "classer",
    "nom": "Classer / catégoriser",
    "description": "Choisit une catégorie parmi celles données, pour chaque résultat.",
    "champ_sortie": "categorie_ia",
}


def prompt(resultat: dict[str, Any], options: dict[str, Any]) -> str:
    categories = [c.strip() for c in str(options.get("categories", "")).split(",") if c.strip()] or ["autre"]
    return (
        "Choisis EXACTEMENT une catégorie dans cette liste fermée, et réponds uniquement par son nom, sans "
        f"rien d'autre : {', '.join(categories)}.\n\nRésultat à classer :\n{resultat}"
    )
