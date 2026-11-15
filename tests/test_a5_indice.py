"""A5 (spec 912, audit 910 § 3.1) : le signal « écosystèmes » compte ceux des CITANTS ; le poids d'une citation est celui
de l'éditeur qui cite, comme pour les noms lus. Aucun réseau."""

from types import SimpleNamespace

from grappes import vraisemblance as vr
from grappes.classement import indice
from grappes.classement.candidats import Candidat, Contexte, citants_par_cite

LETTRES = {
    "web:presse.example/a": "B",
    "web:presse.example/b": "B",
    "web:blog.example": "E",
    "rss:flux.example": "C",
}


def _ctx(citations):
    rel = SimpleNamespace(letter=lambda ref: LETTRES.get(ref, "F"), factor=lambda ref: 1.0)
    return Contexte(
        cfg=None,
        db=None,
        rel=rel,
        grappe="g",
        candidats=[],
        citations=citations,
        lues=set(),
        citants=citants_par_cite(citations),
    )


def _c(ref="web:club.example", **k):
    return Candidat(ref, "Club des Vents", "x", 0, "classe", 0, 0, 0, lettre="F", **k)


CITS = [
    ("web:presse.example/a", "web:club.example"),
    ("web:presse.example/b", "web:club.example"),
    ("web:blog.example", "web:club.example"),
    ("rss:flux.example", "web:club.example"),
]


def test_les_citants_sont_regroupes_par_editeur():
    par = citants_par_cite(CITS)["web:club.example"]
    assert par == {
        "presse.example": {"web:presse.example/a", "web:presse.example/b"},
        "blog.example": {"web:blog.example"},
        "flux.example": {"rss:flux.example"},
    }


def test_le_poids_d_une_citation_est_celui_de_l_editeur_qui_cite():
    lr = vr.charger()
    ctx = _ctx(CITS)
    c = _c(
        editeurs=3
    )  # l'entité elle-même est notée F : avant A5, ses trois citations ne pesaient presque rien
    e = next(x for x in indice.elements(ctx, c, lr) if x.nature == "citations")
    attendu = lr.v("citation") * (
        vr.poids_lettre("B") + vr.poids_lettre("E") + vr.poids_lettre("C")
    )  # une voix par éditeur
    assert abs(e.log10 - min(attendu, lr.v("citation_plafond"))) < 1e-9
    faible = _ctx([("web:blog.example", "web:club.example")])
    e2 = next(x for x in indice.elements(faible, _c(editeurs=1), lr) if x.nature == "citations")
    assert abs(e2.log10 - lr.v("citation") * vr.poids_lettre("E")) < 1e-9


def test_le_signal_ecosystemes_compte_ceux_des_citants():
    lr = vr.charger()
    c = _c(editeurs=3, ecosystemes={"web", "rss"})
    e = [x for x in indice.elements(_ctx(CITS), c, lr) if x.nature == "ecosystemes"]
    assert len(e) == 1 and abs(e[0].log10 - lr.v("ecosysteme")) < 1e-9
    assert not [
        x
        for x in indice.elements(_ctx(CITS[:3]), _c(editeurs=2, ecosystemes={"web"}), lr)
        if x.nature == "ecosystemes"
    ]


def test_charger_remplit_les_ecosystemes_avec_ceux_des_citants():
    import inspect

    from grappes.classement import candidats

    src = inspect.getsource(candidats.charger)
    assert "st.ecosystems" not in src and "ecos_citants" in src


def test_lr_yaml_dit_que_ses_valeurs_ne_sont_pas_mesurees():
    from pathlib import Path

    assert "NON MESURÉES" in Path("config/lr.yaml").read_text(encoding="utf-8")
