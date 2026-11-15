"""A1 (spec 912) : le plan s'applique à TOUS les noms classés, la coupe à « combien » vient après, et elle est dite."""

from __future__ import annotations

from pathlib import Path

from pilote.pont.coupe import plan_puis_coupe

RACINE = Path(__file__).resolve().parents[1]


def _lignes(n):
    return [{"nom": f"Nom {i:03d}", "ville": "Lorient" if i % 2 else "Colmar"} for i in range(n)]


def _filtre_lorient(lignes):
    gardees = [l for l in lignes if l["ville"] == "Lorient"]
    return gardees, {"retires": len(lignes) - len(gardees), "ia": list(range(len(gardees)))}


def test_le_filtre_voit_tous_les_noms_et_la_liste_sort_complete():
    # 20 noms classés, 10 demandés, un filtre qui en garde un sur deux : avant A1 il en sortait 5, il en sort 10.
    lignes, bilan, coupe = plan_puis_coupe(_lignes(20), 10, _filtre_lorient)
    assert len(lignes) == 10 and all(l["ville"] == "Lorient" for l in lignes)
    assert bilan["retires"] == 10
    assert coupe is None  # rien n'a été coupé : rien à dire


def test_la_coupe_garde_l_ordre_du_classement_et_dit_ce_qu_elle_retire():
    lignes, bilan, coupe = plan_puis_coupe(_lignes(100), 10, _filtre_lorient)
    assert [l["nom"] for l in lignes] == [f"Nom {i:03d}" for i in range(1, 20, 2)]
    assert coupe == {"retires": 40, "combien": 10, "noms": [f"Nom {i:03d}" for i in range(21, 81, 2)]}  # le nombre réel, trente noms au plus
    assert bilan["ia"] == list(range(10))  # l'Assistant IA ne traite jamais un nom qui ne sort pas


def test_sans_plan_la_coupe_est_celle_d_avant_et_elle_est_dite():
    lignes, bilan, coupe = plan_puis_coupe(_lignes(12), 10, None)
    assert [l["nom"] for l in lignes] == [f"Nom {i:03d}" for i in range(10)] and bilan is None
    assert coupe == {"retires": 2, "combien": 10, "noms": ["Nom 010", "Nom 011"]}


def test_le_pont_ne_coupe_plus_avant_le_plan_et_le_journal_recoit_la_coupe():
    pont = (RACINE / "src/pilote/pont/executer.py").read_text(encoding="utf-8")
    boucle = pont[pont.index("for c, _lg, p in classes:") : pont.index("plan_puis_coupe(")]
    assert "break" not in boucle and "combien" not in boucle
    assert 'resultat["coupe"]' in pont
    assert "coupe_noms_retires" in (RACINE / "src/pilote/executeur_grappes.py").read_text(encoding="utf-8")


def test_l_executeur_note_la_coupe_au_journal():
    from pilote.executeur_grappes import dire_la_coupe

    notes, avance = [], {}

    class Ctx:
        def noter(self, evenement, **detail):
            notes.append((evenement, detail))

        def avancer(self, **k):
            avance.update(k)

    dire_la_coupe(Ctx(), {"retires": 2, "combien": 10, "noms": ["A", "B"]})
    dire_la_coupe(Ctx(), None)
    assert notes == [("coupe_noms_retires", {"retires": 2, "combien": 10, "noms": ["A", "B"]})]
    assert avance == {"coupe": {"retires": 2, "combien": 10}}
