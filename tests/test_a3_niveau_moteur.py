"""A3 (spec 912), moteur : en mode extraction, `resultat.csv` ne contient que les noms sûrs ; les autres vont dans
`resultat_a_verifier.csv`. Aucun réseau."""

from grappes import vraisemblance as vr
from grappes.classement import production as pr
from grappes.classement.candidats import Candidat
from grappes.sortie import charger_profils


def _c(ref, nom, **k):
    return Candidat(ref, nom, "x", 0, "registre", 0, 0, 0, **k)


SUR_REGISTRE = _c("reg:sirene:1", "Atelier du Phare", registres={"sirene"})
SUR_DEUX = _c(
    "ner:club des vents", "Club des Vents", ner_sites={"a.example": 0.9, "b.example": 0.8}
)
SUR_CITE = _c("web:voiles.example", "Voiles du Large", editeurs=2)
UNE_PAGE = _c("ner:amis du quai", "Amis du Quai", ner_sites={"a.example": 0.9})
ENCYCLO = _c("reg:wikidata:Q1", "Cercle des Dunes", registres={"wikidata"})


def test_niveau_d_un_candidat():
    assert [pr.niveau_de(c) for c in (SUR_REGISTRE, SUR_DEUX, SUR_CITE)] == ["sûr"] * 3
    # une seule page, ou la seule encyclopédie (qui n'est pas un registre de première main) : à vérifier
    assert [pr.niveau_de(c) for c in (UNE_PAGE, ENCYCLO)] == ["à vérifier"] * 2


def _lignes():
    lr = vr.charger()
    cls = [(c, 1.0, 0.9) for c in (SUR_REGISTRE, UNE_PAGE, SUR_DEUX, ENCYCLO)]
    return pr.lignes(cls, pr.ClassementConfig(), lr, pr.Calibreur(), "FR")


def test_les_lignes_portent_le_niveau():
    assert [l.niveau for l in _lignes()] == ["sûr", "à vérifier", "sûr", "à vérifier"]


def test_en_extraction_resultat_ne_garde_que_les_surs(tmp_path):
    (tmp_path / "resultat_a_verifier.csv").write_text("périmé", encoding="utf-8")
    chemins = pr.ecrire_sorties(
        _lignes(), charger_profils("config"), tmp_path, remplace_resultat=True
    )
    assert (tmp_path / "resultat.csv").read_text(encoding="utf-8").splitlines() == [
        "NOM",
        "Atelier du Phare",
        "Club des Vents",
    ]
    assert (tmp_path / "resultat_tsites.csv").read_text(encoding="utf-8").count("\n") == 3
    av = (tmp_path / "resultat_a_verifier.csv").read_text(encoding="utf-8").splitlines()
    assert av[0] == "nom;ville;sources" and [x.split(";")[0] for x in av[1:]] == [
        "Amis du Quai",
        "Cercle des Dunes",
    ]
    brut = (tmp_path / "resultat_brut.csv").read_text(encoding="utf-8").splitlines()
    assert (
        "niveau" in brut[0].split(";") and len(brut) == 5
    )  # le fichier complet garde tout, avec le niveau
    assert tmp_path / "resultat_a_verifier.csv" in chemins


def test_sans_nom_a_verifier_le_fichier_perime_disparait(tmp_path):
    (tmp_path / "resultat_a_verifier.csv").write_text("périmé", encoding="utf-8")
    pr.ecrire_sorties(
        [l for l in _lignes() if l.niveau == "sûr"],
        charger_profils("config"),
        tmp_path,
        remplace_resultat=True,
    )
    assert not (tmp_path / "resultat_a_verifier.csv").exists()


def test_hors_extraction_rien_ne_change(tmp_path):
    chemins = pr.ecrire_sorties(
        _lignes(), charger_profils("config"), tmp_path, remplace_resultat=False
    )
    assert [p.name for p in chemins] == ["resultat_brut.csv"] and not (
        tmp_path / "resultat_a_verifier.csv"
    ).exists()
