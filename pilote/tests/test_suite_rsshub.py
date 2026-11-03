"""RSSHub (3.8.10) : la résolution d'une adresse de site en adresse de flux, contre une fausse instance locale —
aucune vraie instance RSSHub n'est accessible dans ce bac à sable (voir le docstring de suite_rsshub.py)."""

from __future__ import annotations

import http.server
import threading

import pytest

from pilote import suite_rsshub as sr


def test_route_pour_prend_le_domaine_avec_ou_sans_schema():
    assert sr.route_pour("https://exemple.fr/page") == "/site/exemple.fr"
    assert sr.route_pour("exemple.fr") == "/site/exemple.fr"


def test_resoudre_rend_l_adresse_quand_l_instance_repond():
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        url = sr.resoudre(f"http://127.0.0.1:{srv.server_port}", "exemple.fr")
        assert url == f"http://127.0.0.1:{srv.server_port}/site/exemple.fr"
    finally:
        srv.shutdown()


def test_resoudre_leve_erreur_claire_sur_404():
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(404)
            self.end_headers()

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        with pytest.raises(ValueError, match="ne connaît pas de route"):
            sr.resoudre(f"http://127.0.0.1:{srv.server_port}", "exemple.fr")
    finally:
        srv.shutdown()


def test_resoudre_leve_erreur_claire_sans_instance():
    with pytest.raises(OSError, match="ne répond pas"):
        sr.resoudre("http://127.0.0.1:1", "exemple.fr")
