"""Corpus synthétique (~2 000 observations, 3 écosystèmes, thèmes neutres inventés).

Usage : .venv/bin/python outils/corpus_synthetique.py <dossier_sortie> [graine]
Écrit `<sortie>/x/x.jsonl`, `<sortie>/telegram/telegram.jsonl`, `<sortie>/web/web.jsonl`,
au format des fixtures (`tests/fixtures`), et `<sortie>/attendu.json` : le statut attendu
des cibles de recoupement (validé, refusé, ambigu) pour la vérification automatique.

Grappes visées : `config/grappes/demo_a.yaml` (cuisine) et `demo_b.yaml` (jardinage).
Aucun lexique réel, aucune donnée réelle.
"""

from __future__ import annotations

import json
import random
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

A_TERMS = ["soupe", "recette", "#cuisine", "café crème"]
B_TERMS = ["potager", "semis", "tomates", "#jardinage"]
NOISE = ["bonjour", "demain", "voiture", "musique", "ciel", "lundi", "train", "livre", "pluie"]
BASE = datetime(2026, 3, 1, tzinfo=UTC)


class Corpus:
    def __init__(self, seed: int):
        self.rnd = random.Random(seed)
        self.x: list[dict] = []
        self.tg: list[dict] = []
        self.web: list[dict] = []
        self._id = 0

    def _ts(self, days_back: int | None = None) -> datetime:
        d = self.rnd.randrange(0, 60) if days_back is None else days_back
        return BASE - timedelta(days=d, minutes=self.rnd.randrange(0, 1440))

    def _date(self, ts: datetime | None, eco: str):
        if ts is None:
            return None
        if self.rnd.random() < 0.15:  # formats mêlés : epoch ou ISO
            return int(ts.timestamp())
        return ts.isoformat()

    def themed(self, terms: list[str], k: int = 3) -> str:
        words = self.rnd.choices(terms, k=k) + self.rnd.choices(NOISE, k=3)
        self.rnd.shuffle(words)
        return " ".join(words)

    def neutral(self) -> str:
        return " ".join(self.rnd.choices(NOISE, k=6))

    def post(self, eco: str, ident: str, text: str, *, mentions=(), links=(), ts="auto"):
        self._id += 1
        when = self._ts() if ts == "auto" else ts
        if eco == "x":
            body = text + "".join(f" @{m}" for m in mentions)
            rec = {"id": f"x{self._id}", "author": {"handle": f"@{ident}"}, "text": body}
            if links:
                rec["entities"] = {"urls": [{"expanded_url": u} for u in links]}
            if when:
                rec["created_at"] = self._date(when, eco)
            self.x.append(rec)
        elif eco == "telegram":
            body = text + "".join(f" @{m}" for m in mentions)
            rec = {"message_id": self._id, "channel": f"@{ident}", "text": body}
            if links:
                rec["entities"] = [{"type": "url", "url": u} for u in links]
            if when:
                rec["date"] = self._date(when, eco)
            self.tg.append(rec)
        else:
            rec = {"url": f"https://{ident}/p{self._id}", "title": "", "text": text}
            if links:
                rec["outlinks"] = list(links)
            if when:
                rec["fetched_at"] = self._date(when, eco)
            self.web.append(rec)


def link_to(key: str) -> str:
    """Lien qui cite l'élément `key` (`web:domaine` ou `telegram:canal`)."""
    eco, ident = key.split(":", 1)
    return f"https://{ident}/page" if eco == "web" else f"https://t.me/{ident}/1"


def build(seed: int = 11) -> tuple[Corpus, dict[str, str]]:
    c = Corpus(seed)
    rnd = c.rnd
    # --- membres solides des grappes A et B (S élevé), et leurs ancres -------------------
    members_a = (
        [("x", f"cuisinier_{i}") for i in range(12)]
        + [("telegram", f"canal_cuisine_{i}") for i in range(12)]
        + [("web", f"cuisine-{i}.test") for i in range(8)]
        + [("x", "chef_demo"), ("web", "exemple-a.test")]
    )
    members_b = (
        [("x", f"jardinier_{i}") for i in range(8)]
        + [("telegram", f"canal_jardin_{i}") for i in range(8)]
        + [("web", f"jardin-{i}.test") for i in range(4)]
        + [("x", "jardin_demo")]
    )
    for terms, group in ((A_TERMS, members_a), (B_TERMS, members_b)):
        for eco, ident in group:
            for _ in range(28):
                c.post(eco, ident, c.themed(terms))
    # chaque membre cite quelques autres membres de sa grappe (liens du même écosystème)
    for group in (members_a, members_b):
        for eco, ident in group:
            peers = [p for p in group if p != (eco, ident)]
            for _ in range(2):
                p_eco, p_id = rnd.choice(peers)
                key = f"{p_eco}:{p_id}"
                if eco == p_eco and eco != "web":
                    c.post(
                        eco,
                        ident,
                        c.themed(A_TERMS if group is members_a else B_TERMS),
                        mentions=[p_id],
                    )
                elif p_eco in ("web", "telegram"):
                    c.post(eco, ident, c.neutral(), links=[link_to(key)])

    # --- cibles de recoupement (texte propre neutre : S ≈ 0) ----------------------------
    attendu: dict[str, str] = {}

    def target(eco, ident, expected):
        for _ in range(3):
            c.post(eco, ident, c.neutral())
        attendu[f"{eco}:{ident}"] = expected

    xs_a = [m for m in members_a if m[0] == "x"][:5]
    tg_a = [m for m in members_a if m[0] == "telegram"][:3]
    web_a = [m for m in members_a if m[0] == "web"][:3]

    # validé : ≥ 3 citants membres, 3 écosystèmes
    target("web", "cible-valide.test", "valide")
    for eco, ident in xs_a[:3] + tg_a[:2] + web_a[:2]:
        c.post(eco, ident, c.neutral(), links=[link_to("web:cible-valide.test")])
    target("telegram", "cible_valide_tg", "valide")
    for eco, ident in xs_a[:3] + web_a[:2] + tg_a[:2]:
        c.post(eco, ident, c.neutral(), links=[link_to("telegram:cible_valide_tg")])
    # refusé : un seul écosystème (x uniquement)
    target("x", "cible_mono_eco", "refuse")
    for _, ident in xs_a:
        c.post("x", ident, c.neutral(), mentions=["cible_mono_eco"])
    # refusé : trop peu de citants (2)
    target("web", "cible-peu-citee.test", "refuse")
    for eco, ident in (xs_a[0], tg_a[0]):
        c.post(eco, ident, c.neutral(), links=[link_to("web:cible-peu-citee.test")])
    # refusé : citants non membres (bruit, 3 écosystèmes)
    target("web", "cible-bruit.test", "refuse")
    for i in range(6):
        eco = ("x", "telegram", "web")[i % 3]
        ident = f"bruit_{i}" if eco != "web" else f"bruit-{i}.test"
        c.post(eco, ident, c.neutral(), links=[link_to("web:cible-bruit.test")])
    # refusé : citations hors fenêtre (> 180 jours avant la plus récente)
    target("web", "cible-perimee.test", "refuse")
    for eco, ident in xs_a[:3] + tg_a[:2] + web_a[:2]:
        c.post(
            eco,
            ident,
            c.neutral(),
            links=[link_to("web:cible-perimee.test")],
            ts=BASE - timedelta(days=400 + rnd.randrange(30)),
        )
    # ambigu : texte propre mi-A mi-B
    for _ in range(6):
        c.post("x", "mixte", " ".join(rnd.sample(A_TERMS, 3) + rnd.sample(B_TERMS, 3)))
    attendu["x:mixte"] = "ambigu"
    # circulaire : trois sources neutres qui se citent entre elles
    for i in range(3):
        for _ in range(4):
            c.post("x", f"circ{i}", c.neutral(), mentions=[f"circ{(i + 1) % 3}"])
        attendu[f"x:circ{i}"] = "non_classe"

    # --- bruit : sources neutres, doublons, dates absentes, enregistrements invalides ----
    for i in range(40):
        eco = ("x", "telegram", "web")[i % 3]
        ident = f"neutre_{i}" if eco != "web" else f"neutre-{i}.test"
        for _ in range(14):
            c.post(eco, ident, c.neutral(), ts=None if rnd.random() < 0.1 else "auto")
    c.x.extend(rnd.sample(c.x, 40))  # doublons exacts
    c.tg.append({"text": "sans canal"})
    c.web.append({"title": "sans url"})
    return c, attendu


def write(out: Path, seed: int = 11) -> dict[str, str]:
    c, attendu = build(seed)
    for name, rows in (("x", c.x), ("telegram", c.tg), ("web", c.web)):
        d = out / name
        d.mkdir(parents=True, exist_ok=True)
        with (d / f"{name}.jsonl").open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    (out / "attendu.json").write_text(json.dumps(attendu, indent=2, sort_keys=True), "utf-8")
    return attendu


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    write(Path(sys.argv[1]), int(sys.argv[2]) if len(sys.argv) > 2 else 11)
    print("corpus écrit dans", sys.argv[1])
