"""913/N4 : le niveau suit la réunion de deux fiches (et la séparation le rend). 913/N5 : le site de l'acteur reste une preuve affichée,
mais n'est pas un endroit indépendant, comme dans le moteur."""

from __future__ import annotations

from types import SimpleNamespace

from fastapi.testclient import TestClient

from pilote import rapprochements
from pilote.pont.faits import Provenance, endroits_comptes, niveau_de, preuves

from test_a7_numero import _app_avec, _etat, _p, _sans_splink  # noqa: F401  (fixture autouse réutilisée)


def _site_key(hote: str) -> str:
    return hote.lower().removeprefix("www.")


def _candidat(ref: str, citants: tuple[str, ...]) -> SimpleNamespace:
    return SimpleNamespace(ref=ref, registres=set(), citants=set(citants), ner_sites=set())


def test_le_site_de_l_acteur_n_est_pas_un_endroit_independant() -> None:
    ps = preuves(_candidat("web:zorbel.fr", ("web:site0.org",)), Provenance(), _site_key)
    assert {p["lieu"] for p in ps} == {"page:zorbel.fr", "page:site0.org"}  # la preuve reste affichée
    assert endroits_comptes(ps) == 1 and niveau_de(ps, endroits_comptes(ps)) == "a_verifier"


def test_deux_sites_exterieurs_font_un_acteur_sur() -> None:
    ps = preuves(_candidat("web:zorbel.fr", ("web:site0.org", "web:site1.org")), Provenance(), _site_key)
    assert endroits_comptes(ps) == 2 and niveau_de(ps, 2) == "sur"


def test_un_acteur_trouve_seulement_sur_son_site_compte_un_endroit() -> None:
    assert endroits_comptes(preuves(_candidat("web:zorbel.fr", ()), Provenance(), _site_key)) == 1


def test_un_nom_qui_n_est_pas_un_site_compte_toutes_ses_pages() -> None:
    ps = preuves(_candidat("nom:club des vents", ("web:site0.org", "web:site1.org")), Provenance(), _site_key)
    assert endroits_comptes(ps) == 2


def test_la_reunion_rend_sure_une_fiche_trouvee_a_deux_endroits_et_la_separation_le_defait(cfg):
    fiches = [{"nom": "A", "numero_officiel": "412345678", "faits": {"preuves": [_p("page:a.example")], "niveau": "a_verifier"}},
              {"nom": "B", "numero_officiel": "412345678", "faits": {"preuves": [_p("page:b.example")], "niveau": "a_verifier"}}]  # fmt: skip
    app, rid = _app_avec(cfg, fiches)
    with TestClient(app):
        rapprochements.proposer(cfg, app.state.fabrique, rid)
        cands, [r] = _etat(app, rid)
        assert {c.faits["niveau"] for c in cands.values()} == {"sur"} and {c.nb_endroits for c in cands.values()} == {2}
        rapprochements.trancher(cfg, app.state.fabrique, r.id, "separe", "t")
        cands, _ = _etat(app, rid)
        assert {c.faits["niveau"] for c in cands.values()} == {"a_verifier"} and "niveau_seul" not in cands["A"].faits


def test_une_fiche_sure_rend_sure_la_fiche_reunie(cfg):
    fiches = [{"nom": "A", "numero_officiel": "412345678", "faits": {"preuves": [_p("page:a.example")], "niveau": "sur"}},
              {"nom": "B", "numero_officiel": "412345678", "faits": {"preuves": [_p("page:a.example")], "niveau": "a_verifier"}}]  # fmt: skip
    app, rid = _app_avec(cfg, fiches)
    with TestClient(app):
        rapprochements.proposer(cfg, app.state.fabrique, rid)
        cands, _ = _etat(app, rid)
        assert cands["B"].faits["niveau"] == "sur" and cands["B"].nb_endroits == 1


def test_une_fiche_sans_niveau_n_en_recoit_pas(cfg):
    fiches = [{"nom": "A", "numero_officiel": "412345678", "faits": {"preuves": [_p("page:a.example")]}},
              {"nom": "B", "numero_officiel": "412345678", "faits": {"preuves": [_p("page:b.example")]}}]  # fmt: skip
    app, rid = _app_avec(cfg, fiches)
    with TestClient(app):
        rapprochements.proposer(cfg, app.state.fabrique, rid)
        cands, _ = _etat(app, rid)
        assert all("niveau" not in c.faits for c in cands.values())
