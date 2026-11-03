"""Classement de production (D64) : calibreur, lignes de sortie, activation par la configuration. Aucun réseau."""

import math

from grappes import vraisemblance as vr
from grappes.classement import production as pr
from grappes.classement.candidats import Candidat
from test_phase4 import make_cfg


def test_calibreur_par_defaut_est_un_rapport_de_cotes_un_pour_un():
    c = pr.Calibreur()
    assert c.proba(0.0) == 0.5 and abs(c.proba(1.0) - 10 / 11) < 1e-9 and c.valide is False


def test_calibreur_isotone_interpole_et_borne():
    c = pr.Calibreur("isotone", x=[0.0, 1.0, 2.0], y=[0.1, 0.3, 0.9], valide=True)
    assert c.proba(-5) == 0.1 and c.proba(9) == 0.9 and math.isclose(c.proba(0.5), 0.2)


def test_config_absente_inactive(tmp_path):
    cc = pr.charger_config(tmp_path)
    assert cc.actif is False and cc.remplace_resultat is False and cc.variantes is False


def test_config_du_depot_inactive_par_defaut():
    cc = pr.charger_config("config")
    assert cc.actif is False and "wikidata" in cc.registres and cc.variantes is False


def test_mode_recherche_sites_ne_change_rien(tmp_path):
    """Décision 901/Q26 : le mode par défaut ne touche pas classement.yaml (« comportement actuel »)."""
    cfg = make_cfg(tmp_path)
    cc = pr.ClassementConfig()
    assert pr.cc_pour_mode(cc, cfg) is cc


def test_mode_recherche_extraction_active_le_classement_sans_changer_les_registres(tmp_path):
    """Décision 901/Q26 : le mode « lire le contenu » force actif/noms/remplace_resultat, pas les registres déjà
    choisis par classement.yaml (pas d'appel réseau supplémentaire non demandé)."""
    cfg = make_cfg(tmp_path, mode_recherche="extraction")
    cc = pr.ClassementConfig(actif=False, noms=False, remplace_resultat=False, registres=())
    nouveau = pr.cc_pour_mode(cc, cfg)
    assert nouveau.actif is True and nouveau.noms is True and nouveau.remplace_resultat is True
    assert nouveau.registres == ()  # inchangé : pas de registres ajoutés sans qu'on les ait demandés


def test_lignes_disent_si_le_chiffre_est_une_mesure():
    lr = vr.charger()
    c = Candidat("reg:wikidata:Q1", "Fenix Toulouse Handball", "x", 0, "registre", 0, 0, 0, registres={"wikidata"}, ville="Toulouse")
    cls = [(c, 2.0, 0.999)]
    ls = pr.lignes(cls, pr.ClassementConfig(), lr, pr.Calibreur(), "FR")
    assert ls[0].calibre == "estimation étendue" and ls[0].score == 99.0 and ls[0].ville == "Toulouse"
    ls = pr.lignes(cls, pr.ClassementConfig(), lr, pr.Calibreur(valide=True), "FR")
    assert ls[0].calibre == "mesuré"
    assert pr.lignes(cls, pr.ClassementConfig(p_min=0.9999), lr, pr.Calibreur(), "FR") == []
