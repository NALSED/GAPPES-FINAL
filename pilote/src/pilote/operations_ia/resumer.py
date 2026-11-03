"""Opération « Résumer » (3.8.09) : un résumé court de ce qu'une fiche porte déjà (description, détail trouvé),
jamais un fait nouveau."""

from __future__ import annotations

from typing import Any

OPERATION = {
    "id": "resumer",
    "nom": "Résumer",
    "description": "Un résumé court de ce que la fiche porte déjà.",
    "champ_sortie": "resume_ia",
}


def prompt(resultat: dict[str, Any], options: dict[str, Any]) -> str:
    return (
        "Résume en une phrase, en français, ce que ce résultat décrit déjà. N'invente et n'ajoute aucun fait "
        "qui ne figure pas dans le texte ci-dessous. Réponds uniquement par la phrase, sans préambule.\n\n"
        f"{resultat}"
    )
