"""A1 (spec 912) : le plan de travail s'applique à TOUS les noms classés, puis la liste est coupée au nombre demandé, et ce que la coupe
retire est dit. Avant, la coupe venait d'abord : un filtre du plan ne voyait que les premiers noms, et la liste sortait plus courte que
demandé alors que de bons noms attendaient juste derrière. Séparé d'`executer.py` pour pouvoir être essayé sans la bibliothèque grappes."""

from __future__ import annotations

from typing import Any

NOMS_DITS = 30  # comme `plan_noms_retires` : le nombre réel, et les trente premiers noms


def plan_puis_coupe(lignes: list[dict], combien: int, appliquer_plan=None) -> tuple[list[dict], dict[str, Any] | None, dict[str, Any] | None]:
    """(noms gardés, bilan du plan ou None, coupe ou None). `lignes` arrive dans l'ordre du classement ; `appliquer_plan(lignes)` rend
    (noms que le plan laisse passer, bilan). La coupe garde les `combien` premiers de ce qui reste. Dans le bilan, `ia` (positions des noms
    que l'Assistant IA doit traiter) est réduit aux noms qui sortent : on ne paie pas pour un nom coupé."""
    bilan = None
    if appliquer_plan is not None:
        lignes, bilan = appliquer_plan(lignes)
    coupe = None
    if combien > 0 and len(lignes) > combien:
        retirees = lignes[combien:]
        coupe = {"retires": len(retirees), "combien": combien, "noms": [str(l.get("nom", "")) for l in retirees[:NOMS_DITS]]}
        lignes = lignes[:combien]
        if bilan is not None and "ia" in bilan:
            bilan = {**bilan, "ia": [k for k in bilan["ia"] if k < combien]}
    return lignes, bilan, coupe
