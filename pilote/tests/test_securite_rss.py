"""Q-SECU : l'ajout d'un flux RSS refuse les adresses d'identifiants des hébergeurs, comme l'ajout d'une API."""

from __future__ import annotations

import pytest

from pilote import flux_rss
from pilote.refus import ConfigRefusee


@pytest.mark.parametrize("url", ["http://169.254.169.254/latest/meta-data/", "http://[fd00:ec2::254]/flux.xml"])
def test_adresse_metadonnees_refusee(url: str) -> None:
    with pytest.raises(ConfigRefusee, match="Adresse refusée"):
        flux_rss.verifier_adresse(url)


@pytest.mark.parametrize("url", ["https://exemple.org/flux.xml", "http://127.0.0.1:1200/rsshub/route", "http://192.168.0.60/flux.xml"])
def test_adresse_ordinaire_acceptee(url: str) -> None:
    # le réseau local reste autorisé exprès (RSSHub sur la machine) : seul le service d'identifiants est refusé
    assert flux_rss.verifier_adresse(url) == url


def test_schema_toujours_controle() -> None:
    with pytest.raises(ConfigRefusee, match="http"):
        flux_rss.verifier_adresse("file:///etc/passwd")
