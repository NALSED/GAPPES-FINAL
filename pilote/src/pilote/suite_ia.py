"""Assistant IA (3.8.09) : applique une opération (voir `operations_ia/`) à un résultat déjà collecté, en appelant
en silence l'agent Claude Code déjà installé et connecté par abonnement Pro/Max — PAS une clé d'API, PAS de
facturation séparée (vérifié auprès de la documentation officielle : un abonnement Pro/Max ne donne pas accès à
l'API classique, mais l'agent s'y connecte). Le même mécanisme que momo utilise déjà pour les tâches mécaniques
(`/areas/agent-ia.md`), adapté à .115.

Règle de l'outil : jamais un fait inventé en silence. Si l'agent ne répond pas, ou répond quelque chose
d'inexploitable, une erreur claire est levée — l'appelant garde le résultat sans le champ IA, et le dit.

Ce que l'IA produit est rangé dans `faits["ia"]` (champ de sortie de l'opération -> texte), jamais dans une
colonne de la fiche : la donnée IA ne se mêle pas aux faits trouvés, et la marque (`faits["ia_marque"]`) la suit
jusqu'à l'export (spécification 10, règle 1).

Décision 904/Q33 : le coût affiché n'est pas un nombre d'appels, mais les TOKENS RÉELS consommés — lus directement
dans `usage` de `claude -p … --output-format json`, rien à estimer. Ce chiffre est informatif seulement (le
forfait Pro/Max de Sednal n'est pas un quota en tokens, c'est une fenêtre glissante de 5 heures sans solde publié) :
jamais mêlé au compteur crédits (3.8.08, facturé différemment), jamais plafonné lui-même — seul le NOMBRE DE NOMS
traités par recherche l'est (option « Traiter au maximum » de la tuile)."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

DELAI_S = 60
# Effort de raisonnement (`claude -p … --effort <niveau>`, vérifié sur .250 le 03/11/2026) : mot affiché -> valeur.
EFFORTS = {"par défaut": "", "faible": "low", "moyen": "medium", "élevé": "high", "très élevé": "xhigh", "maximal": "max"}
# Les quatre compteurs de `usage` qui représentent des tokens réellement consommés (Q33) : la lecture, l'écriture et
# les deux sens du cache — jamais un cumul d'affichage inventé, seulement ce que le CLI rend déjà.
_CHAMPS_USAGE = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")


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
    """La ligne de commande silencieuse (`claude -p "…" --model <modèle> --effort <niveau> --output-format json`),
    isolée pour être testée sans lancer de processus réel. Le JSON porte `result` (le texte) et `usage` (les
    tokens, Q33) — sans lui il n'y aurait qu'un texte brut, sans aucun moyen de compter la consommation réelle."""
    cmd = [chemin_agent() or "claude", "-p", prompt, "--output-format", "json"]
    if modele:
        cmd += ["--model", modele]
    if effort:
        cmd += ["--effort", effort]
    return cmd


def total_tokens(usage: dict[str, Any]) -> int:
    """Les tokens réellement consommés par un appel, tels que `usage` les donne (Q33) : rien d'estimé."""
    return sum(int(usage.get(c) or 0) for c in _CHAMPS_USAGE)


def demander(modele: str, prompt: str, effort: str = "") -> tuple[str, int]:
    """(le texte renvoyé par l'agent, les tokens consommés par cet appel). Lève OSError si l'agent n'est pas
    installé, ne répond pas ou signale lui-même une erreur (`is_error`) ; ValueError si sa réponse n'est pas le
    JSON attendu ou que le texte est vide — jamais un fait inventé en silence."""
    try:
        p = subprocess.run(commande(modele, prompt, effort), capture_output=True, text=True, timeout=DELAI_S, check=False)
    except FileNotFoundError as exc:
        raise OSError("l'agent Claude Code n'est pas installé sur cette machine (introuvable sur le PATH)") from exc
    except subprocess.TimeoutExpired as exc:
        raise OSError(f"l'agent Claude Code a dépassé {DELAI_S} secondes") from exc
    try:
        d = json.loads(p.stdout)
    except ValueError as exc:
        if p.returncode != 0:
            derniere = (p.stderr.strip().splitlines() or ["il s'est arrêté sans message"])[-1][:200]
            raise OSError(f"l'agent Claude Code n'a pas pu répondre : {derniere}") from exc
        raise ValueError("l'agent Claude Code n'a pas rendu une réponse JSON lisible") from exc
    if p.returncode != 0 or d.get("is_error"):
        raise OSError(f"l'agent Claude Code a signalé une erreur : {str(d.get('result') or '').strip()[:200] or 'sans message'}")
    sortie = str(d.get("result") or "").strip()
    if not sortie:
        raise ValueError("l'agent Claude Code n'a rien rendu")
    return sortie, total_tokens(d.get("usage") or {})


def appliquer(operation: dict, resultat: dict, options: dict, modele: str = "", effort: str = "") -> tuple[str, int]:
    """(le texte de `operation['champ_sortie']` pour ce résultat, les tokens consommés). Ne modifie resultat nulle part."""
    return demander(modele, operation["module"].prompt(resultat, options), effort)


def appliquer_lignes(lignes: list[dict], operation: dict, ia_spec: dict, signaler=None, arreter=None) -> dict:
    """Applique `operation` à chaque ligne de `lignes` (au plus `ia_spec['plafond']`, Q33), EN PLACE :
    `faits["ia"][champ_sortie]`, et le champ ajouté à `faits["ia_marque"]` si `ia_spec['marquer']`. Une ligne dont
    l'agent échoue garde son résultat sans le champ IA (jamais un fait inventé en silence) : comptée à part,
    signalée si `signaler` est donné. `arreter()` vrai (arrêt demandé, limite de temps) : les lignes restantes ne
    sont pas traitées, et c'est compté. Rend `{"ia_appels", "ia_tokens", "ia_echecs"?, "ia_non_traitees"?,
    "ia_plafonnees"?}` pour le journal (3.8.09/Q33)."""
    plafond = ia_spec.get("plafond")
    a_traiter = lignes if plafond is None else lignes[:plafond]
    plafonnees = len(lignes) - len(a_traiter)
    appels = echecs = tokens = 0
    champ = operation["champ_sortie"]
    for n, ligne in enumerate(a_traiter):
        if arreter and arreter():
            return {
                "ia_appels": appels, "ia_tokens": tokens, **({"ia_echecs": echecs} if echecs else {}),
                "ia_non_traitees": len(a_traiter) - n, **({"ia_plafonnees": plafonnees} if plafonnees else {}),
            }  # fmt: skip
        try:
            options = {"categories": ia_spec.get("categories", "")} if ia_spec.get("categories") else {}
            texte, cout = appliquer(operation, ligne, options, ia_spec.get("modele", ""), ia_spec.get("effort", ""))
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
        tokens += cout
    return {
        "ia_appels": appels, "ia_tokens": tokens, **({"ia_echecs": echecs} if echecs else {}),
        **({"ia_plafonnees": plafonnees} if plafonnees else {}),
    }  # fmt: skip
