"""Scrapling (spec 906) : scraping auto-hébergé, gratuit, licence BSD-3 — famille prestataire de collecte, sans
clé ni coût. Dépendance optionnelle (`pilote[scrapling]`) : les tests se sautent si elle est absente."""

from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import ClassVar

import pytest

from pilote.adaptateurs import Client, ErreurSource, charger

scrapling = pytest.importorskip("scrapling")

PAGE = """<!doctype html><html><body>
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
    noms = charger("scrapling").chercher({"quoi": "nautique"}, Client("scrapling"), {**PARAMETRES, "url": site + "/recherche?q={quoi}"})
    assert noms == [
        {"nom": "Club Nautique Imaginaire", "origine": "Site d'essai (Scrapling)", "site": "/clubs/1", "ville": "Port-Exemple", "genre": "club"},
        {"nom": "Club Nautique du Lac", "origine": "Site d'essai (Scrapling)", "site": "/clubs/2", "ville": "Lac-Exemple", "genre": "club"},
    ]
    assert FauxSite.chemins[-1] == "/recherche?q=nautique"  # {quoi} rempli dans l'adresse, comme api_json


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


def test_scrapling_lit_un_exemple_enregistre_comme_le_niveau_2_de_la_fiche_11():
    # fiche 11, niveau 2 : l'exemple enregistré est du texte brut (HTML), pas du JSON — `convertir` doit le lire pareil,
    # sans appel réseau (LIT_PARAMETRES = True, exactement le même chemin que `tests_source._lire_par_adaptateur`)
    m = charger("scrapling")
    assert m.LIT_PARAMETRES is True
    noms = m.convertir(PAGE, parametres=PARAMETRES)
    assert [n["nom"] for n in noms] == ["Club Nautique Imaginaire", "Club Nautique du Lac"]
