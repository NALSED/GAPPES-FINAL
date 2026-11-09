"""Le plan appliqué par le moteur (suite_plan) : quelles sources partent, quelles étapes jouent sur quelle branche, ce qui n'est pas appliqué et dit."""

from __future__ import annotations

import json

import pytest

from pilote.refus import ConfigRefusee
from pilote.suite_plan import appliquer, compiler

PAYS = {"fr": ["fr", "france"], "france": ["fr", "france"]}


def src(i, role="CHERCHER", langue="fr", etat="warn", operateurs=()):
    return {"id": i, "nom": i.upper(), "role": role, "langue": langue, "etat": etat, "operateurs": list(operateurs)}


def outil(i, nature="modele", modele=None, etat="ok", options=(), code=""):
    return {
        "id": i,
        "nom": i,
        "nature": nature,
        "modele": modele,
        "etat": etat,
        "options": [list(o) for o in options],
        "code": code,
    }


SOURCES = [src("a"), src("b"), src("c", langue="en"), src("v", role="VERIFIER"), src("d", operateurs=["site", "filetype"])]
OUTILS = [
    outil("filtre", options=[("Garder si le champ", "ville"), ("est égal à", "Lyon")]),
    outil("si", options=[("Si le champ", "catégorie"), ("est égal à", "association")]),
    outil("fusion"), outil("format", options=[("Format de sortie", "CSV"), ("Séparateur", ";")]),
    outil("traduction", options=[("Langue d'entrée", "détecter"), ("Traduire vers", "français, anglais"), ("Ne pas traduire", "rien")]),
    outil("boucle"), outil("ia", etat="off"), outil("attente"), outil("rsshub"), outil("budget"),
    outil("requete_avancee", options=[("Type de qualificatif", "Limiter à un site/domaine"), ("Valeur", "")]),
]  # fmt: skip


def noeud(i, ref=None, role=None, opts=None):
    role = (
        role
        or {"saisie": "ENTREE", "grappes": "GRAPPES"}.get(i)
        or ("CHERCHER" if ref in {s["id"] for s in SOURCES} else "OUTIL")
    )
    return {"id": i, "nom": i, "role": role, "ref": ref, "opts": opts}


def lien(a, b, label=None):
    return {"id": f"{a}>{b}", "from": a, "to": b, **({"label": label} if label else {})}


def plan(noeuds, liens):
    return {"nodes": [noeud(*n) if isinstance(n, tuple) else n for n in noeuds], "edges": liens}


def comp(p, **k):
    return compiler(p, SOURCES, OUTILS, pays_equiv=PAYS, **k)


def ligne(nom, par, ville="Lyon", genre="association", **autres):
    return {
        "nom": nom,
        "trouve_par": list(par),
        "ville": ville,
        "pays": "FR",
        "genre_de_chose": genre,
        "genre_source": "registre",
        "site": "",
        "numero_officiel": "",
        "faits": {},
        **autres,
    }


def test_seules_les_sources_reliees_de_bout_en_bout_partent():
    p = plan(
        [("saisie",), ("grappes",), ("n1", "a"), ("n2", "b"), ("n3", "c")],
        [lien("saisie", "n1"), lien("n1", "grappes"), lien("saisie", "n2"), lien("n3", "grappes")],
    )
    c = comp(p)
    assert c["sources"] == ["a"]  # b ne rend rien à Grappes, c ne reçoit rien de la saisie


def test_un_filtre_ne_juge_que_la_branche_ou_il_se_trouve():
    p = plan(
        [("saisie",), ("grappes",), ("n1", "a"), ("n2", "b"), ("f", "filtre")],
        [lien("saisie", "n1"), lien("saisie", "n2"), lien("n1", "f"), lien("f", "grappes"), lien("n2", "grappes")],
    )
    c = comp(p)
    lignes = [
        ligne("Club Lyon", ["a"]),
        ligne("Club Paris", ["a"], ville="Paris"),
        ligne("Autre Paris", ["b"], ville="Paris"),
        ligne("Les deux", ["a", "b"], ville="Paris"),
    ]
    gardes, bilan = appliquer(lignes, c)
    assert [x["nom"] for x in gardes] == [
        "Club Lyon",
        "Autre Paris",
        "Les deux",
    ]  # « Club Paris » (source a seule) est retiré ; « Les deux » passe par la branche b
    # 1.1 (§8) : le compteur par tuile — « Les deux » entre dans la tuile (trouvé aussi par « a ») mais n'en sort pas (ville ≠ Lyon)
    assert bilan["tuiles"]["f"] == {"nom": "f", "entrees": 3, "sorties": 1}
    assert (
        bilan["par_tuile"]["f"]["n"] == 1 and "Club Paris" in bilan["par_tuile"]["f"]["noms"] and bilan["retires"] == 1
    )


def test_un_nom_d_une_source_hors_plan_n_est_pas_juge_mais_compte_a_part():
    p = plan(
        [("saisie",), ("grappes",), ("n1", "a"), ("f", "filtre")],
        [lien("saisie", "n1"), lien("n1", "f"), lien("f", "grappes")],
    )
    gardes, bilan = appliquer(
        [ligne("Page web", ["(web)"], ville="Paris"), ligne("Hors filtre", ["a"], ville="Paris")], comp(p)
    )
    assert [x["nom"] for x in gardes] == ["Page web"] and bilan["non_attribues"] == 1


def test_condition_si_demande_ses_deux_sorties_etiquetees():
    base = [("saisie",), ("grappes",), ("n1", "a"), ("s", "si"), ("x", "fusion"), ("y", "fusion")]
    liens = [
        lien("saisie", "n1"),
        lien("n1", "s"),
        lien("s", "x"),
        lien("s", "y"),
        lien("x", "grappes"),
        lien("y", "grappes"),
    ]
    with pytest.raises(ConfigRefusee, match="laquelle est « oui »"):
        comp(plan(base, liens))
    liens_ok = [
        lien("saisie", "n1"),
        lien("n1", "s"),
        lien("s", "x", "oui"),
        lien("s", "y", "non"),
        lien("x", "grappes"),
        lien("y", "grappes"),
    ]
    gardes, _ = appliquer(
        [ligne("Asso", ["a"], genre="association"), ligne("Boîte", ["a"], genre="entreprise")],
        comp(plan(base, liens_ok)),
    )
    assert len(gardes) == 2  # oui ET non vont à Grappes : tout passe
    # seule la sortie « oui » mène à Grappes : on ne garde que les associations ; la sortie « non » seule : les autres
    solo_oui = [lien("saisie", "n1"), lien("n1", "s"), lien("s", "x", "oui"), lien("x", "grappes")]
    assert [
        g["nom"]
        for g in appliquer(
            [ligne("Asso", ["a"]), ligne("Boîte", ["a"], genre="entreprise")], comp(plan(base[:5], solo_oui))
        )[0]
    ] == ["Asso"]
    solo_non = [lien("saisie", "n1"), lien("n1", "s"), lien("s", "x", "non"), lien("x", "grappes")]
    assert [
        g["nom"]
        for g in appliquer(
            [ligne("Asso", ["a"]), ligne("Boîte", ["a"], genre="entreprise")], comp(plan(base[:5], solo_non))
        )[0]
    ] == ["Boîte"]


def test_pays_nom_ou_code_c_est_pareil():
    o = [outil("filtre", options=[("Garder si le champ", "pays"), ("est égal à", "France")])]
    p = plan(
        [("saisie",), ("grappes",), ("n1", "a"), ("f", "filtre")],
        [lien("saisie", "n1"), lien("n1", "f"), lien("f", "grappes")],
    )
    c = compiler(p, SOURCES, o, pays_equiv=PAYS)
    assert len(appliquer([ligne("X", ["a"])], c)[0]) == 1  # le candidat porte « FR », le filtre dit « France »


@pytest.mark.parametrize(
    "opts,mot",
    [
        ([("Garder si le champ", "couleur"), ("est égal à", "x")], "n'existe pas"),
        ([("Garder si le champ", "ville"), ("est égal à", "")], "comparé"),
    ],
)
def test_un_filtre_incoherent_est_refuse_avant_tout_appel(opts, mot):
    p = plan(
        [("saisie",), ("grappes",), ("n1", "a"), ("f", "filtre", None, opts)],
        [lien("saisie", "n1"), lien("n1", "f"), lien("f", "grappes")],
    )
    with pytest.raises(ConfigRefusee, match=mot):
        comp(p)


def _plan_filtre(opts):
    o = [outil("filtre", options=opts)]
    p = plan([("saisie",), ("grappes",), ("n1", "a"), ("f", "filtre")], [lien("saisie", "n1"), lien("n1", "f"), lien("f", "grappes")])
    return compiler(p, SOURCES, o, pays_equiv=PAYS)


def test_plusieurs_conditions_combinees_par_et_ou_ou():
    et = [("Champ 1", "ville"), ("Comparateur 1", "est égal à"), ("Valeur 1", "Lyon"),
          ("Champ 2", "genre"), ("Comparateur 2", "est égal à"), ("Valeur 2", "association"), ("Combinateur", "et")]  # fmt: skip
    noms = lambda c: {g["nom"] for g in appliquer([ligne("A", ["a"], ville="Lyon", genre="association"), ligne("B", ["a"], ville="Lyon", genre="entreprise")], c)[0]}
    assert noms(_plan_filtre(et)) == {"A"}  # B : genre différent, tombe sur la deuxième condition
    ou = [*et[:-1], ("Combinateur", "ou")]
    assert noms(_plan_filtre(ou)) == {"A", "B"}  # B passe quand même : « ville = Lyon » suffit en OU


@pytest.mark.parametrize(
    "comparateur,valeur_opt,nom_passe,nom_tombe",
    [
        ("est différent de", "Lyon", "B", "A"),
        ("contient", "yo", "A", "B"),
        ("ne contient pas", "yo", "B", "A"),
        ("commence par", "Ly", "A", "B"),
        ("finit par", "on", "A", "B"),
        ("est vide", "", "C", "A"),
        ("n'est pas vide", "", "A", "C"),
    ],
)
def test_les_huit_comparateurs(comparateur, valeur_opt, nom_passe, nom_tombe):
    opts = [("Champ 1", "ville"), ("Comparateur 1", comparateur), ("Valeur 1", valeur_opt)]
    c = _plan_filtre(opts)
    lignes = [ligne("A", ["a"], ville="Lyon"), ligne("B", ["a"], ville="Paris"), ligne("C", ["a"], ville="")]
    gardes = {g["nom"] for g in appliquer(lignes, c)[0]}
    assert nom_passe in gardes and nom_tombe not in gardes


def test_filtre_corroboration_et_fiabilite_minimale():
    c_corr = _plan_filtre([("Champ 1", "Nombre de sources"), ("Valeur 1", "2")])
    lignes = [ligne("Confirme", ["a", "b"]), ligne("Seul", ["a"])]
    assert {g["nom"] for g in appliquer(lignes, c_corr)[0]} == {"Confirme"}

    o_fiab = [outil("filtre", options=[("Champ 1", "Fiabilité minimale"), ("Valeur 1", "C")])]
    p_fiab = plan([("saisie",), ("grappes",), ("na", "a"), ("nb", "b"), ("f", "filtre")],
                  [lien("saisie", "na"), lien("saisie", "nb"), lien("na", "f"), lien("nb", "f"), lien("f", "grappes")])  # fmt: skip
    c_fiab = compiler(p_fiab, SOURCES, o_fiab, pays_equiv=PAYS)
    fiabilites = {"a": "B", "b": "E"}
    assert {g["nom"] for g in appliquer([ligne("ParA", ["a"]), ligne("ParB", ["b"])], c_fiab, fiabilites_sources=fiabilites)[0]} == {"ParA"}


def test_filtre_garder_au_maximum_tronque_apres_les_conditions():
    c = _plan_filtre([("Champ 1", "pays"), ("Comparateur 1", "est égal à"), ("Valeur 1", "FR"), ("Garder au maximum", "2")])
    lignes = [ligne(f"N{i}", ["a"]) for i in range(5)]
    gardes = appliquer(lignes, c)[0]
    assert [g["nom"] for g in gardes] == ["N0", "N1"]  # les deux premiers qui arrivent au filtre, dans l'ordre


def test_un_plan_qui_tourne_en_rond_ou_un_outil_eteint_est_refuse():
    p = plan(
        [("saisie",), ("grappes",), ("n1", "a"), ("x", "fusion"), ("y", "fusion")],
        [lien("saisie", "n1"), lien("n1", "x"), lien("x", "y"), lien("y", "x"), lien("y", "grappes")],
    )
    with pytest.raises(ConfigRefusee, match="tourne en rond"):
        comp(p)
    p2 = plan(
        [("saisie",), ("grappes",), ("n1", "a"), ("i", "ia")],
        [lien("saisie", "n1"), lien("n1", "i"), lien("i", "grappes")],
    )
    with pytest.raises(ConfigRefusee, match="éteint"):
        comp(p2)


def test_la_verification_agit_sur_les_resultats_des_sources_placees_avant_elle():
    p = plan(
        [("saisie",), ("grappes",), ("n1", "a"), ("n2", "b"), ("nv", "v")],
        [lien("saisie", "n1"), lien("saisie", "n2"), lien("n1", "nv"), lien("nv", "grappes"), lien("n2", "grappes")],
    )
    c = comp(p)
    assert c["sources"] == ["a", "b"] and c["verificateurs"] == [{"id": "v", "en_amont": ["a"], "fonction": "verifier"}]
    assert any("vérifie les résultats des sources placées avant" in x["texte"] for x in c["appliques"])


def test_fusion_sensibilite_et_regle_de_doublon_sont_reglables():
    def fusion_de(opts):
        p = plan([("saisie",), ("grappes",), ("n1", "a"), ("fu", "fusion", None, opts)], [lien("saisie", "n1"), lien("n1", "fu"), lien("fu", "grappes")])
        return comp(p)["fusion"]

    assert fusion_de([["Même entité si", "Normal"], ["En cas de doublon, garder", "la plus fiable"]]) == {"tuile": "fu", "seuil": 0.20, "garder": "fiable"}
    assert fusion_de([["Même entité si", "Large"], ["En cas de doublon, garder", "la plus récente"]]) == {"tuile": "fu", "seuil": 0.10, "garder": "recente"}
    assert fusion_de([["Même entité si", "Strict"], ["En cas de doublon, garder", "la première trouvée"]]) == {"tuile": "fu", "seuil": 0.40, "garder": "premiere"}


def test_format_fusion_et_ce_qui_n_est_pas_applique():
    p = plan([("saisie",), ("grappes",), ("n1", "a"), ("fo", "format"), ("fu", "fusion"), ("bo", "boucle"), ("at", "attente")],
             [lien("saisie", "n1"), lien("n1", "fu"), lien("fu", "fo"), lien("fo", "bo"), lien("bo", "at"), lien("at", "grappes")])  # fmt: skip
    c = comp(p)
    assert c["format"] == ["csv"]
    assert {x["nom"] for x in c["non_appliques"]} == {"bo"} and all(x["raison"] for x in c["non_appliques"])
    assert {x["nom"] for x in c["appliques"]} >= {"fo", "fu", "at"}  # attente (3.8.07) est désormais appliquée : « sauter » est déjà le comportement par défaut
    assert c["attente"] == {"tuile": "at", "action": "sauter"}


def test_attente_choix_arreter_toute_la_recherche():
    p = plan([("saisie",), ("grappes",), ("n1", "a"), ("at", "attente", None, [["Quand le quota est atteint", "Arrêter toute la recherche"]])],
             [lien("saisie", "n1"), lien("n1", "at"), lien("at", "grappes")])  # fmt: skip
    c = comp(p)
    assert c["attente"] == {"tuile": "at", "action": "arreter"}
    assert any("arrête toute la recherche" in x["texte"] for x in c["appliques"] if x["nom"] == "at")


# 2.3 (retour du 08/11/2026) : le plafond PROPRE à la recherche reste non appliqué (NON_APPLIQUES, inchangé),
# mais son seuil et son action « Prévenir » sont désormais extraits pour l'alerte du Tableau de bord.
def test_budget_alerte_extraite_montant_fixe_par_defaut():
    p = plan([("saisie",), ("grappes",), ("n1", "a"), ("bu", "budget")],
             [lien("saisie", "n1"), lien("n1", "bu"), lien("bu", "grappes")])  # fmt: skip
    c = comp(p)
    assert c["budget_alerte"] == {"tuile": "bu", "nom": "bu", "type": "montant", "montant": 5.0, "seuil_pct": 80.0, "prevenir": True}
    assert any("plafond de dépense est celui de Réglages" in x["raison"] for x in c["non_appliques"] if x["nom"] == "bu")


def test_budget_alerte_pourcentage_et_action_ne_rien_faire():
    p = plan(
        [("saisie",), ("grappes",), ("n1", "a"),
         ("bu", "budget", None, [["Budget maximum", "Pourcentage du plafond mensuel"], ["Pourcentage du plafond mensuel", "10"], ["À partir de", "50"], ["Action", "Ne rien faire"]])],
        [lien("saisie", "n1"), lien("n1", "bu"), lien("bu", "grappes")],
    )  # fmt: skip
    c = comp(p)
    assert c["budget_alerte"] == {"tuile": "bu", "nom": "bu", "type": "pourcentage", "pourcentage": 10.0, "seuil_pct": 50.0, "prevenir": False}


def test_boucle_non_appliquee_dit_pourquoi_selon_l_origine():
    def non_applique(opts):
        p = plan([("saisie",), ("grappes",), ("n1", "a"), ("bo", "boucle", None, opts)], [lien("saisie", "n1"), lien("n1", "bo"), lien("bo", "grappes")])
        return comp(p)["non_appliques"][0]["raison"]

    assert "liste" in non_applique([["Origine de la liste", "Liste collée"], ["Liste", "Lyon\nParis"]])
    assert "2 élément" in non_applique([["Origine de la liste", "Liste collée"], ["Liste", "Lyon\nParis"]])
    assert "fichier importé" in non_applique([["Origine de la liste", "Fichier importé"]])
    assert "tuile précédente" in non_applique([["Origine de la liste", "Résultat d'une tuile précédente"]])


def test_format_lit_le_vrai_registre_pas_seulement_csv_json():
    """3.8.01 : « xlsx » et « webhook » (ni dans l'ancienne liste figée) sont des formats réels du registre."""
    p = plan([("saisie",), ("grappes",), ("n1", "a"), ("fo", "format", None, [["Format de sortie", "XLSX WEBHOOK"]])],
             [lien("saisie", "n1"), lien("n1", "fo"), lien("fo", "grappes")])  # fmt: skip
    c = comp(p)
    assert c["format"] == ["webhook", "xlsx"]  # ordre du registre (alphabétique par module), pas celui saisi dans l'option
    assert any("Excel" in x["texte"] and "Webhook" in x["texte"] for x in c["appliques"] if x["nom"] == "fo")


def test_format_inconnu_refuse_avec_la_liste_reelle():
    p = plan([("saisie",), ("grappes",), ("n1", "a"), ("fo", "format", None, [["Format de sortie", "PDF"]])],
             [lien("saisie", "n1"), lien("n1", "fo"), lien("fo", "grappes")])  # fmt: skip
    with pytest.raises(ConfigRefusee, match="Excel"):
        comp(p)


def plan_requete_avancee(opts, apres=False):
    noeuds = [("saisie",), ("grappes",), ("r", "requete_avancee", None, opts), ("nd", "d"), ("na", "a")]
    liens = (
        [lien("saisie", "nd"), lien("saisie", "na"), lien("nd", "r"), lien("na", "r"), lien("r", "grappes")]
        if apres
        else [lien("saisie", "r"), lien("r", "nd"), lien("r", "na"), lien("nd", "grappes"), lien("na", "grappes")]
    )
    return plan(noeuds, liens)


# --- 909 §3 : la Requête avancée qualifie la requête des sources placées après elle, et seulement celles qui déclarent comprendre le qualificatif
def test_requete_avancee_qualifie_seulement_les_sources_qui_le_comprennent():
    opts = [("Type de qualificatif", "Limiter à un site/domaine"), ("Valeur", "linkedin.com/in/")]
    c = comp(plan_requete_avancee(opts))
    assert c["requetes"] == {"d": [{"type": "site", "valeur": "linkedin.com/in/"}]}  # « a » ne déclare aucun opérateur
    texte = c["appliques"][0]["texte"]
    assert "D" in texte and "ignoré" in texte and "A" in texte


def test_requete_avancee_posee_apres_les_sources_non_appliquee():
    opts = [("Type de qualificatif", "Limiter à un site/domaine"), ("Valeur", "linkedin.com/in/")]
    c = comp(plan_requete_avancee(opts, apres=True))
    assert c["requetes"] == {} and "après les sources" in c["non_appliques"][0]["raison"]


def test_requete_avancee_sans_valeur_non_appliquee():
    opts = [("Type de qualificatif", "Limiter à un site/domaine"), ("Valeur", "")]
    c = comp(plan_requete_avancee(opts))
    assert c["requetes"] == {} and "aucune valeur" in c["non_appliques"][0]["raison"]


def test_requete_avancee_type_inconnu_est_refuse():
    opts = [("Type de qualificatif", "Bidon"), ("Valeur", "x")]
    with pytest.raises(ConfigRefusee, match="qualificatif"):
        comp(plan_requete_avancee(opts))


def test_requete_avancee_une_source_posee_deux_fois_est_qualifiee_une_fois():
    opts = [("Type de qualificatif", "Limiter à un site/domaine"), ("Valeur", "linkedin.com/in/")]
    noeuds = [("saisie",), ("grappes",), ("r", "requete_avancee", None, opts), ("n1", "d"), ("n2", "d")]
    liens = [lien("saisie", "r"), lien("r", "n1"), lien("r", "n2"), lien("n1", "grappes"), lien("n2", "grappes")]
    assert comp(plan(noeuds, liens))["requetes"] == {"d": [{"type": "site", "valeur": "linkedin.com/in/"}]}


@pytest.mark.parametrize(
    "qualificatif, valeur_saisie",
    [
        ("Limiter à un site/domaine", "exemple.test inurl:admin"),  # un opérateur de plus, glissé dans la valeur
        ("Limiter à un type de fichier", "env"),  # famille reconnaissance de sécurité, écartée par la spécification
        ("Exclure un mot", "deux mots"),  # seul le premier serait exclu
        ("Phrase exacte", 'une "phrase'),  # casserait les guillemets
    ],
)
def test_requete_avancee_une_valeur_hors_du_vocabulaire_est_refusee(qualificatif, valeur_saisie):
    with pytest.raises(ConfigRefusee):
        comp(plan_requete_avancee([("Type de qualificatif", qualificatif), ("Valeur", valeur_saisie)]))


def test_requete_avancee_type_de_fichier_document_accepte_et_normalise():
    opts = [("Type de qualificatif", "Limiter à un type de fichier"), ("Valeur", ".PDF")]
    assert comp(plan_requete_avancee(opts))["requetes"] == {"d": [{"type": "filetype", "valeur": "pdf"}]}


def plan_traduction(opts):
    return plan(
        [("saisie",), ("grappes",), ("t", "traduction", None, opts), ("n1", "a"), ("n3", "c")],
        [lien("saisie", "t"), lien("t", "n1"), lien("t", "n3"), lien("n1", "grappes"), lien("n3", "grappes")],
    )


def test_traduction_vers_la_langue_de_chaque_source():
    ok = [("Langue d'entrée", "détecter"), ("Traduire vers", "français, anglais"), ("Ne pas traduire", "rien")]
    c = comp(plan_traduction(ok), langue_saisie="fr", traduction_disponible=True)
    assert c["traductions"] == {
        "c": {"tuile": "t", "de": "fr", "vers": "en", "presets": []}
    }  # la source « a » cherche déjà en français : rien à traduire
    # sans moteur de traduction, avec la protection des noms propres, ou sans langue de saisie : non appliquée, avec la raison
    assert "moteur de traduction" in comp(plan_traduction(ok), langue_saisie="fr")["non_appliques"][0]["raison"]
    propres = [
        ("Langue d'entrée", "détecter"),
        ("Traduire vers", "français, anglais"),
        ("Ne pas traduire", "les noms propres"),
    ]
    assert (
        "entités nommées"
        in comp(plan_traduction(propres), langue_saisie="fr", traduction_disponible=True)["non_appliques"][0]["raison"]
    )
    # 3.8.02 : la détection de la langue de la saisie a échoué (pas de langue_saisie) — la tuile ne refuse plus de
    # fonctionner, elle laisse le moteur de traduction détecter lui-même (de="auto") au lieu d'exiger une langue en amont.
    sans_detection = comp(plan_traduction(ok), traduction_disponible=True)
    assert sans_detection["non_appliques"] == []
    assert sans_detection["traductions"] == {
        "a": {"tuile": "t", "de": "auto", "vers": "fr", "presets": []},
        "c": {"tuile": "t", "de": "auto", "vers": "en", "presets": []},
    }
    with pytest.raises(ConfigRefusee, match="langue"):
        comp(
            plan_traduction(
                [("Langue d'entrée", "français"), ("Traduire vers", "klingon"), ("Ne pas traduire", "rien")]
            ),
            traduction_disponible=True,
        )


def test_traduction_langue_d_entree_multiple_restreint_la_detection():
    # 7.3 (retour du 08/11/2026) : « Langue d'entrée » devient multiple, au sens « détecte uniquement parmi ces
    # langues-là » — un texte détecté hors de la liste cochée retombe sur « auto » plutôt que d'être pris tel quel
    # (le cas que Sednal voulait éviter : un texte français pris pour du portugais).
    opts = [("Langue d'entrée", "français, anglais, allemand"), ("Traduire vers", "anglais"), ("Ne pas traduire", "rien")]
    dans_la_liste = comp(plan_traduction(opts), langue_saisie="fr", traduction_disponible=True)
    assert dans_la_liste["traductions"]["c"] == {"tuile": "t", "de": "fr", "vers": "en", "presets": []}
    hors_liste = comp(plan_traduction(opts), langue_saisie="pt", traduction_disponible=True)
    assert hors_liste["traductions"]["c"]["de"] == "auto"


def test_traduction_ne_pas_traduire_presets_et_interrupteur_global():
    avec_presets = [
        ("Langue d'entrée", "détecter"), ("Traduire vers", "anglais"), ("Ne pas traduire", "majuscules, urls"), ("Protéger certains mots", "oui"),
    ]  # fmt: skip
    c = comp(plan_traduction(avec_presets), langue_saisie="fr", traduction_disponible=True)
    assert c["traductions"]["c"]["presets"] == ["majuscules", "urls_emails"]
    # l'interrupteur global coupé : plus aucun preset ne s'applique, même cochés dans « Ne pas traduire »
    coupe = [*avec_presets[:3], ("Protéger certains mots", "non")]
    c2 = comp(plan_traduction(coupe), langue_saisie="fr", traduction_disponible=True)
    assert c2["traductions"]["c"]["presets"] == []


def test_un_script_d_outil_est_joue_et_un_script_en_echec_ne_retire_rien_en_silence():
    o = [
        *OUTILS,
        outil(
            "garder-fr",
            nature="script",
            code="def run(resultats):\n    return [r for r in resultats if r['ville'] == 'Lyon']",
        ),
    ]
    p = plan(
        [("saisie",), ("grappes",), ("n1", "a"), ("s", "garder-fr")],
        [lien("saisie", "n1"), lien("n1", "s"), lien("s", "grappes")],
    )
    c = compiler(p, SOURCES, o, pays_equiv=PAYS)

    def lance(code, entree):
        liste = json.loads(entree)
        return {"ok": True, "sortie": json.dumps([r for r in liste if r["ville"] == "Lyon"])}

    gardes, bilan = appliquer([ligne("Lyonnais", ["a"]), ligne("Parisien", ["a"], ville="Paris")], c, lance)
    assert [x["nom"] for x in gardes] == ["Lyonnais"] and bilan["par_tuile"]["s"]["n"] == 1
    gardes, bilan = appliquer(
        [ligne("Lyonnais", ["a"]), ligne("Parisien", ["a"], ville="Paris")],
        c,
        lambda code, e: {"ok": False, "erreur": "boum"},
    )
    assert (
        len(gardes) == 2 and "boum" in bilan["erreurs"][0]
    )  # un script cassé ne fait pas disparaître des noms : on le dit


def test_une_verification_posee_apres_une_source_ne_juge_que_ses_resultats(monkeypatch):
    from pilote import adaptateurs
    from pilote.pont.verification import verifier_candidats

    vus = []

    class Faux:
        @staticmethod
        def chercher(entree, client, parametres):
            vus.append(entree["nom"])
            return []

    monkeypatch.setattr(adaptateurs, "charger", lambda nom: Faux)
    lignes = [
        {"nom": "De A", "site": "a.example", "trouve_par": ["a"]},
        {"nom": "De B", "site": "b.example", "trouve_par": ["b"]},
        {"nom": "Des deux", "site": "c.example", "trouve_par": ["a", "b"]},
    ]
    v = {"source": "v", "verifie_sur": "site", "module": "faux", "parametres": {}, "cles_noms": [], "en_amont": ["a"]}
    bilans = verifier_candidats(lignes, {"verificateurs": [v]}, {}, lambda: False, 60.0, lambda *a, **k: None)
    assert (
        vus == ["De A", "Des deux"] and bilans[0]["a_verifier"] == 2
    )  # « De B » n'a pas été trouvé par une source placée avant la vérification
    vus.clear()
    verifier_candidats(
        lignes, {"verificateurs": [{**v, "en_amont": None}]}, {}, lambda: False, 60.0, lambda *a, **k: None
    )
    assert len(vus) == 3  # sans source avant elle, elle vérifie tous les résultats


def test_le_journal_ne_dit_retire_que_ce_qui_l_est_vraiment():
    """Partie 2 de test.md (S2) : un nom tombé sur une branche mais gardé par une autre n'est pas « retiré »."""
    base = [("saisie",), ("grappes",), ("n1", "a"), ("s", "si"), ("x", "fusion"), ("y", "fusion")]
    liens = [lien("saisie", "n1"), lien("n1", "s"), lien("s", "x", "oui"), lien("s", "y", "non"), lien("x", "grappes"), lien("y", "grappes")]
    gardes, bilan = appliquer([ligne("Asso", ["a"], genre="association"), ligne("Boîte", ["a"], genre="entreprise")], comp(plan(base, liens)))
    assert len(gardes) == 2 and bilan["retires"] == 0 and bilan["par_tuile"] == {}  # oui ET non mènent à Grappes : personne n'est retiré
    seul_oui = [lien("saisie", "n1"), lien("n1", "s"), lien("s", "x", "oui"), lien("x", "grappes")]
    gardes, bilan = appliquer([ligne("Asso", ["a"], genre="association"), ligne("Boîte", ["a"], genre="entreprise")], comp(plan(base[:5], seul_oui)))
    assert [g["nom"] for g in gardes] == ["Asso"] and bilan["par_tuile"]["s"]["noms"] == ["Boîte"] and bilan["par_tuile"]["s"]["n"] == 1  # la condition dit « association » : la boîte tombe, et c'est dit


OUTILS_IA_ON = [outil("ia") if o["id"] == "ia" else o for o in OUTILS]


def comp_ia(p, disponible=True):
    return compiler(p, SOURCES, OUTILS_IA_ON, pays_equiv=PAYS, ia_disponible=disponible)


def test_ia_choisit_l_operation_et_le_modele():
    """Décision 901/3.8.09 : l'Assistant IA est enfin câblé dans le plan compilé (NON_APPLIQUES ne le cite plus)."""
    p = plan(
        [("saisie",), ("grappes",), ("n1", "a"), ("ia", "ia", None, [["Opération", "Résumer"], ["Modèle", "haiku"], ["Marquer les résultats", "oui"]])],
        [lien("saisie", "n1"), lien("n1", "ia"), lien("ia", "grappes")],
    )  # fmt: skip
    c = comp_ia(p)
    assert c["ia"] == {"tuile": "ia", "operation": "resumer", "modele": "haiku", "effort": "", "marquer": True, "plafond": None, "categories": ""}
    assert any("Résumer" in x["texte"] for x in c["appliques"] if x["nom"] == "ia")
    assert "ia" not in {x["nom"] for x in c["non_appliques"]}


def test_ia_operation_inconnue_refuse():
    p = plan(
        [("saisie",), ("grappes",), ("n1", "a"), ("ia", "ia", None, [["Opération", "Autre chose"]])],
        [lien("saisie", "n1"), lien("n1", "ia"), lien("ia", "grappes")],
    )  # fmt: skip
    with pytest.raises(ConfigRefusee, match="opération connue"):
        comp_ia(p)


def test_ia_marquer_non_desactive_le_marquage():
    p = plan(
        [("saisie",), ("grappes",), ("n1", "a"), ("ia", "ia", None, [["Opération", "Classer / catégoriser"], ["Catégories", "sport, culture"], ["Marquer les résultats", "non"]])],
        [lien("saisie", "n1"), lien("n1", "ia"), lien("ia", "grappes")],
    )  # fmt: skip
    assert comp_ia(p)["ia"] == {"tuile": "ia", "operation": "classer", "modele": "", "effort": "", "marquer": False, "plafond": None, "categories": "sport, culture"}


# 12.2 (retour du 08/11/2026) : « Classer / catégoriser » retombait sur « autre » faute d'un champ pour saisir
# les catégories ; refuser de lancer tant qu'elles ne sont pas données, plutôt que de tout classer en silence.
def test_ia_classer_sans_categories_refuse():
    p = plan(
        [("saisie",), ("grappes",), ("n1", "a"), ("ia", "ia", None, [["Opération", "Classer / catégoriser"]])],
        [lien("saisie", "n1"), lien("n1", "ia"), lien("ia", "grappes")],
    )  # fmt: skip
    with pytest.raises(ConfigRefusee, match="catégories"):
        comp_ia(p)


def test_ia_une_seule_tuile_jouee():
    p = plan(
        [("saisie",), ("grappes",), ("n1", "a"), ("ia1", "ia", None, [["Opération", "Résumer"]]), ("ia2", "ia", None, [["Opération", "Résumer"]])],
        [lien("saisie", "n1"), lien("n1", "ia1"), lien("ia1", "ia2"), lien("ia2", "grappes")],
    )  # fmt: skip
    c = comp_ia(p)
    assert c["ia"]["tuile"] == "ia1"
    assert any(x["nom"] == "ia2" for x in c["non_appliques"])


def test_ia_sans_agent_installe_n_est_pas_appliquee_et_le_dit():
    """3.8.09, « Comment momo vérifie » : agent absent -> la tuile refuse de s'appliquer et le dit, comme Traduction sans adresse."""
    p = plan(
        [("saisie",), ("grappes",), ("n1", "a"), ("ia", "ia", None, [["Opération", "Résumer"]])],
        [lien("saisie", "n1"), lien("n1", "ia"), lien("ia", "grappes")],
    )  # fmt: skip
    c = comp_ia(p, disponible=False)
    assert c["ia"] is None and "n'est pas installé" in c["non_appliques"][0]["raison"]


# 908, point 13 (retour du 08/11/2026) : seul le niveau 1 a un mécanisme réel ; les trois autres sont refusés
# avec une raison claire, jamais appliqués à l'aveugle.
def test_ia_niveau_1_par_defaut_est_applique():
    p = plan(
        [("saisie",), ("grappes",), ("n1", "a"), ("ia", "ia", None, [["Opération", "Résumer"]])],
        [lien("saisie", "n1"), lien("n1", "ia"), lien("ia", "grappes")],
    )  # fmt: skip
    assert comp_ia(p)["ia"] is not None  # pas de « Niveau » réglé : niveau 1 implicite, jamais un refus sur un réglage ancien


def test_ia_niveaux_2_a_4_sont_refuses_avec_leur_numero():
    for niveau in ("2 — Aider à trier", "3 — Extraire et formuler", "4 — Chercher elle-même"):
        p = plan(
            [("saisie",), ("grappes",), ("n1", "a"), ("ia", "ia", None, [["Opération", "Résumer"], ["Niveau", niveau]])],
            [lien("saisie", "n1"), lien("n1", "ia"), lien("ia", "grappes")],
        )  # fmt: skip
        c = comp_ia(p)
        assert c["ia"] is None
        assert f"niveau {niveau[0]}" in c["non_appliques"][0]["raison"] and "pas encore branché" in c["non_appliques"][0]["raison"]


def test_ia_effort_menu_ferme():
    def ia_de(effort):
        p = plan(
            [("saisie",), ("grappes",), ("n1", "a"), ("ia", "ia", None, [["Opération", "Résumer"], ["Effort", effort]])],
            [lien("saisie", "n1"), lien("n1", "ia"), lien("ia", "grappes")],
        )  # fmt: skip
        return comp_ia(p)["ia"]

    assert ia_de("élevé")["effort"] == "high" and ia_de("très élevé")["effort"] == "xhigh" and ia_de("par défaut")["effort"] == ""
    with pytest.raises(ConfigRefusee, match="effort"):
        ia_de("énorme")


def test_ia_ne_traite_que_les_noms_qui_atteignent_sa_tuile():
    """3.8.09 : « applique l'opération aux résultats qui atteignent cette tuile » — la branche de B ne passe pas par elle."""
    p = plan(
        [("saisie",), ("grappes",), ("n1", "a"), ("n2", "b"), ("ia", "ia", None, [["Opération", "Résumer"]])],
        [lien("saisie", "n1"), lien("n1", "ia"), lien("ia", "grappes"), lien("saisie", "n2"), lien("n2", "grappes")],
    )  # fmt: skip
    lignes = [ligne("De A", ["a"]), ligne("De B", ["b"]), ligne("Des deux", ["a", "b"])]
    gardees, bilan = appliquer(lignes, comp_ia(p))
    assert [gardees[k]["nom"] for k in bilan["ia"]] == ["De A", "Des deux"]
    assert bilan["tuiles"]["ia"] == {"nom": "ia", "entrees": 2, "sorties": 2}  # le compteur de tuile (1.1 §8) la voit passer


def test_la_tuile_jouee_ne_depend_pas_du_hasard_du_processus():
    """Revue 902 : l'ordre des outils venait d'un ensemble (hachage aléatoire par processus) : la tuile Fusion / Attente /
    Assistant IA « jouée » changeait d'un lancement à l'autre. Elle suit maintenant l'ordre du plan."""
    import subprocess
    import sys

    code = (
        "import sys; sys.path.insert(0, 'tests');"
        "from test_suite_plan import comp_ia, plan, lien;"
        "p = plan([('saisie',), ('grappes',), ('n1', 'a'), ('ia1', 'ia', None, [['Opération', 'Résumer']]), ('ia2', 'ia', None, [['Opération', 'Résumer']])],"
        "[lien('saisie', 'n1'), lien('n1', 'ia1'), lien('ia1', 'ia2'), lien('ia2', 'grappes')]);"
        "print(comp_ia(p)['ia']['tuile'])"
    )
    vus = {subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env={"PYTHONHASHSEED": str(g), "PATH": ""}, check=True).stdout.strip() for g in range(6)}
    assert vus == {"ia1"}


def test_rsshub_sans_instance_reglee_n_est_pas_appliquee_et_le_dit():
    """3.8.10 : « Sans suite.rsshub_url réglée : la tuile refuse de s'appliquer et le dit »."""
    p = plan(
        [("saisie",), ("grappes",), ("n1", "a"), ("r", "rsshub", None, [["Site à transformer", "https://www.exemple.fr/politique"]])],
        [lien("saisie", "n1"), lien("n1", "grappes"), lien("saisie", "r"), lien("r", "grappes")],
    )  # fmt: skip
    c = comp(p)
    assert c["rsshub"] == [] and "aucune instance RSSHub" in c["non_appliques"][0]["raison"]
    c = comp(p, rsshub_disponible=True)
    assert c["rsshub"] == [{"tuile": "r", "nom": "r", "site": "https://www.exemple.fr/politique"}] and c["non_appliques"] == []


def test_rsshub_sans_adresse_de_site_est_refusee():
    p = plan(
        [("saisie",), ("grappes",), ("r", "rsshub", None, [["Site à transformer", "adresse du site"]])],
        [lien("saisie", "r"), lien("r", "grappes")],
    )  # fmt: skip
    with pytest.raises(ConfigRefusee, match="adresse du site à transformer"):
        comp(p, rsshub_disponible=True)


def test_ia_plafond_traiter_au_maximum():
    def ia_de(valeur):
        p = plan(
            [("saisie",), ("grappes",), ("n1", "a"), ("ia", "ia", None, [["Opération", "Résumer"], ["Traiter au maximum", valeur]])],
            [lien("saisie", "n1"), lien("n1", "ia"), lien("ia", "grappes")],
        )  # fmt: skip
        return comp_ia(p)["ia"]["plafond"]

    assert ia_de("5") == 5 and ia_de("") is None and ia_de("beaucoup") is None
