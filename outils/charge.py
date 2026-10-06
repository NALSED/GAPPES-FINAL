"""Test de charge : N observations synthétiques (thèmes neutres), ingest -> run -> export.

Usage : .venv/bin/python outils/charge.py [N] [dossier_travail]
Mesure le temps de chaque étape et le pic mémoire (ru_maxrss).
"""

from __future__ import annotations

import random
import resource
import sys
import tempfile
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from grappes.clustering.assign import assign
from grappes.clustering.export import export_csv
from grappes.config import load_config
from grappes.models import Observation, SourceRef
from grappes.pipeline import make_run_id
from grappes.storage.db import Database

WORDS_A = ["soupe", "recette", "#cuisine", "café crème", "four", "sel"]
WORDS_B = ["potager", "semis", "tomates", "#jardinage", "arrosage", "terre"]
NOISE = ["bonjour", "demain", "voiture", "musique", "ciel", "lundi", "train", "livre"]


def synth(n: int, n_sources: int, seed: int = 7):
    rnd = random.Random(seed)
    base = datetime(2026, 1, 1, tzinfo=UTC)
    ecos = ["x", "telegram", "web"]
    sources = [SourceRef(ecos[i % 3], f"src{i}") for i in range(n_sources)]
    theme = {s.key: rnd.choice([WORDS_A, WORDS_B, NOISE]) for s in sources}
    for i in range(n):
        s = sources[rnd.randrange(n_sources)]
        words = rnd.choices(theme[s.key], k=3) + rnd.choices(NOISE, k=4)
        rnd.shuffle(words)
        cited = [sources[rnd.randrange(n_sources)] for _ in range(rnd.randrange(3))]
        yield Observation(
            obs_id=f"load{i}",
            source=s,
            ts=base + timedelta(minutes=i % 100_000),
            text=" ".join(words),
            mentions=tuple(c for c in cited if c.ecosystem != "web"),
            links=tuple(f"https://{c.ident}.test/p" for c in cited if c.ecosystem == "web"),
        )


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100_000
    work = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(tempfile.mkdtemp(prefix="charge_"))
    cfg = load_config(Path(__file__).resolve().parents[1] / "config")
    db = Database(work / "charge.db")
    t0 = time.perf_counter()
    db.add_observations(synth(n, max(100, n // 20)), {})
    t1 = time.perf_counter()
    obs = db.load_observations()
    t2 = time.perf_counter()
    res = assign(obs, cfg)
    t3 = time.perf_counter()
    run_id = make_run_id([o.obs_id for o in obs], cfg.config_hash)
    db.save_run(
        run_id, cfg.config_hash, res.entities, res.memberships, res.citations, res.validations
    )
    t4 = time.perf_counter()
    export_csv(res, cfg, run_id, work / "sorties")
    t5 = time.perf_counter()
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    print(
        f"observations={n} entités={len(res.entities)} citations={len(res.citations)} "
        f"validations={len(res.validations)} itérations={res.iterations}"
    )
    print(
        f"insertion={t1 - t0:.1f}s chargement={t2 - t1:.1f}s assign={t3 - t2:.1f}s "
        f"sauvegarde={t4 - t3:.1f}s export={t5 - t4:.1f}s total={t5 - t0:.1f}s"
    )
    print(f"pic mémoire={rss:.0f} Mo ; base={Path(db.path).stat().st_size / 1e6:.0f} Mo")


if __name__ == "__main__":
    main()
