"""Opération « Extraire des mots-clés » (3.8.09) : quelques mots déjà présents dans le texte de la fiche,
jamais un mot qui n'y figure pas."""

from __future__ import annotations

from typing import Any

OPERATION = {
    "id": "extraire_mots_cles",
    "nom": "Extraire des mots-clés",
    "description": "Quelques mots déjà présents dans le texte de la fiche, qui la résument.",
    "champ_sortie": "mots_cles_ia",
}


def prompt(resultat: dict[str, Any], options: dict[str, Any]) -> str:
    maximum = str(options.get("maximum", "5")).strip() or "5"
    return (
        f"Choisis au plus {maximum} mots ou expressions courtes, DÉJÀ PRÉSENTS dans le texte ci-dessous, qui le "
        "résument le mieux. Réponds uniquement par la liste, séparée par des virgules, sans numérotation.\n\n"
        f"{resultat}"
    )
