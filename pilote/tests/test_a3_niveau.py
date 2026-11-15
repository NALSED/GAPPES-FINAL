"""A3 (spec 912) : deux niveaux de sortie, « sûr » et « à vérifier ». Un fait de plus sur la fiche, aucun score."""

from __future__ import annotations

from pathlib import Path

from pilote import classements as cl
from pilote import suite_plan
from pilote.pont.faits import niveau_de
from pilote.pont.verification import relever_niveaux

RACINE = Path(__file__).resolve().parents[1]


def _p(main, lieu):
    return {"source": "s", "classe": "registre" if main == "premiere" else "web", "main": main, "lieu": lieu}


def test_un_registre_de_premiere_main_suffit():
    assert niveau_de([_p("premiere", "registre:r")], 1) == "sur"


def test_deux_endroits_independants_suffisent_un_seul_non():
    assert niveau_de([_p("seconde", "page:a.example"), _p("seconde", "page:b.example")], 2) == "sur"
    assert niveau_de([_p("seconde", "page:a.example")], 1) == "a_verifier"
    assert niveau_de([], 1) == "a_verifier"


def test_une_confirmation_stricte_releve_le_niveau_un_meme_nom_non():
    lignes = [
        {"nom": "A", "faits": {"niveau": "a_verifier", "verifications": [{"source": "x", "signal": "confirmation"}]}},
        {"nom": "B", "faits": {"niveau": "a_verifier", "verifications": [{"source": "x", "signal": "meme_nom"}]}},
        {"nom": "C", "faits": {"niveau": "a_verifier", "verifications": [{"source": "x", "signal": "alerte"}]}},
        {"nom": "D", "faits": {"niveau": "sur"}},
    ]
    relever_niveaux(lignes)
    assert [l["faits"]["niveau"] for l in lignes] == ["sur", "a_verifier", "a_verifier", "sur"]


def test_filtre_sait_lire_le_niveau():
    assert suite_plan.CHAMPS["niveau"] == "niveau"
    assert suite_plan.valeur({"faits": {"niveau": "sur"}}, "niveau") == "sûr"
    assert suite_plan.valeur({"faits": {"niveau": "a_verifier"}}, "niveau") == "à vérifier"
    assert suite_plan.valeur({"faits": {}}, "niveau") == ""
    lc = {"champ": "niveau", "comparateur": "egal", "valeurs": ["Sûr"]}
    assert suite_plan._teste_ligne({"faits": {"niveau": "sur"}}, lc, {}, None)
    assert not suite_plan._teste_ligne({"faits": {"niveau": "a_verifier"}}, lc, {}, None)
    assert '"niveau"' in (RACINE / "static/suite/js/options_outils.js").read_text(encoding="utf-8")


def test_un_classement_de_tri_peut_grouper_par_niveau():
    assert "niveau" in cl.FAITS

    def ligne(faits):
        return cl.Ligne(1, "N", "web", 1, [], "", "", "", "", "", None, faits=faits)

    assert cl.valeur("niveau", ligne({"niveau": "sur"}), str)[:2] == ("sur", "sûrs")
    assert cl.valeur("niveau", ligne({"niveau": "a_verifier"}), str)[:2] == ("a_verifier", "à vérifier")
    assert cl.valeur("niveau", ligne({}), str)[0] == ""  # recherche d'avant A3 : dit, jamais deviné
    rangs = [cl.valeur("niveau", ligne(f), str)[2] for f in ({"niveau": "sur"}, {"niveau": "a_verifier"}, {})]
    assert rangs == sorted(rangs)


def test_le_pont_pose_le_niveau_puis_le_releve_apres_la_verification():
    pont = (RACINE / "src/pilote/pont/executer.py").read_text(encoding="utf-8")
    assert pont.index("relever_niveaux(lignes)") > pont.index("verifier_candidats(lignes")
    assert '"niveau": niveau_de(' in (RACINE / "src/pilote/pont/faits.py").read_text(encoding="utf-8")
