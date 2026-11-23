"""914/B : des pages qui se recopient comptent pour un seul endroit. Thème inventé (clubs de cerf-volant)."""

from __future__ import annotations

from types import SimpleNamespace

from grappes.classement import copies
from grappes.classement.candidats import Candidat
from grappes.classement.production import niveau_de

AVANT = ("la saison commence au printemps sur la grande plage du nord où les membres se retrouvent chaque samedi matin pour "
         "préparer les voiles réparer les lignes et accueillir les nouveaux venus qui veulent apprendre à piloter")
APRES = ("le club organise aussi une fête du vent en septembre avec des démonstrations de cerfs-volants géants des ateliers "
         "pour les enfants et un concours de figures jugé par les anciens champions de la région venus en voisins")
AUTRE = ("rencontre avec une équipe qui vole par tous les temps depuis vingt ans et qui forme chaque hiver des pilotes dans "
         "un gymnase prêté par la commune avant de repartir dehors dès que les beaux jours reviennent sur les dunes du sud")
NOM = "Les Cerfs-Volants Bleus"


def _obs(site: str, texte: str):
    return SimpleNamespace(source=SimpleNamespace(key=f"web:{site}"), text=texte)


def _cand(ner_sites=(), citants=(), editeurs=0):
    return Candidat(ref="ner:x", nom=NOM, nom_brut=NOM, confiance=0, statut="nomme", s=0, e=0, a=0, citants=set(citants),
                    editeurs=editeurs, ner_sites=dict.fromkeys(ner_sites, 0.9))  # fmt: skip


def _texte(avant=AVANT, apres=APRES):
    return f"{avant} {NOM} {apres}"


def test_copie_mot_pour_mot_un_seul_endroit():
    c = _cand(ner_sites=["a.example", "b.example"])
    copies.marquer([c], [_obs("a.example", _texte()), _obs("b.example", "Annuaire. " + _texte() + " Fin de la fiche.")])
    assert c.copies == {"a.example": "a.example", "b.example": "a.example"}
    assert niveau_de(c) == "à vérifier"


def test_copie_legerement_retouchee_un_seul_endroit():
    c = _cand(ner_sites=["a.example", "b.example"])
    retouche = AVANT.replace("samedi", "dimanche")
    copies.marquer([c], [_obs("a.example", _texte()), _obs("b.example", _texte(avant=retouche))])
    assert copies.independants(c.ner_sites, c.copies) == 1


def test_deux_textes_differents_deux_endroits():
    c = _cand(ner_sites=["a.example", "b.example"])
    copies.marquer([c], [_obs("a.example", _texte()), _obs("b.example", _texte(avant=AUTRE, apres=AUTRE))])
    assert c.copies == {} and niveau_de(c) == "sûr"


def test_meme_modele_de_site_textes_differents_deux_endroits():
    menu = "accueil actualités agenda contact mentions légales plan du site " * 6  # même gabarit, loin du nom : hors du passage comparé
    c = _cand(ner_sites=["a.example", "b.example"])
    copies.marquer([c], [_obs("a.example", menu + _texte() + " " + menu), _obs("b.example", menu + _texte(avant=AUTRE, apres=AUTRE) + " " + menu)])
    assert c.copies == {}


def test_passage_trop_court_pas_juge():
    c = _cand(ner_sites=["a.example", "b.example"])
    copies.marquer([c], [_obs("a.example", f"Liste : {NOM}, autre club."), _obs("b.example", f"Liste : {NOM}, autre club.")])
    assert c.copies == {} and niveau_de(c) == "sûr"


def test_copie_et_troisieme_site_independant_reste_sur():
    c = _cand(ner_sites=["a.example", "b.example", "c.example"])
    copies.marquer([c], [_obs("a.example", _texte()), _obs("b.example", _texte()), _obs("c.example", _texte(avant=AUTRE, apres=AUTRE))])
    assert copies.independants(c.ner_sites, c.copies) == 2 and niveau_de(c) == "sûr"


def test_citants_qui_se_recopient():
    c = _cand(citants=["web:a.example", "rss:b.example"], editeurs=2)
    copies.marquer([c], [_obs("a.example", _texte()), SimpleNamespace(source=SimpleNamespace(key="rss:b.example"), text=_texte())])
    assert niveau_de(c) == "à vérifier"


def test_registre_jamais_regroupe():
    c = _cand(ner_sites=["a.example", "b.example"])
    c.registres = {"sirene"}
    copies.marquer([c], [_obs("a.example", _texte()), _obs("b.example", _texte())])
    assert niveau_de(c) == "sûr"


def test_regroupement_transitif():
    e1, e2, e3 = (copies.empreinte(copies.mots(_texte(avant=a))) for a in (AVANT, AVANT.replace("samedi", "dimanche"), AVANT.replace("samedi", "lundi")))
    assert copies.groupes({"a": [e1], "b": [e2], "c": [e3]}) == {"a": "a", "b": "a", "c": "a"}
