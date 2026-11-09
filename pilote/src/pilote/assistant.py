"""Assistant de première installation (fiche 02) : trois étapes dans l'ordre (sources, vérification, sortie). Il ne fait QU'ÉCRIRE les
fichiers de configuration ; ceux-ci restent la référence. Chaque étape peut être rejouée seule depuis Réglages sans toucher aux autres."""

from __future__ import annotations

from typing import Any

from pilote.refus import ConfigRefusee
from pilote.sources import Declaration


def patch_etape(etape: int, p: dict[str, Any], decls: dict[str, Declaration]) -> dict[str, Any]:
    if etape == 1:
        coches = set(p.get("chercher") or [])
        inconnues = [s for s in coches if s not in decls]
        if inconnues:
            raise ConfigRefusee(f"La source « {inconnues[0]} » n'existe pas.")
        patch: dict[str, Any] = {
            "pays": str(p.get("pays", "")).strip().upper(), "presets_coches": list(p.get("presets_coches") or []),
            "sources": {sid: {"chercher": sid in coches} for sid in decls if "chercher" in decls[sid].roles},
        }  # fmt: skip
        if p.get("plafond") is not None:
            patch["budget"] = {"plafond_mensuel_usd": p["plafond"]}
        return patch
    if etape == 2:
        verifier = set(p.get("verifier") or [])
        # 909, point 2.1.c (retour du 09/11/2026) : enrichir a sa propre place dans l'assistant, comme verifier
        # — une source enrichir SEULE (rdap, intelligencex) n'y apparaissait jamais avant ce point.
        enrichir = set(p.get("enrichir") or [])
        inconnues = [s for s in (verifier | enrichir) if s not in decls]
        if inconnues:
            raise ConfigRefusee(f"La source « {inconnues[0]} » n'existe pas.")
        actif = bool(p.get("active", True))
        # le MODE n'est touché que s'il est donné : rejouer cette étape ne doit pas annuler en silence le choix
        # « vérifier aussi avec les sources qui ne font que vérifier », fait dans Réglages (mesuré : il retombait à « memes »).
        verif: dict[str, Any] = {"active": actif}
        if p.get("mode") is not None:
            verif["mode"] = str(p["mode"])
        sources: dict[str, Any] = {sid: {"verifier": actif and sid in verifier} for sid in decls if "verifier" in decls[sid].roles}
        if "enrichir" in p:  # comme le mode : une page qui ne connaît pas encore cette section (ancienne interface) n'éteint pas en silence ce qui a été coché ailleurs
            for sid, d in decls.items():
                if "enrichir" in d.roles:
                    sources[sid] = {**sources.get(sid, {}), "enrichir": actif and sid in enrichir}
        return {"verification": verif, "sources": sources}
    if etape == 3:
        return {"sortie": {"actifs": list(p.get("actifs") or []), "dossier": str(p.get("dossier", "")).strip()}}
    raise ConfigRefusee("Cette étape n'existe pas (1, 2 ou 3).")


def fusion(patches: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for p in patches:
        for k, v in p.items():
            if k == "sources":
                out.setdefault("sources", {})
                for sid, ch in v.items():
                    out["sources"][sid] = {**out["sources"].get(sid, {}), **ch}
            elif isinstance(v, dict) and isinstance(out.get(k), dict):
                out[k] = {**out[k], **v}
            else:
                out[k] = v
    return out
