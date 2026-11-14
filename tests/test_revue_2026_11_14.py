"""Non-régression des défauts corrigés à la relecture intégrale du 14/11/2026 (moteur). Aucun réseau."""

from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
import yaml

from grappes.autonomy import Autonomy, load_autonomy
from grappes.classement import fusion
from grappes.classement.candidats import Candidat, Contexte
from grappes.config import ConfigError, load_scoring
from grappes.fetch import PageFetcher
from grappes.fetch.robots import MAX_CRAWL_DELAY_S, RobotsCache
from grappes.ner.extraire import Nomme
from grappes.search.http import Response

PAGE = b"<html><head><title>Atelier</title>%s</head><body><p>Un atelier de quartier.</p></body></html>"


def transport_de(routes):
    """Faux transport : adresse -> (statut, en-têtes, corps). Garde la liste des adresses demandées."""
    vues = []

    def transport(method, url, headers, body, timeout, max_bytes):
        vues.append(url)
        statut, entetes, corps = routes.get(url, (404, {}, b""))
        return Response(statut, entetes, corps)

    transport.vues = vues
    return transport


def recuperateur(routes):
    t = transport_de(routes)
    return PageFetcher(Autonomy(), transport=t, sleep=lambda s: None, monotonic=lambda: 0.0, allow_private=True), t


# --- robots.txt ------------------------------------------------------------------------------------


def test_un_robots_txt_redirige_est_suivi_et_le_site_reste_visitable():
    """`exemple.test/robots.txt` renvoie vers `www.` : avant, tout le site passait pour interdit."""
    html = {"Content-Type": "text/html"}
    f, t = recuperateur({
        "https://atelier.test/robots.txt": (301, {"Location": "https://www.atelier.test/robots.txt"}, b""),
        "https://www.atelier.test/robots.txt": (200, {}, b"User-agent: *\nDisallow: /prive/\n"),
        "https://atelier.test/page": (200, html, PAGE % b""),
        "https://atelier.test/prive/x": (200, html, PAGE % b""),
    })  # fmt: skip
    assert f.fetch("https://atelier.test/page").ok
    interdit = f.fetch("https://atelier.test/prive/x")
    assert not interdit.ok and interdit.status == "robots"  # les règles lues après la redirection s'appliquent
    assert "https://atelier.test/prive/x" not in t.vues


def test_une_boucle_de_redirections_de_robots_txt_ne_tourne_pas_sans_fin():
    appels = []

    def fetch(url):
        appels.append(url)
        return 302, b"", url

    assert RobotsCache(fetch, "grappes-collecte/1").check("https://boucle.test/page") == (False, 0.0)
    assert len(appels) <= 6


def test_un_crawl_delay_demesure_ecarte_le_site_au_lieu_de_faire_dormir_le_cycle():
    regles = f"User-agent: *\nCrawl-delay: {int(MAX_CRAWL_DELAY_S) + 1}\n".encode()
    dormi = []
    t = transport_de({"https://lent.test/robots.txt": (200, {}, regles), "https://lent.test/page": (200, {"Content-Type": "text/html"}, PAGE % b"")})
    f = PageFetcher(Autonomy(), transport=t, sleep=dormi.append, monotonic=lambda: 0.0, allow_private=True)
    r = f.fetch("https://lent.test/page")
    assert not r.ok and r.status == "robots"
    assert "https://lent.test/page" not in t.vues and not dormi


# --- rel=canonical ---------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("canonique", "attendu"),
    [
        (b'<link rel="canonical" href="https://grand-journal.test/une">', "https://petit-site.test/billet"),  # autre éditeur : ignoré
        (b'<link rel="canonical" href="https://blog.petit-site.test/billet-propre">', "https://blog.petit-site.test/billet-propre"),  # même éditeur : cru
    ],
)
def test_une_page_ne_se_declare_pas_page_d_un_autre_editeur(canonique, attendu):
    f, _ = recuperateur({
        "https://petit-site.test/robots.txt": (404, {}, b""),
        "https://petit-site.test/billet": (200, {"Content-Type": "text/html"}, PAGE % canonique),
    })  # fmt: skip
    r = f.fetch("https://petit-site.test/billet")
    assert r.ok and r.record["canonical_url"] == attendu


# --- réglages vrai/faux ----------------------------------------------------------------------------


@pytest.mark.parametrize("texte", ["resultat: {inclure_personnes: non}", "resultat: {inclure_ambigus: oui}", "redact_persons: faux", "csv: {bom: non}"])
def test_un_vrai_faux_ecrit_en_toutes_lettres_est_refuse_dans_scoring(tmp_path, texte):
    """« inclure_personnes: non » était lu comme vrai : les noms de personnes sortaient en clair."""
    f = tmp_path / "scoring.yaml"
    f.write_text(texte, encoding="utf-8")
    with pytest.raises(ConfigError, match="true ou false"):
        load_scoring(f)


def test_les_vrais_booleens_de_scoring_passent(tmp_path):
    f = tmp_path / "scoring.yaml"
    f.write_text("resultat: {inclure_personnes: false, inclure_ambigus: true}\nredact_persons: true\n", encoding="utf-8")
    sc = load_scoring(f)
    assert sc.resultat_inclure_personnes is False and sc.resultat_inclure_ambigus is True and sc.redact_persons is True


@pytest.mark.parametrize("reglages", [{"apprentissage": {"actif": "non"}}, {"recalibrage": {"actif": "non"}}, {"apprentissage": {"exiger_racine_de_confiance": "non"}}, {"seuil_ingestion": {"valeur": 20, "auto_ajustable": "non"}}])
def test_un_vrai_faux_ecrit_en_toutes_lettres_est_refuse_dans_autonomie(tmp_path, reglages):
    (tmp_path / "autonomie.yaml").write_text(yaml.safe_dump(reglages), encoding="utf-8")
    with pytest.raises(ConfigError, match="true ou false"):
        load_autonomy(tmp_path)


# --- noms lus dans les textes ----------------------------------------------------------------------


def _contexte(candidats):
    return Contexte(cfg=None, db=SimpleNamespace(load_observations=list), rel=SimpleNamespace(factor=lambda ref: 1.0), grappe="g", candidats=candidats, citations=[], lues=set())


def _nomme(nom, categorie):
    return Nomme(nom.casefold(), nom, pages={"o1"}, sites={"journal.test"}, score_par_site={"journal.test": 0.99}, categorie=categorie)


def test_seules_les_organisations_lues_dans_un_texte_deviennent_candidates():
    """Depuis l'élargissement de l'extraction aux personnes et aux lieux, chaque nom de personne et chaque ville
    lus dans une page sortaient comme des acteurs du sujet."""
    nommes = {"a": _nomme("Atelier des Lilas", "ORG"), "b": _nomme("Camille Exemple", "PER"), "c": _nomme("Ville-Exemple", "LOC"), "d": _nomme("Cercle Ancien", "")}
    cands, _ = fusion.ajouter(_contexte([]), [], nommes)
    assert sorted(c.nom for c in cands) == ["Atelier des Lilas", "Cercle Ancien"]


def test_enrichir_une_copie_ne_modifie_pas_le_candidat_du_contexte():
    web = Candidat("web:atelier.test", "Atelier des Lilas", "Atelier des Lilas", 50.0, "classé", 50.0, 0.0, 0.0)
    ctx = _contexte([web])
    cands, _ = fusion.ajouter(ctx, ctx.candidats, {"a": _nomme("Atelier des Lilas", "ORG")})
    assert cands[0].ner_sites == {"journal.test": 0.99}
    assert web.ner_sites == {}  # une configuration « sans noms lus » calculée ensuite sur le même contexte reste propre


# --- recherche, découverte, registres --------------------------------------------------------------


def test_les_resultats_deja_recus_sont_gardes_quand_la_page_suivante_echoue(tmp_path, monkeypatch):
    from grappes.search import engine
    from grappes.search.base import SearchError, SearchProvider
    from grappes.search.config import ProviderSpec, SearchConfig
    from grappes.search.models import Candidate

    class DeuxPages(SearchProvider):
        type = "essai_deux_pages"

        def search(self, keyword, limit):
            yield Candidate("web", "premier.test", "https://premier.test", keyword, self.id, "page 1")
            raise SearchError("page 2 : HTTP 500")

    monkeypatch.setattr(engine, "get_provider_class", lambda kind: DeuxPages)
    cfg = SearchConfig(actifs=("p",), providers={"p": ProviderSpec("p", "essai_deux_pages", {})}, plugins_dir=tmp_path / "aucun", journal=tmp_path / "j.log")
    rep = engine.run_search(cfg, ["atelier"], execute=True)
    assert [c.ident for c in rep.raw] == ["premier.test"] and rep.status["p"].startswith("erreur")


def test_un_fichier_csv_injoignable_rend_la_source_muette():
    from grappes.decouverte.client import DecouverteError
    from grappes.decouverte.sources_yaml import Source, interroger

    class Panne:
        def get_text(self, url, encoding="utf-8-sig"):
            raise DecouverteError("réseau : TimeoutError")

    assert interroger(Source("jeu", "https://donnees.test/jeu.csv", format="csv"), "ateliers de quartier", Panne()) == []


def test_une_lecture_interrompue_d_un_registre_garde_l_ancien_cache(tmp_path):
    import json

    from grappes.registres import Registre, RegistresConfig, refresh_domaines
    from grappes.search.base import Journal
    from grappes.storage.db import Database

    db = Database(tmp_path / "g.db")
    with db.transaction() as c:
        c.executemany("INSERT INTO registre_domaines(registre, domaine, maj, ville) VALUES (?,?,?,?)", [("r", "ancien-a.test", "2020-01-01T00:00:00+00:00", ""), ("r", "ancien-b.test", "2020-01-01T00:00:00+00:00", "")])
    spec = Registre("r", "Registre", "domaines", "https://registre.test/api", items="resultats", champ_url="site", pagination={"param": "debut", "pas": 1, "max_pages": 3})
    pages = iter([Response(200, {}, json.dumps({"resultats": [{"site": "https://nouveau.test"}]}).encode()), Response(500, {}, b"")])
    refresh_domaines(db, spec, RegistresConfig((spec,)), datetime(2026, 11, 14, tzinfo=UTC), lambda *a: next(pages), Journal(None))
    assert {r["domaine"] for r in db.conn.execute("SELECT domaine FROM registre_domaines")} == {"ancien-a.test", "ancien-b.test"}
    db.close()


def test_un_libelle_sans_detail_wikidata_est_non_verifiable(tmp_path):
    juger = pytest.importorskip("grappes.autocal.juger")
    from grappes.autocal.reference import Reference

    w = SimpleNamespace(search=lambda nom, n: [{"id": "Q1", "label": nom}], api=lambda **kw: {"entities": {}}, sparql=lambda q: [])
    v = juger.Juge(Reference("s", "ateliers", "", [], ["Q9"]), w, tmp_path / "juge.json").juger("Atelier des Lilas", "ner:atelier des lilas")
    assert v.verdict == juger.NON_VERIFIABLE
