"""913/N1 : un site ne se confirme pas par son propre flux RSS ni par un de ses sous-domaines."""

from __future__ import annotations

from grappes.classement.candidats import citants_par_cite
from grappes.ecosystem.crossref import CrossRefRule, build_citations, validate_crossref
from grappes.models import Observation, SourceRef


def _obs(i: str, eco: str, ident: str, lien: str) -> Observation:
    return Observation(i, SourceRef(eco, ident), None, "texte", links=(lien,))


EXTERIEURS = [_obs(str(i), "web", f"site{i}.org", "https://zorbel.fr/") for i in range(2)]


def test_le_flux_du_site_ne_cite_pas_son_site() -> None:
    cits = build_citations([_obs("f", "rss", "zorbel.fr", "https://zorbel.fr/actu/1")])
    assert cits == []


def test_un_sous_domaine_ne_cite_pas_son_site() -> None:
    cits = build_citations([_obs("b", "web", "blog.zorbel.fr", "https://www.zorbel.fr/")])
    assert cits == []


def test_le_flux_ne_fait_pas_passer_le_site_confirme() -> None:
    sans = validate_crossref(build_citations(EXTERIEURS), "g", lambda x: True, lambda x: 1.0, CrossRefRule())["web:zorbel.fr"]
    avec = validate_crossref(
        build_citations([*EXTERIEURS, _obs("f", "rss", "zorbel.fr", "https://zorbel.fr/actu/1")]), "g", lambda x: True, lambda x: 1.0, CrossRefRule()
    )["web:zorbel.fr"]
    assert sans.validated is False
    assert (avec.ecosystems, avec.validated) == (sans.ecosystems, sans.validated)


def test_le_recoupement_ignore_une_citation_du_meme_editeur_meme_fournie_a_la_main() -> None:
    from grappes.ecosystem.crossref import Citation

    cits = [Citation(f"web:site{i}.org", "web:zorbel.fr", "web", str(i), None) for i in range(2)]
    cits.append(Citation("rss:zorbel.fr", "web:zorbel.fr", "rss", "f", None))
    v = validate_crossref(cits, "g", lambda x: True, lambda x: 1.0, CrossRefRule())["web:zorbel.fr"]
    assert "rss:zorbel.fr" not in v.citers and v.ecosystems == ("web",)


def test_le_compte_d_editeurs_de_a3_n_inclut_pas_le_site_lui_meme() -> None:
    cits = build_citations([*EXTERIEURS, _obs("f", "rss", "zorbel.fr", "https://zorbel.fr/actu/1")])
    assert set(citants_par_cite([(c.citer, c.cited) for c in cits])["web:zorbel.fr"]) == {"site0.org", "site1.org"}


def test_deux_sites_differents_se_citent_toujours() -> None:
    cits = build_citations([_obs("a", "rss", "autre.fr", "https://zorbel.fr/")])
    assert [(c.citer, c.cited) for c in cits] == [("rss:autre.fr", "web:zorbel.fr")]


def test_deux_sites_heberges_cote_a_cote_se_citent_toujours() -> None:
    cits = build_citations([_obs("a", "web", "monclub.wordpress.com", "https://autreclub.wordpress.com/")])
    assert [(c.citer, c.cited) for c in cits] == [("web:monclub.wordpress.com", "web:autreclub.wordpress.com")]
