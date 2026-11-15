"""En-tête User-Agent des appels aux registres : identifiable, sans adresse de contact écrite dans le code.

Les services publics interrogés (Wikidata, data.gouv.fr…) demandent un User-Agent qui dise qui appelle et comment le joindre.
L'adresse de contact est lue dans la variable d'environnement `GRAPPES_CONTACT` (une adresse de courriel ou une adresse de page),
posée par la personne qui exploite l'outil. Absente : le User-Agent nomme l'outil sans contact.
"""

from __future__ import annotations

import os

VARIABLE = "GRAPPES_CONTACT"


def user_agent(outil: str) -> str:
    """« grappes/0.1 (<outil>; <contact>) python-urllib » ; sans contact déclaré, la parenthèse ne porte que l'outil."""
    contact = " ".join(os.environ.get(VARIABLE, "").split())[:120]
    return f"grappes/0.1 ({outil}{'; ' + contact if contact else ''}) python-urllib"
