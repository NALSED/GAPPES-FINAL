"""RSSHub (3.8.10) : de l'adresse d'un site à l'adresse de son flux, par les règles Radar de l'instance (le contrat
vérifié contre une vraie instance le 03/11/2026), contre une fausse instance locale — aucun appel réseau ici."""

from __future__ import annotations

import http.server
import json
import threading

import pytest

from pilote import suite_rsshub as sr

REGLES = {
    "exemple.fr": {
        "_name": "Exemple",
        ".": [
            {"title": "Rubrique", "source": ["/:rubrique"], "target": "/exemple/:rubrique"},
            {"title": "Tout", "source": ["/"], "target": "/exemple/tout"},
            {"title": "Article", "source": ["/:rubrique/:id?"], "target": "/exemple/:rubrique/:id?"},
            {"title": "Requête", "source": ["/cherche?q=:q"], "target": "/exemple/q/:q"},
        ],
    },
    "vide.fr": {"_name": "Vide", ".": [{"title": "Rien", "source": ["/"], "target": "/vide/tout"}]},
}
FLUX = b'<?xml version="1.0"?><rss version="2.0"><channel><title>x</title><item><title>Un article</title><link>https://exemple.fr/a</link></item></channel></rss>'
VIDE = b'<?xml version="1.0"?><rss version="2.0"><channel><title>x</title></channel></rss>'


def test_routes_suivent_les_regles_radar():
    # « Rubrique » et « Article » (paramètre facultatif absent) mènent à la même route : rendue une seule fois ;
    # le motif avec requête (« /cherche?q=:q ») n'est pas pris en charge, jamais une fausse correspondance
    assert sr.routes(REGLES, "https://www.exemple.fr/politique") == [{"titre": "Rubrique", "route": "/exemple/politique"}]
    assert sr.routes(REGLES, "exemple.fr") == [{"titre": "Tout", "route": "/exemple/tout"}]
    assert sr.routes(REGLES, "https://exemple.fr/politique/42") == [{"titre": "Article", "route": "/exemple/politique/42"}]
    assert sr.routes(REGLES, "https://inconnu.fr/x") == []  # domaine que RSSHub ne couvre pas


@pytest.fixture
def instance():
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            corps = {"/api/radar/rules": json.dumps(REGLES).encode(), "/exemple/tout": FLUX, "/vide/tout": VIDE}.get(self.path)
            self.send_response(200 if corps else 404)
            self.end_headers()
            self.wfile.write(corps or b"")

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_port}"
    srv.shutdown()


def test_resoudre_rend_le_flux_lu_une_fois(instance):
    lu = sr.resoudre(instance, "https://www.exemple.fr/")
    assert lu == {"url": f"{instance}/exemple/tout", "titre": "Tout", "articles": 1, "format": "rss"}


def test_site_non_couvert_le_dit_clairement(instance):
    with pytest.raises(ValueError, match="ne connaît pas de route"):
        sr.resoudre(instance, "https://inconnu.fr/")


def test_route_sans_article_le_dit_clairement(instance):
    with pytest.raises(ValueError, match="aucune de ses routes n'a rendu d'article"):
        sr.resoudre(instance, "https://vide.fr/")


def test_instance_absente_le_dit_clairement():
    with pytest.raises(OSError, match="ne répond pas"):
        sr.resoudre("http://127.0.0.1:1", "exemple.fr")


def test_la_prise_rsshub_se_nomme_d_apres_le_site():
    """Le flux RSSHub a pour adresse celle de l'instance (127.0.0.1) : la prise et son nom viennent du SITE."""
    ident = sr.identifiant("https://www.exemple.fr/politique")
    assert ident.startswith("rsshub-www-exemple-fr-") and sr.nom_prise(ident) == "RSSHub (www.exemple.fr)"
    assert sr.nom_prise("rss-exemple-fr-123456") is None


def test_tri_et_export_disent_le_nom_des_flux_jamais_l_identifiant(cfg):
    """Revue 902 : un flux ajouté à la main s'affichait « rss-… » dans Tri et à l'export ; une prise RSSHub aussi."""
    from pilote import flux_rss, tri

    f = flux_rss.ajouter(cfg, "https://www.exemple.fr/flux.xml", nom="Exemple Actu", verifier=False)
    nom = tri.noms_de_sources(cfg)
    assert nom(f["id"]) == "Exemple Actu"
    assert nom(sr.identifiant("https://www.exemple.fr/politique")) == "RSSHub (www.exemple.fr)"


def test_lancer_avec_seulement_une_tuile_rsshub(cfg, monkeypatch, tmp_path):
    """Le flux est trouvé au lancement ; une recherche dont RSSHub est la seule entrée part ; un site non couvert est dit."""
    from conftest import copier_config
    from fastapi.testclient import TestClient

    from pilote.app import creer_app
    from pilote.config import charger

    cfg2 = charger(copier_config(tmp_path / "r", suite={"rsshub_url": "http://rsshub.test"}))
    monkeypatch.setattr(sr, "resoudre", lambda url, site: (_ for _ in ()).throw(ValueError(f"RSSHub ne connaît pas de route pour « {site} ».")) if "inconnu" in site
                        else {"url": f"{url}/exemple/tout", "titre": "Tout", "articles": 3, "format": "rss"})  # fmt: skip
    n = lambda i, nom, role, ref=None, opts=None: {"id": i, "nom": nom, "role": role, "ref": ref, "x": 0, "y": 0, "opts": opts or []}

    def plan(site):
        return {"nodes": [n("saisie", "Ta saisie", "ENTREE"), n("grappes", "Grappes", "GRAPPES"), n("r", "RSSHub", "OUTIL", "rsshub", [["Site à transformer", site]])],
                "edges": [{"from": "saisie", "to": "r"}, {"from": "r", "to": "grappes"}]}  # fmt: skip

    with TestClient(creer_app(cfg2)) as c:
        assert c.post("/api/suite/outils/rsshub/allumer", json={"avertissement_lu": True}).status_code == 200
        r = c.post("/api/suite/lancer", json={"saisie": "x", "mode": "Avancée", "plan": plan("https://www.exemple.fr/"), "pays": "FR"})
        assert r.status_code == 202, r.text
        assert "3 articles" in r.json()["appliques"][0]["texte"] and r.json()["non_appliques"] == []
        r = c.post("/api/suite/lancer", json={"saisie": "x", "mode": "Avancée", "plan": plan("https://inconnu.fr/"), "pays": "FR"})
        assert r.status_code == 422 and "ne connaît pas de route" in r.text  # rien ne peut chercher : refusé, avec la raison de la tuile


def test_le_flux_rsshub_devient_une_prise_comme_un_flux_ajoute_a_la_main(cfg, tmp_path):
    from pilote import moteur_sources

    cible = tmp_path / "copie"
    (cible / "recherche").mkdir(parents=True)
    (cible / "recherche.yaml").write_text("actifs: []\n", encoding="utf-8")
    plan = {"rsshub": [{"tuile": "r", "nom": "RSSHub", "site": "https://www.exemple.fr/", "flux": "http://127.0.0.1:1200/exemple/tout", "format": "rss"}]}
    moteur_sources.materialiser(cfg, cible, {"sources": [], "plan": plan})
    ident = sr.identifiant("https://www.exemple.fr/")
    definition = (cible / "recherche" / f"{ident}.yaml").read_text(encoding="utf-8")
    assert "http://127.0.0.1:1200/exemple/tout" in definition and ident in (cible / "recherche.yaml").read_text(encoding="utf-8")
