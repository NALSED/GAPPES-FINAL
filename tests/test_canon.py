from grappes.canon import canonical_domain, canonical_handle, canonical_url


def test_handle():
    assert canonical_handle("@Foo_Bar") == "foo_bar"
    assert canonical_handle("  FOO ") == "foo"


def test_domain():
    assert canonical_domain("WWW.Exemple.TEST") == "exemple.test"
    assert canonical_domain("https://www.exemple.test:8080/a/b") == "exemple.test"
    assert canonical_domain("exemple.test/chemin") == "exemple.test"


def test_url_nettoyage():
    u = "HTTPS://WWW.Exemple.test/Soupe/?utm_source=x&fbclid=1&id=3#frag"
    assert canonical_url(u) == "https://exemple.test/Soupe?id=3"


def test_url_slash_final_et_racine():
    assert canonical_url("https://exemple.test/") == "https://exemple.test"
    assert canonical_url("https://exemple.test/a/b/") == "https://exemple.test/a/b"


def test_url_sans_schema():
    assert canonical_url("www.exemple.test/a") == "https://exemple.test/a"


def test_url_vide_et_idempotence():
    assert canonical_url("  ") == ""
    u = canonical_url("https://www.exemple.test/a/?utm_x=1&b=2")
    assert canonical_url(u) == u
