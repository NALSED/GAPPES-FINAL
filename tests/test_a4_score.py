"""A4 (spec 912) : pas de chiffre présenté comme une probabilité tant que la calibration n'est pas valide."""

from grappes import vraisemblance as vr
from grappes.classement import production as pr
from grappes.classement.candidats import Candidat
from grappes.sortie import charger_profils, ecrire

C = Candidat("reg:sirene:1", "Atelier du Phare", "x", 0, "registre", 0, 0, 0, registres={"sirene"})


def test_sans_calibration_valide_le_chiffre_est_retire_la_bande_reste(tmp_path):
    lr = vr.charger()
    ls = pr.lignes([(C, 2.0, 0.999)], pr.ClassementConfig(), lr, pr.Calibreur(), "FR")
    assert ls[0].score is None and ls[0].bande and ls[0].calibre == "non mesuré"
    brut = [p for p in charger_profils("config") if p.id == "brut"]
    txt = ecrire(ls, brut, tmp_path)[0].read_text(encoding="utf-8").splitlines()
    i = txt[0].split(";").index("score")
    assert txt[1].split(";")[i] == "" and txt[1].split(";")[txt[0].split(";").index("bande")] == ls[0].bande


def test_avec_une_calibration_valide_le_chiffre_revient():
    ls = pr.lignes([(C, 2.0, 0.999)], pr.ClassementConfig(), vr.charger(), pr.Calibreur(valide=True), "FR")
    assert ls[0].score == 99.0 and ls[0].calibre == "mesuré"


def test_l_ordre_ne_depend_pas_du_chiffre_affiche():
    autre = Candidat("reg:sirene:2", "Club des Vents", "x", 0, "registre", 0, 0, 0, registres={"sirene"})
    ls = pr.lignes([(C, 2.0, 0.9), (autre, 1.0, 0.6)], pr.ClassementConfig(), vr.charger(), pr.Calibreur(), "FR")
    assert [x.nom for x in ls] == ["Atelier du Phare", "Club des Vents"]


def test_la_calibration_livree_n_est_pas_valide():
    assert pr.charger_calibreur("config/calibration.json").valide is False
