"""Scrapling (spec 906) : scraping auto-hébergé, gratuit, licence BSD-3 — famille prestataire de collecte, sans
clé ni coût. Dépendance optionnelle (`pilote[scrapling]`) : les tests se sautent si elle est absente."""

from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import ClassVar

import pytest

from pilote.adaptateurs import Client, ErreurSource, charger

scrapling = pytest.importorskip("scrapling")

PAGE = """<!doctype html><html><head><title>Club Nautique Imaginaire</title>
<meta name="description" content="Club de voile et d'aviron à Port-Exemple."></head><body>
<ul>
<li class="club"><h3><a href="/clubs/1">Club Nautique Imaginaire</a></h3><span class="ville">Port-Exemple</span></li>
<li class="club"><h3><a href="/clubs/2">Club Nautique du Lac</a></h3><span class="ville">Lac-Exemple</span></li>
<li class="club"><h3><a href="/sans-lien"></a></h3></li>
</ul>
</body></html>"""


class FauxSite(BaseHTTPRequestHandler):
    chemins: ClassVar[list] = []

    def do_GET(self):
        FauxSite.chemins.append(self.path)
        self.send_response(404 if self.path.startswith("/404") else 200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(PAGE.encode("utf-8"))

    def log_message(self, *a):
        pass


@pytest.fixture
def site():
    s = HTTPServer(("127.0.0.1", 0), FauxSite)
    FauxSite.chemins = []
    threading.Thread(target=s.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{s.server_port}"
    s.shutdown()


PARAMETRES = {"liste": "li.club", "champs": {"nom": "h3 a::text", "site": "h3 a::attr(href)", "ville": "span.ville::text"}, "genre": "club", "origine_texte": "Site d'essai (Scrapling)"}


def test_scrapling_rend_les_noms_d_une_page_html_par_selecteur_css(site):
    noms = charger("scrapling").chercher({"quoi": "nautique"}, Client("scrapling"), {**PARAMETRES, "url": site + "/recherche"})
    assert noms == [
        {"nom": "Club Nautique Imaginaire", "origine": "Site d'essai (Scrapling)", "site": "/clubs/1", "ville": "Port-Exemple", "genre": "club"},
        {"nom": "Club Nautique du Lac", "origine": "Site d'essai (Scrapling)", "site": "/clubs/2", "ville": "Lac-Exemple", "genre": "club"},
    ]


def test_scrapling_encode_les_mots_cherches_jamais_colles_dans_le_texte(site):
    # un mot avec une espace et un « & » ne doit jamais casser l'adresse ni s'y coller tel quel (toujours par `params`, encodé)
    charger("scrapling").chercher({"quoi": "clubs & associations"}, Client("scrapling"), {**PARAMETRES, "url": site + "/recherche", "params": {"q": "{quoi}"}})
    assert FauxSite.chemins[-1] == "/recherche?q=clubs+%26+associations"


def test_scrapling_ecarte_un_resultat_sans_nom(site):
    # le 3e <li> n'a pas de texte dans son lien : écarté, pas un nom vide
    noms = charger("scrapling").chercher({"quoi": "nautique"}, Client("scrapling"), {**PARAMETRES, "url": site + "/recherche"})
    assert len(noms) == 2


def test_scrapling_refuse_sans_adresse_ni_selecteurs(site):
    with pytest.raises(ErreurSource, match="adresse"):
        charger("scrapling").chercher({"quoi": "x"}, Client("scrapling"), {**PARAMETRES, "url": ""})
    with pytest.raises(ErreurSource, match="sélecteur CSS d'un résultat"):
        charger("scrapling").chercher({"quoi": "x"}, Client("scrapling"), {**PARAMETRES, "url": site, "liste": ""})
    with pytest.raises(ErreurSource, match="sélecteur CSS contient le nom"):
        charger("scrapling").chercher({"quoi": "x"}, Client("scrapling"), {**PARAMETRES, "url": site, "champs": {"site": "a::attr(href)"}})


def test_scrapling_dit_clairement_une_page_en_erreur(site):
    with pytest.raises(ErreurSource, match="404"):
        charger("scrapling").chercher({"quoi": "x"}, Client("scrapling"), {**PARAMETRES, "url": site + "/404", "liste": "introuvable"})  # fmt: skip


def test_scrapling_prefixe_un_site_relatif(site):
    noms = charger("scrapling").chercher({"quoi": "nautique"}, Client("scrapling"), {**PARAMETRES, "url": site + "/recherche", "site_prefixe": site})
    assert [n["site"] for n in noms] == [site + "/clubs/1", site + "/clubs/2"]


def test_scrapling_lit_un_exemple_enregistre_comme_le_niveau_2_de_la_fiche_11():
    # fiche 11, niveau 2 : l'exemple enregistré est du texte brut (HTML), pas du JSON — `convertir` doit le lire pareil,
    # sans appel réseau (LIT_PARAMETRES = True, exactement le même chemin que `tests_source._lire_par_adaptateur`)
    m = charger("scrapling")
    assert m.LIT_PARAMETRES is True
    noms = m.convertir(PAGE, parametres=PARAMETRES)
    assert [n["nom"] for n in noms] == ["Club Nautique Imaginaire", "Club Nautique du Lac"]


# 5.2 c (retour du 08/11/2026) : la tuile ENRICHIR — pas une recherche, la propre page d'un candidat.
PARAMETRES_SITE = {"lire_site": True, "champs": {"nom": "title::text", "detail": 'meta[name="description"]::attr(content)'}}


def test_scrapling_lire_site_lit_la_propre_page_du_candidat(site):
    noms = charger("scrapling").chercher({"site": site + "/recherche"}, Client("scrapling"), PARAMETRES_SITE)
    assert noms == [{"nom": "Club Nautique Imaginaire", "detail": "Club de voile et d'aviron à Port-Exemple.", "origine": "Scrapling (scraping auto-hébergé)"}]


def test_scrapling_lire_site_sans_site_ne_fait_pas_echouer_la_verification(site):
    assert charger("scrapling").chercher({}, Client("scrapling"), PARAMETRES_SITE) == []


def test_scrapling_lire_site_page_en_erreur_ne_fait_pas_echouer_la_verification(site):
    assert charger("scrapling").chercher({"site": site + "/404"}, Client("scrapling"), PARAMETRES_SITE) == []


def test_scrapling_lire_site_offline_meme_chemin_que_niveau_2():
    assert charger("scrapling").convertir(PAGE, parametres=PARAMETRES_SITE) == [
        {"nom": "Club Nautique Imaginaire", "detail": "Club de voile et d'aviron à Port-Exemple.", "origine": "Scrapling (scraping auto-hébergé)"}
    ]


def test_scrapling_navigateur_appelle_le_fetcher_furtif(monkeypatch):
    # 5.2 a : le mode navigateur furtif choisit StealthyFetcher plutôt que Fetcher — vérifié sans lancer de vrai
    # navigateur (même principe que `suite_ia` : on ne mocke pas pour écarter le test, on isole l'appel externe).
    from scrapling import fetchers as sf

    class FauxReponse:
        status = 200

        def css(self, _sel):
            return []

    vus = []

    def faux_fetch(url, **kw):
        vus.append((url, kw))
        return FauxReponse()

    monkeypatch.setattr(sf.StealthyFetcher, "fetch", staticmethod(faux_fetch))
    charger("scrapling").chercher({"site": "https://exemple.invalid/club"}, Client("scrapling"), {**PARAMETRES_SITE, "navigateur": True})
    assert vus and vus[0][0] == "https://exemple.invalid/club" and vus[0][1]["headless"] is True
