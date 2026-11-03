"""Assistant IA (3.8.09) : applique une opération (voir `operations_ia/`) à un résultat déjà collecté, en appelant
en silence l'agent Claude Code déjà installé et connecté par abonnement Pro/Max — PAS une clé d'API, PAS de
facturation séparée (vérifié auprès de la documentation officielle : un abonnement Pro/Max ne donne pas accès à
l'API classique, mais l'agent s'y connecte). Le même mécanisme que momo utilise déjà pour les tâches mécaniques
(`/areas/agent-ia.md`), adapté à .115.

Règle de l'outil : jamais un fait inventé en silence. Si l'agent ne répond pas, ou répond quelque chose
d'inexploitable, une erreur claire est levée — l'appelant garde le résultat sans le champ IA, et le dit."""

from __future__ import annotations

import subprocess

DELAI_S = 60


def commande(modele: str, prompt: str) -> list[str]:
    """La ligne de commande silencieuse (`claude -p "…" --model <modèle>`), isolée pour être testée sans lancer
    de processus réel."""
    cmd = ["claude", "-p", prompt]
    if modele:
        cmd += ["--model", modele]
    return cmd


def demander(modele: str, prompt: str) -> str:
    """Le texte renvoyé par l'agent. Lève OSError si l'agent n'est pas installé ou ne répond pas, ValueError s'il
    rend une sortie vide — jamais un fait inventé en silence."""
    try:
        p = subprocess.run(commande(modele, prompt), capture_output=True, text=True, timeout=DELAI_S, check=False)
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


def appliquer(operation: dict, resultat: dict, options: dict, modele: str = "") -> str:
    """Le texte à mettre dans `operation['champ_sortie']` pour ce résultat. Ne modifie resultat nulle part : à
    l'appelant de poser le champ et la marque « IA »."""
    return demander(modele, operation["module"].prompt(resultat, options))


def appliquer_lignes(lignes: list[dict], operation: dict, ia_spec: dict, signaler=None) -> dict:
    """Applique `operation` à chaque ligne de `lignes`, EN PLACE (pose `operation['champ_sortie']`, et
    `ligne['ia_marque']` si `ia_spec['marquer']`). Une ligne dont l'agent échoue garde son résultat sans le
    champ IA (jamais un fait inventé en silence) : comptée à part, signalée si `signaler` est donné.
    Rend `{"ia_appels": n, "ia_echecs": n}` (la seconde clé absente si aucun échec), pour le journal (3.8.09)."""
    appels, echecs = 0, 0
    for ligne in lignes:
        try:
            texte = appliquer(operation, ligne, {}, ia_spec.get("modele", ""))
        except (OSError, ValueError) as exc:
            echecs += 1
            if signaler:
                signaler("ia_echec", nom=ligne.get("nom", ""), raison=str(exc)[:200])
            continue
        ligne[operation["champ_sortie"]] = texte
        if ia_spec.get("marquer"):
            ligne.setdefault("ia_marque", []).append(operation["champ_sortie"])
        appels += 1
    return {"ia_appels": appels, **({"ia_echecs": echecs} if echecs else {})}
