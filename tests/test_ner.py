"""Reconnaissance de noms (D63, chantier 2) : découpage, nettoyage, agrégation, doublons. Aucun modèle chargé."""

from pathlib import Path

from grappes.ner import extraire as ex


def test_morceaux_couvrent_tout_le_texte():
    t = ("Phrase numéro un. " * 200).strip()
    ms = ex.morceaux(t, 300)
    assert "".join(m for _, m in ms) == t
    assert all(len(m) <= 300 for _, m in ms)
    assert all(t[d : d + len(m)] == m for d, m in ms)


def test_nettoyer_et_retenir():
    cfg = ex.NerConfig()
    assert ex.nettoyer("  les Girondins de Bordeaux, ") == "Girondins de Bordeaux"
    assert ex.retenir("Metz Handball", cfg)
    assert not ex.retenir("handball", cfg)  # aucune majuscule
    assert not ex.retenir("12", cfg)
    assert not ex.retenir(" ".join(["Mot"] * 9), cfg)


def test_recoller_apostrophe():
    t = "OGC Nice Côte d'Azur Handball"
    ms = [ex.Mention(0, 15, 0.9, "m"), ex.Mention(16, 29, 0.95, "m")]
    r = ex._recoller(ms, t)
    assert len(r) == 1 and t[r[0].debut : r[0].fin] == t and r[0].score == 0.9


def test_variantes_signalees():
    noms = {k: ex.Nomme(k, k) for k in ("fenix toulouse", "fenix toulouse handball", "metz handball")}
    assert ex.variantes(noms) == [("fenix toulouse", "fenix toulouse handball")]


def test_mentions_cache_et_seuil(tmp_path: Path, monkeypatch):
    m = ex.ModeleNer("m", "faux/modele", categories={"ORG": ["ORG"]})
    cfg = ex.NerConfig((m,), seuil_confiance=0.8)
    appels = []

    class Pipe:
        def __call__(self, morceau):
            appels.append(1)
            return [
                {"entity_group": "ORG", "start": 0, "end": 5, "score": 0.9},
                {"entity_group": "ORG", "start": 6, "end": 9, "score": 0.5},
                {"entity_group": "PER", "start": 10, "end": 13, "score": 0.99},
                {"entity_group": "ORG", "start": 90, "end": 99, "score": 0.99},  # hors texte : écarté
            ]

    monkeypatch.setattr(ex, "_pipeline", lambda *_: Pipe())
    texte = "Metz Handball joue"
    r = ex.mentions_modele(texte, m, cfg, tmp_path)
    assert [(x.debut, x.fin) for x in r] == [(0, 5)]
    r2 = ex.mentions_modele(texte, m, cfg, tmp_path)  # cache : le modèle ne retourne pas
    assert r2 == r and len(appels) == 1


def test_categorie_propagee_de_l_etiquette_a_la_mention(tmp_path, monkeypatch):
    """903 : ORG et PER élargis en même temps, chaque mention garde la catégorie qui l'a retenue, pas l'étiquette brute."""
    m = ex.ModeleNer("m", "faux/modele", categories={"ORG": ["ORG"], "PER": ["PER"]})
    cfg = ex.NerConfig((m,), seuil_confiance=0.8)

    class Pipe:
        def __call__(self, morceau):
            return [
                {"entity_group": "ORG", "start": 0, "end": 4, "score": 0.9},
                {"entity_group": "PER", "start": 8, "end": 13, "score": 0.95},
                {"entity_group": "MISC", "start": 14, "end": 18, "score": 0.99},  # catégorie non retenue : écartée
            ]

    monkeypatch.setattr(ex, "_pipeline", lambda *_: Pipe())
    texte = "ACME dirigée par Marie demain"
    r = ex.mentions_modele(texte, m, cfg, tmp_path)
    assert [(x.debut, x.fin, x.categorie) for x in r] == [(0, 4, "ORG"), (8, 13, "PER")]
    r2 = ex.mentions_modele(texte, m, cfg, tmp_path)  # cache : la catégorie survit au round-trip JSON
    assert [x.categorie for x in r2] == ["ORG", "PER"]


def test_extraire_agrege_la_categorie_la_plus_frequente(tmp_path, monkeypatch):
    m = ex.ModeleNer("m", "faux/modele", categories={"ORG": ["ORG"], "PER": ["PER"]})
    cfg = ex.NerConfig((m,), seuil_confiance=0.0, min_pages=1)

    appels = {"n": 0}

    class Pipe:
        def __call__(self, morceau):
            appels["n"] += 1
            if appels["n"] == 1:
                return [{"entity_group": "PER", "start": 0, "end": 12, "score": 0.9}]
            return [{"entity_group": "PER", "start": 0, "end": 12, "score": 0.9}]

    monkeypatch.setattr(ex, "_pipeline", lambda *_: Pipe())
    res = ex.extraire([("o1", "web:x.fr", "Marie Dupont parle"), ("o2", "web:y.fr", "Marie Dupont écrit")], cfg)
    n = res[ex.norm_cle("Marie Dupont")]
    assert n.categorie == "PER" and n.categories["PER"] == 2
