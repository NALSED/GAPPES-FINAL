"""A2 (spec 912) : une confirmation exige le nom ET un second champ concordant ; le nom seul est « meme_nom », sans effet."""

from __future__ import annotations

from pilote import adaptateurs
from pilote.pont.verification import fiabilite_effective, verifier_candidats

SPEC = {"verificateurs": [{"source": "registre-test", "module": "registre-test", "verifie_sur": "nom"}], "mains_sources": {"registre-test": "premiere"}, "fiabilites_sources": {"registre-test": "A"}}


def _verifier(monkeypatch, lignes, rendus):
    class Faux:
        @staticmethod
        def chercher(entree, client, parametres):
            return [dict(r) for r in rendus.get(entree["nom"], [])]

    monkeypatch.setattr(adaptateurs, "charger", lambda nom: Faux)
    verifier_candidats(lignes, SPEC, {}, lambda: False, 60.0, lambda *a, **k: None)
    fiabilite_effective(lignes, SPEC)
    return lignes


def test_le_nom_seul_n_est_pas_une_confirmation_et_ne_releve_pas_la_fiabilite(monkeypatch):
    lignes = _verifier(monkeypatch, [{"nom": "Atelier du Phare", "ville": "", "site": ""}], {"Atelier du Phare": [{"nom": "Atelier du Phare", "origine": "Registre"}]})
    v = lignes[0]["faits"]["verifications"][0]
    assert v["signal"] == "meme_nom" and v["champs"] == {"ville": "absence", "numero": "absence", "site": "absence"}
    assert "fiabilite_effective" not in lignes[0]["faits"]


def test_un_second_champ_concordant_fait_la_confirmation(monkeypatch):
    rendus = {
        "Par ville": [{"nom": "Par ville", "ville": "  LORIENT ", "origine": "Registre"}],
        "Par numéro": [{"nom": "Par numéro", "numero": "412 345 678", "origine": "Registre"}],
        "Par site": [{"nom": "Par site", "site": "https://www.Phare.example/accueil", "origine": "Registre"}],
    }
    lignes = _verifier(monkeypatch, [{"nom": "Par ville", "ville": "Lorient"}, {"nom": "Par numéro", "numero_officiel": "412345678"}, {"nom": "Par site", "site": "phare.example"}], rendus)
    for ligne in lignes:
        assert ligne["faits"]["verifications"][0]["signal"] == "confirmation", ligne["nom"]
        assert ligne["faits"]["fiabilite_effective"] == "A"


def test_un_homonyme_d_une_autre_ville_est_un_desaccord_affiche_sans_effet(monkeypatch):
    lignes = _verifier(monkeypatch, [{"nom": "Atelier du Phare", "ville": "Lorient"}], {"Atelier du Phare": [{"nom": "Atelier du Phare", "ville": "Colmar", "origine": "Registre"}]})
    v = lignes[0]["faits"]["verifications"][0]
    assert v["signal"] == "meme_nom" and v["champs"]["ville"] == "desaccord"
    assert "fiabilite_effective" not in lignes[0]["faits"]


def test_parmi_plusieurs_homonymes_celui_qui_concorde_est_retenu(monkeypatch):
    rendus = {"Atelier du Phare": [{"nom": "Atelier du Phare", "ville": "Colmar", "origine": "fiche 1"}, {"nom": "Atelier du Phare", "ville": "Lorient", "origine": "fiche 2"}]}
    v = _verifier(monkeypatch, [{"nom": "Atelier du Phare", "ville": "Lorient"}], rendus)[0]["faits"]["verifications"][0]
    assert v["signal"] == "confirmation" and v["origine"] == "fiche 2"


def test_une_adresse_de_preuve_n_est_pas_un_numero_officiel(monkeypatch):
    rendus = {"Atelier du Phare": [{"nom": "Atelier du Phare", "numero": "https://registre.example/fiche/12", "origine": "Registre"}]}
    v = _verifier(monkeypatch, [{"nom": "Atelier du Phare", "numero_officiel": "412345678"}], rendus)[0]["faits"]["verifications"][0]
    assert v["signal"] == "meme_nom" and v["champs"]["numero"] == "absence" and v["preuve"] == "https://registre.example/fiche/12"


def test_une_alerte_sur_le_nom_seul_reste_une_alerte(monkeypatch):
    rendus = {"Atelier du Phare": [{"nom": "Atelier du Phare", "origine": "fiche 1"}, {"nom": "Atelier du Phare", "signal": "alerte", "origine": "liste"}]}
    v = _verifier(monkeypatch, [{"nom": "Atelier du Phare"}], rendus)[0]["faits"]["verifications"][0]
    assert v["signal"] == "alerte" and v["origine"] == "liste"


def test_une_ancienne_confirmation_sur_le_nom_seul_ne_releve_plus_rien():
    lignes = [{"nom": "X", "faits": {"verifications": [{"source": "registre-test", "signal": "meme_nom"}]}}]
    fiabilite_effective(lignes, SPEC)
    assert "fiabilite_effective" not in lignes[0]["faits"]


def test_la_page_dit_meme_nom_et_ce_qui_concorde_ou_differe():
    from pathlib import Path

    js = (Path(__file__).resolve().parents[1] / "static/tri.js").read_text(encoding="utf-8")
    assert "Même nom seulement (non confirmé)" in js and "concorde : " in js and "diffère : " in js
