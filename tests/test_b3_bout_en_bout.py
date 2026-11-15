"""B3 (spec 912) : une recherche complète avec les fichiers de `config/` TELS QU'ILS SONT LIVRÉS (copiés, jamais modifiés). Les autres
essais de bout en bout utilisent la configuration du corpus synthétique : un réglage livré qui casserait la chaîne n'était vu par aucun.
Seul le sujet est ajouté (`grappes/` : trois thèmes neutres inventés du corpus). Aucun réseau : la configuration livrée est en `autonome:
false`, et l'essai échoue si un appel de recherche part."""

import csv
import hashlib
import shutil
import sys
from datetime import timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "outils"))
import corpus_synthetique as cs

from grappes.config import load_config
from grappes.cycle.engine import OK, run_cycle
from grappes.pipeline import ingest
from grappes.storage.db import Database

LIVREE = Path(__file__).resolve().parents[1] / "config"


def _empreinte(dossier: Path, sauf: str = "grappes") -> dict[str, str]:
    return {str(p.relative_to(dossier)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(dossier.rglob("*")) if p.is_file() and sauf not in p.relative_to(dossier).parts[:1] and "apprentissage" not in p.parts}  # fmt: skip


@pytest.fixture(scope="module")
def monde(tmp_path_factory):
    t = tmp_path_factory.mktemp("b3")
    attendu = cs.write(t / "corpus")
    conf = t / "config"
    shutil.copytree(LIVREE, conf)
    shutil.copytree(t / "corpus" / "config" / "grappes", conf / "grappes")  # le sujet : la seule chose ajoutée
    avant = _empreinte(conf)
    cfg = load_config(conf)
    (t / "d").mkdir()
    db = Database(t / "d" / "grappes.db")
    for eco in ("x", "telegram", "instagram", "web"):
        ingest(db, t / "corpus" / eco, eco, cfg)
    db.close()
    mp = pytest.MonkeyPatch()
    import urllib.request

    def interdit(*a, **k):
        raise AssertionError("appel réseau pendant l'essai de bout en bout")

    mp.setattr(urllib.request, "urlopen", interdit)
    try:
        rapport = run_cycle(conf, t / "d" / "grappes.db", t / "sorties", t / "d", now=cs.BASE + timedelta(days=1))
    finally:
        mp.undo()
    return {"t": t, "conf": conf, "avant": avant, "attendu": attendu, "rapport": rapport}


def _lignes(p: Path, delim=","):
    return list(csv.reader(p.read_text(encoding="utf-8").splitlines(), delimiter=delim))


def test_la_configuration_livree_est_utilisee_telle_quelle(monde):
    assert _empreinte(LIVREE) == monde["avant"]  # copie fidèle
    assert _empreinte(monde["conf"]) == monde["avant"]  # la recherche n'a rien réécrit dans les réglages


def test_la_recherche_va_au_bout(monde):
    assert monde["rapport"].status == OK
    assert (monde["t"] / "sorties" / "resultat.csv").exists()


def test_les_acteurs_attendus_sortent_et_les_faux_connus_ne_sortent_pas(monde):
    tous = {r[0] for r in _lignes(monde["t"] / "sorties" / "resultat.csv")[1:]}
    voulus = {n for noms in monde["attendu"]["resultat"].values() for n in noms}
    assert voulus <= tous, sorted(voulus - tous)
    assert not tous & set(monde["attendu"]["hors_resultat"])  # refus, ambigus, bruit : absents
    assert tous == voulus  # et rien d'autre


def test_le_fichier_complet_en_mode_classique(monde):
    """La configuration livrée est en mode classique (classement inactif). Le niveau (A3) et le retrait du chiffre non mesuré (A4) ne
    concernent que le mode extraction : ici la colonne `niveau` est vide et `score` porte la confiance d'appartenance du mode classique."""
    brut = _lignes(monde["t"] / "sorties" / "resultat_brut.csv", ";")
    tete = brut[0]
    assert "niveau" in tete and "score" in tete and len(brut) > 1
    assert {r[tete.index("niveau")] for r in brut[1:]} == {""}
    assert all(r[tete.index("score")].isdigit() and 0 <= int(r[tete.index("score")]) <= 100 for r in brut[1:])
