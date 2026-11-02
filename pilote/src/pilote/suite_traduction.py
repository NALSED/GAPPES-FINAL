"""Traduction de la requête, pour chercher dans la langue d'une source (spécification 09). Le moteur n'est PAS choisi par le code : c'est un service
compatible LibreTranslate dont l'adresse se règle dans `pilote.yaml` (`suite.traduction_url`) ; sans adresse, la tuile Traduction n'est pas appliquée
et le plan le dit. L'original reste toujours à côté (règle 1) : la requête traduite n'écrase rien, elle est seulement envoyée à la source, et
le journal garde les deux."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request

DELAI_S = 20

# « Ne pas traduire » (3.8.02) : quatre presets faisables aujourd'hui sur du texte, sans reconnaissance d'entités.
# « Noms propres » (le cinquième de la spécification) n'est pas dans ce registre : il demande une reconnaissance de
# noms pas encore branchée — l'interface le montre grisé, avec « bientôt », plutôt que de le proposer ici.
PRESETS = {
    "guillemets": re.compile(r'"[^"]+"|«[^»]+»'),
    "majuscules": re.compile(r"\b[A-Z]{2,}\b"),
    "nombres_dates": re.compile(r"\b[\d](?:[\d\s.,:/ -]*[\d])?\s?[€$]?\b"),
    "urls_emails": re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b|\bhttps?://\S+\b|\b(?:[\w-]+\.)+[a-zA-Z]{2,}\b"),
}


def _jeton(i: int) -> str:
    """Sans chiffre ni majuscule : aucun des presets ne le re-matche quand un preset suivant relit le texte déjà
    jeté (sinon `nombres_dates` ou `majuscules` repère le jeton précédent et le casse en le remplaçant à son tour)."""
    lettres, out, n = "abcdefghijklmnopqrstuvwxyz", [], i
    while True:
        out.append(lettres[n % 26])
        n = n // 26 - 1
        if n < 0:
            break
    return f"§prot{''.join(reversed(out))}§"


def proteger(texte: str, presets: list[str]) -> tuple[str, dict[str, str]]:
    """Remplace les passages protégés par un jeton que le moteur de traduction laisse tel quel — jamais un mot
    qu'il chercherait à traduire. `restaurer()` les remet après coup."""
    correspondances: dict[str, str] = {}

    def remplacer(m: re.Match) -> str:
        jeton = _jeton(len(correspondances))
        correspondances[jeton] = m.group(0)
        return jeton

    out = texte
    for p in presets:
        motif = PRESETS.get(p)
        if motif is not None:
            out = motif.sub(remplacer, out)
    return out, correspondances


def restaurer(texte: str, correspondances: dict[str, str]) -> str:
    for jeton, original in correspondances.items():
        texte = texte.replace(jeton, original)
    return texte


def traduire(url: str, texte: str, de: str, vers: str) -> str:
    """Le texte traduit. Lève OSError / ValueError : l'appelant garde alors la requête d'origine et le dit.

    Les modèles installés vont de et vers l'anglais. Le service SAIT composer deux modèles (fr → es via en), mais la version 1.9.6 de LibreTranslate
    avec Argos 1.11 rend alors le texte anglais intermédiaire (constaté le 27/10/2026) : on pivote donc nous-mêmes, en deux appels."""
    if de not in ("en", "auto") and vers != "en" and de != vers:
        return _un_appel(url, _un_appel(url, texte, de, "en"), "en", vers)
    return _un_appel(url, texte, de, vers)


def _un_appel(url: str, texte: str, de: str, vers: str) -> str:
    """Un appel ; si le modèle rend le texte tel quel (il prend « Sports Association » en capitales pour un nom propre), un second essai en minuscules, la première lettre rétablie."""
    r = _appel(url, texte, de, vers)
    if r.casefold() == texte.casefold() and texte != texte.lower() and de != vers:
        r2 = _appel(url, texte.lower(), de, vers)
        if r2.casefold() != texte.casefold():
            return r2[:1].upper() + r2[1:] if texte[:1].isupper() else r2
    return r


def traduire_protege(url: str, texte: str, de: str, vers: str, presets: list[str] | None = None) -> str:
    """`traduire()`, en protégeant d'abord les passages que les presets « Ne pas traduire » désignent (3.8.02)."""
    protege, correspondances = proteger(texte, presets or [])
    return restaurer(traduire(url, protege, de, vers), correspondances)


def _appel(url: str, texte: str, de: str, vers: str) -> str:
    corps = json.dumps({"q": texte, "source": de, "target": vers, "format": "text"}).encode()
    req = urllib.request.Request(
        url.rstrip("/") + "/translate", data=corps, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=DELAI_S) as r:
            rep = json.loads(r.read().decode())
    except urllib.error.URLError as exc:
        raise OSError(f"le moteur de traduction ne répond pas ({exc})") from exc
    t = rep.get("translatedText") if isinstance(rep, dict) else None
    if not isinstance(t, str) or not t.strip():
        raise ValueError("le moteur de traduction n'a rien rendu")
    return t.strip()
