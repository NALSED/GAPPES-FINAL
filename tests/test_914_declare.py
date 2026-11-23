"""914/A : ce qu'une page déclare d'elle-même. Thèmes inventés, numéros synthétiques à clé de Luhn calculée."""

from __future__ import annotations

import json

from grappes.fetch.declare import luhn, numero_valide, numeros_du_texte, relever
from grappes.ingestion.web import WebFetcher
from grappes.storage.db import Database


def _cle(debut: str) -> str:
    """Complète `debut` d'un chiffre de contrôle de Luhn."""
    return next(debut + str(k) for k in range(10) if luhn(debut + str(k)))


SIREN = _cle("40000001")
AUTRE = _cle("40000002")
SIRET = _cle(SIREN + "0001")
FAUX = SIREN[:-1] + str((int(SIREN[-1]) + 1) % 10)


def _page(jsonld: dict | None = None, corps: str = "") -> bytes:
    tete = f'<script type="application/ld+json">{json.dumps(jsonld)}</script>' if jsonld else ""
    return f"<html><head>{tete}</head><body>{corps}</body></html>".encode()


def test_cle_de_controle():
    assert numero_valide(SIREN) == "siren"
    assert numero_valide(SIRET) == "siret"
    assert numero_valide(FAUX) == ""
    assert numero_valide("356000000" + "00047") == "siret"  # La Poste : somme des chiffres multiple de 5


def test_numero_annonce_dans_le_texte():
    t = f"Mentions légales. Association des Cerfs-Volants Bleus, SIREN {SIREN[:3]} {SIREN[3:6]} {SIREN[6:]}."
    assert numeros_du_texte(t) == [("siren", SIREN)]


def test_numero_sans_mot_annonciateur_ignore():
    assert numeros_du_texte(f"Appelez le {SIREN} pour réserver.") == []


def test_cle_fausse_jetee():
    assert numeros_du_texte(f"SIRET : {FAUX}00012") == []
    assert relever(_page(corps=f"SIREN {FAUX}"), f"SIREN {FAUX}", "https://cerfs-volants.example") == {}


def test_hebergeur_ecarte():
    t = f"Éditeur : Club des Cerfs-Volants, SIREN {SIREN}. Hébergé par Nuage SAS, RCS Ville B {AUTRE}."
    assert numeros_du_texte(t) == [("siren", SIREN)]


def test_rna_et_tva():
    assert numeros_du_texte("Association déclarée, RNA W123456789.") == [("rna", "W123456789")]
    assert numeros_du_texte(f"TVA intracommunautaire : FR12 {SIREN}") == [("siren", SIREN)]


def test_schema_org():
    org = {"@context": "https://schema.org", "@type": "SportsOrganization", "name": "Les Cerfs-Volants Bleus", "taxID": SIREN,
           "url": "https://www.cerfs-volants.example/", "telephone": "01 02 03 04 05",
           "address": {"@type": "PostalAddress", "addressLocality": "Villebrume", "postalCode": "99001"}, "sameAs": ["https://reseau.example/cerfs"]}
    d = relever(_page(org), "", "https://cerfs-volants.example/contact")
    assert d == {"numero": SIREN, "type_numero": "siren", "methode": "schema.org", "nom": "Les Cerfs-Volants Bleus", "ville": "Villebrume",
                 "code_postal": "99001", "telephone": "01 02 03 04 05", "comptes": ["https://reseau.example/cerfs"]}


def test_organisation_d_un_autre_site_ignoree():
    org = {"@context": "https://schema.org", "@type": "Organization", "name": "Fédération des Cerfs-Volants", "taxID": AUTRE, "url": "https://federation.example"}
    assert relever(_page(org), "", "https://cerfs-volants.example") == {}


def test_deux_numeros_differents_rien():
    t = f"SIREN {SIREN}. Partenaire : SIREN {AUTRE}."
    assert "numero" not in relever(_page(corps=t), t, "https://cerfs-volants.example")


def test_siren_et_siret_du_meme_siren():
    t = f"SIREN {SIREN}, SIRET {SIRET}"
    d = relever(_page(corps=t), t, "https://cerfs-volants.example")
    assert (d["numero"], d["type_numero"], d["methode"]) == (SIRET, "siret", "texte")


def test_page_mal_formee_ne_plante_pas():
    assert relever(b"<html><script type='application/ld+json'>{pas du json</script>", "", "https://x.example") == {}


def test_garde_en_base(tmp_path):
    rec = {"url": "https://cerfs-volants.example/", "title": "Accueil", "text": "Bienvenue", "declare": {"numero": SIREN, "type_numero": "siren", "methode": "texte"}}
    obs = list(WebFetcher().parse(rec))
    db = Database(tmp_path / "g.db")
    db.add_observations(obs, {})
    (o,) = db.load_observations()
    assert json.loads(o.meta["declare"])["numero"] == SIREN
