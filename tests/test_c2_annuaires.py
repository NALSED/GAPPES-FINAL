"""C2 (spec 912) : une page dont l'essentiel est une liste (un annuaire) est lue en entier, dans un plafond écrit en configuration.
Une page ordinaire garde les limites d'avant. Aucun réseau."""

from pathlib import Path

from grappes.autonomy import Autonomy, load_autonomy
from grappes.classement import production as pr
from grappes.classement.candidats import Candidat
from grappes.fetch import pages
from grappes.fetch.html import extract


def _annuaire(n: int) -> bytes:
    entrees = "".join(
        f'<li><a href="https://club-{i}.example/">Club des Vents numéro {i}</a>, salle municipale, rue du Port {i}, ouvert le mardi et le jeudi soir</li>'
        for i in range(n)
    )
    return f"<html><head><title>Annuaire des clubs</title></head><body><h1>Tous les clubs</h1><ul>{entrees}</ul></body></html>".encode()


def _article(n_liens: int) -> bytes:
    liens = "".join(f'<a href="https://autre-{i}.example/">lien {i}</a> ' for i in range(n_liens))
    texte = (
        "<p>"
        + ("Un long paragraphe de récit sans aucune liste, qui parle de voile et de vent. " * 400)
        + "</p>"
    )
    return f"<html><head><title>Récit</title></head><body>{texte}<p>{liens}</p><ul><li>un</li><li>deux</li></ul></body></html>".encode()


def test_l_extraction_compte_les_entrees_et_la_part_de_liste():
    a = extract(_annuaire(300), "text/html", "https://annuaire.example/clubs")
    assert a.entrees == 300 and a.part_liste > 0.9
    b = extract(_article(150), "text/html", "https://journal.example/recit")
    assert b.entrees == 2 and b.part_liste < 0.1


def test_une_page_annuaire_est_reconnue_une_page_ordinaire_non():
    reglage = Autonomy()
    assert pages.est_annuaire(extract(_annuaire(300), "text/html", "https://a.example/"), reglage)
    assert not pages.est_annuaire(
        extract(_annuaire(20), "text/html", "https://a.example/"), reglage
    )  # trop peu d'entrées
    assert not pages.est_annuaire(
        extract(_article(150), "text/html", "https://a.example/"), reglage
    )  # beaucoup de liens, mais un récit


def test_les_limites_d_une_page_annuaire_sont_relevees_dans_le_plafond():
    reglage = Autonomy()
    page = extract(_annuaire(300), "text/html", "https://a.example/")
    assert (
        pages.limites(page, reglage)
        == (reglage.annuaire_texte_max, reglage.annuaire_liens_max)
        == (100_000, 500)
    )
    assert (
        len(page.text) > pages.MAX_TEXT and len(page.links) > pages.MAX_LINKS
    )  # l'ancienne coupe en perdait une partie
    assert pages.limites(extract(_article(150), "text/html", "https://a.example/"), reglage) == (
        pages.MAX_TEXT,
        pages.MAX_LINKS,
    )
    court = Autonomy(annuaire_texte_max=30_000, annuaire_liens_max=120)
    assert pages.limites(page, court) == (30_000, 120)  # le plafond est celui de la configuration


def test_le_plafond_se_regle_dans_autonomie_yaml(tmp_path):
    (tmp_path / "autonomie.yaml").write_text(
        "annuaires:\n  texte_max: 50000\n  liens_max: 250\n  entrees_min: 80\n  part_min: 0.6\n",
        encoding="utf-8",
    )
    a = load_autonomy(tmp_path)
    assert (
        a.annuaire_texte_max,
        a.annuaire_liens_max,
        a.annuaire_entrees_min,
        a.annuaire_part_min,
    ) == (50_000, 250, 80, 0.6)
    assert (
        load_autonomy("config").annuaire_texte_max == 100_000
    )  # la configuration livrée porte le plafond, écrit en clair
    assert "annuaires:" in Path("config/autonomie.yaml").read_text(encoding="utf-8")


def test_un_nom_lu_sur_une_seule_page_annuaire_reste_a_verifier():
    c = Candidat(
        "ner:club des vents numero 7",
        "Club des Vents numéro 7",
        "x",
        0,
        "classe",
        0,
        0,
        0,
        ner_sites={"annuaire.example": 0.9},
    )
    assert pr.niveau_de(c) == "à vérifier"
