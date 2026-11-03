"""Opérations de l'Assistant IA (3.8.09) : AUCUNE liste figée dans le cœur, sur le même principe que les formats de
sortie (`pilote/formats/`) — chaque opération est un petit module qui se déclare avec un dictionnaire `OPERATION`
et une fonction `prompt(resultat, options) -> str` ; ajouter une opération = ajouter un fichier.

Règle de l'outil (02/11/2026, retour de Sednal) : une opération ne touche JAMAIS un champ existant (nom, ville…),
elle ajoute seulement un nouveau champ marqué IA. Une opération qui modifierait un fait reste à décider à part,
le jour où elle est vraiment demandée — ce registre ne l'empêche pas techniquement, mais aucune livrée ici n'en
a besoin."""

from __future__ import annotations

import importlib
import pkgutil
from types import ModuleType
from typing import Any

CHAMPS = {"id", "nom", "description", "champ_sortie"}


def _declaration(m: ModuleType) -> dict[str, Any] | None:
    o = getattr(m, "OPERATION", None)
    if not isinstance(o, dict) or not CHAMPS >= set(o) or not {"id", "nom", "description", "champ_sortie"} <= set(o):
        return None
    if not callable(getattr(m, "prompt", None)):
        return None  # une opération qui ne sait pas construire son invite n'en est pas une
    return {**o, "module": m}


def decouvrir() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for info in sorted(pkgutil.iter_modules(__path__), key=lambda i: i.name):  # type: ignore[name-defined]
        if info.name.startswith("_"):
            continue
        d = _declaration(importlib.import_module(f"{__name__}.{info.name}"))
        if d:
            out[d["id"]] = d
    return out


def vue() -> list[dict[str, Any]]:
    return [{k: v for k, v in d.items() if k != "module"} for d in decouvrir().values()]
