"""Assistant IA (3.8.09) : applique une opération (voir `operations_ia/`) à un résultat déjà collecté, en appelant
en silence l'agent Claude Code déjà installé et connecté par abonnement Pro/Max — PAS une clé d'API, PAS de
facturation séparée (vérifié auprès de la documentation officielle : un abonnement Pro/Max ne donne pas accès à
l'API classique, mais l'agent s'y connecte). Le même mécanisme que momo utilise déjà pour les tâches mécaniques
(`/areas/agent-ia.md`), adapté à .115.

Règle de l'outil : jamais un fait inventé en silence. Si l'agent ne répond pas, ou répond quelque chose
d'inexploitable, une erreur claire est levée — l'appelant garde le résultat sans le champ IA, et le dit.

Ce que l'IA produit est rangé dans `faits["ia"]` (champ de sortie de l'opération -> texte), jamais dans une
colonne de la fiche : la donnée IA ne se mêle pas aux faits trouvés, et la marque (`faits["ia_marque"]`) la suit
jusqu'à l'export (spécification 10, règle 1)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

DELAI_S = 60
# Effort de raisonnement (`claude -p … --effort <niveau>`, vérifié sur .250 le 03/11/2026) : mot affiché -> valeur.
EFFORTS = {"par défaut": "", "faible": "low", "moyen": "medium", "élevé": "high", "très élevé": "xhigh", "maximal": "max"}


def chemin_agent() -> str | None:
    """L'agent Claude Code : sur le PATH, sinon à son emplacement d'installation par défaut (`~/.local/bin/claude`).
    Un service systemd n'a pas `~/.local/bin` dans son PATH : sans ce repli, chaque appel échouait sur .115."""
    trouve = shutil.which("claude")
    if trouve:
        return trouve
    defaut = Path.home() / ".local" / "bin" / "claude"
    return str(defaut) if defaut.is_file() else None


def disponible() -> bool:
    return chemin_agent() is not None


def commande(modele: str, prompt: str, effort: str = "") -> list[str]:
    """La ligne de commande silencieuse (`claude -p "…" --model <modèle> --effort <niveau>`), isolée pour être
    testée sans lancer de processus réel."""
    cmd = [chemin_agent() or "claude", "-p", prompt]
    if modele:
        cmd += ["--model", modele]
    if effort:
        cmd += ["--effort", effort]
    return cmd


def demander(modele: str, prompt: str, effort: str = "") -> str:
    """Le texte renvoyé par l'agent. Lève OSError si l'agent n'est pas installé ou ne répond pas, ValueError s'il
    rend une sortie vide — jamais un fait inventé en silence."""
    try:
        p = subprocess.run(commande(modele, prompt, effort), capture_output=True, text=True, timeout=DELAI_S, check=False)
    except FileNotFoundError as exc:
        raise OSError("l'agent Claude Code n'est pas installé sur cette machine (introuvable sur le PATH)") from exc
    except subprocess.TimeoutExpired as exc:
        raise OSError(f"l'agent Claude Code a dépassé {DELAI_S} secondes") from exc
    if p.returncode != 0:
        derniere = (p.stderr.strip().splitlines() or ["il s'est arrêté sans message"])[-1][:200]
        raise OSError(f"l'agent Claude Code n'a pas pu répondre : {derniere}")
    sortie = p.stdout.strip()
    if not sortie:
        raise ValueError("l'agent Claude Code n'a rien rendu")
    return sortie


def appliquer(operation: dict, resultat: dict, options: dict, modele: str = "", effort: str = "") -> str:
    """Le texte de `operation['champ_sortie']` pour ce résultat. Ne modifie resultat nulle part."""
    return demander(modele, operation["module"].prompt(resultat, options), effort)


def appliquer_lignes(lignes: list[dict], operation: dict, ia_spec: dict, signaler=None, arreter=None) -> dict:
    """Applique `operation` à chaque ligne de `lignes`, EN PLACE : `faits["ia"][champ_sortie]`, et le champ ajouté à
    `faits["ia_marque"]` si `ia_spec['marquer']`. Une ligne dont l'agent échoue garde son résultat sans le champ IA
    (jamais un fait inventé en silence) : comptée à part, signalée si `signaler` est donné. `arreter()` vrai (arrêt
    demandé, limite de temps) : les lignes restantes ne sont pas traitées, et c'est compté.
    Rend `{"ia_appels", "ia_echecs"?, "ia_non_traitees"?}` pour le journal (3.8.09)."""
    appels = echecs = 0
    champ = operation["champ_sortie"]
    for n, ligne in enumerate(lignes):
        if arreter and arreter():
            return {"ia_appels": appels, **({"ia_echecs": echecs} if echecs else {}), "ia_non_traitees": len(lignes) - n}
        try:
            texte = appliquer(operation, ligne, {}, ia_spec.get("modele", ""), ia_spec.get("effort", ""))
        except (OSError, ValueError) as exc:
            echecs += 1
            if signaler:
                signaler("ia_echec", nom=ligne.get("nom", ""), raison=str(exc)[:200])
            continue
        faits = ligne.setdefault("faits", {})
        faits.setdefault("ia", {})[champ] = texte
        if ia_spec.get("marquer"):
            faits["ia_marque"] = sorted({*faits.get("ia_marque", []), champ})
        appels += 1
    return {"ia_appels": appels, **({"ia_echecs": echecs} if echecs else {})}
