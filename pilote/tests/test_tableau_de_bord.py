"""1.1 — Tableau de bord, §8 : le compteur par tuile et la ligne de journal « tuile_passee », sans lancer de
vraie recherche (ExecuteurGrappes.dire_le_plan ne fait que lire des dictionnaires et appeler ctx)."""

from __future__ import annotations

from types import SimpleNamespace

from pilote.executeur_grappes import ExecuteurGrappes


def ctx():
    evenements, avance = [], {}
    c = SimpleNamespace(avancer=lambda **k: avance.update(k), noter=lambda e, **k: evenements.append((e, k)))
    return c, evenements, avance


def test_tuile_passee_ecrite_une_fois_par_tuile_avec_son_bilan(cfg):
    c, evenements, avance = ctx()
    spec = {"plan": {
        "appliques": [], "non_appliques": [], "effets": {"f1": "journal", "f2": "compteur", "f3": "rien"},
    }}
    jeu = {"tuiles": {
        "f1": {"nom": "Traduction", "entrees": 120, "sorties": 120},  # pas de filtrage réel ici (simplifié pour le test) : compte quand même si entrees>0
        "f2": {"nom": "Filtre", "entrees": 30, "sorties": 18},
        "f3": {"nom": "Format", "entrees": 10, "sorties": 10},
    }}
    ExecuteurGrappes(cfg).dire_le_plan(c, spec, jeu)
    assert avance["plan"]["tuiles"] == jeu["tuiles"]
    # seule la tuile à l'effet « journal » écrit une ligne — pas celle à « compteur » ni à « rien »
    assert evenements == [("tuile_passee", {"tuile": "f1", "nom": "Traduction", "traversees": 120, "modifiees": 0})]


def test_tuile_sans_fiche_traversee_n_ecrit_rien(cfg):
    c, evenements, avance = ctx()
    spec = {"plan": {"appliques": [], "non_appliques": [], "effets": {"f1": "journal"}}}
    jeu = {"tuiles": {"f1": {"nom": "Filtre", "entrees": 0, "sorties": 0}}}
    ExecuteurGrappes(cfg).dire_le_plan(c, spec, jeu)
    assert evenements == []


def test_filtre_qui_retire_la_moitie_ecrit_le_bon_bilan(cfg):
    c, evenements, _ = ctx()
    spec = {"plan": {"appliques": [], "non_appliques": [], "effets": {"f2": "journal"}}}
    jeu = {"tuiles": {"f2": {"nom": "Filtre", "entrees": 30, "sorties": 18}}}
    ExecuteurGrappes(cfg).dire_le_plan(c, spec, jeu)
    assert evenements == [("tuile_passee", {"tuile": "f2", "nom": "Filtre", "traversees": 30, "modifiees": 12})]
