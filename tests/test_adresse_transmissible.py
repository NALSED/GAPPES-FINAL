"""Une adresse avec des accents se transmet (revue 902 : trois pages d'un média perdues sur UnicodeEncodeError au
cycle réel). Le serveur est local (boucle locale), aucune requête réelle."""

import http.server
import threading

from grappes.search.http import adresse_transmissible, urllib_transport


def test_accents_encodes_le_reste_intact():
    assert adresse_transmissible("https://exemple.test/a/b?c=1") == "https://exemple.test/a/b?c=1"
    assert (
        adresse_transmissible("https://exemple.test/fr/perturbations-routières/42?q=enquête#é")
        == "https://exemple.test/fr/perturbations-routi%C3%A8res/42?q=enqu%C3%AAte#%C3%A9"
    )
    assert adresse_transmissible("https://exemple.test/d%C3%A9j%C3%A0/é") == "https://exemple.test/d%C3%A9j%C3%A0/%C3%A9"
    assert adresse_transmissible("https://café.test:8080/x").startswith("https://xn--caf-dma.test:8080/")


def test_une_page_a_accents_est_vraiment_demandee():
    vus = []

    class Gestion(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            vus.append(self.path)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *a):
            pass

    serveur = http.server.HTTPServer(("127.0.0.1", 0), Gestion)
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    try:
        r = urllib_transport("GET", f"http://127.0.0.1:{serveur.server_port}/fr/enquête-relève", {}, None, 5.0, 1000)
    finally:
        serveur.shutdown()
    assert r.status == 200 and vus == ["/fr/enqu%C3%AAte-rel%C3%A8ve"]
