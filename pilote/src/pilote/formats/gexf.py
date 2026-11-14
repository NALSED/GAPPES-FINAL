"""Format de sortie « Réseau (GEXF) » (fiche 14) : les noms et leurs liens (maison mère, siège, même adresse...), pour Gephi et les logiciels de réseaux.
GEXF 1.3. Un lien vers un nom qui n'est pas dans la sortie crée un nœud « extérieur ». La trace est dans `<meta><description>`."""

from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET
from pathlib import Path

from pilote.formats._commun import phrase_trace, propre_xml

FORMAT = {
    "id": "gexf",
    "nom": "Réseau (GEXF)",
    "description": "Les noms et leurs liens, pour Gephi et les logiciels de réseaux.",
    "extension": ".gexf",
    "famille": "fichier",
    "contenus": ["detail"],
    "contenus_defaut": ["detail"],
}
NS = "http://gexf.net/1.3"
ATTRIBUTS = [("origine", "string"), ("ville", "string"), ("pays", "string"), ("fonction", "string"), ("decision", "string"), ("site", "string")]


def ecrire(jeu: dict, contenu: str, options: dict, chemin: Path) -> dict:
    ET.register_namespace("", NS)
    racine = ET.Element(f"{{{NS}}}gexf", {"version": "1.3"})
    meta = ET.SubElement(racine, f"{{{NS}}}meta", {"lastmodifieddate": jeu["trace"]["date"][:10]})
    ET.SubElement(meta, f"{{{NS}}}creator").text = "pilote"
    ET.SubElement(meta, f"{{{NS}}}description").text = propre_xml("\n".join(phrase_trace(jeu["trace"])))
    graphe = ET.SubElement(racine, f"{{{NS}}}graph", {"defaultedgetype": "directed", "mode": "static"})
    attrs = ET.SubElement(graphe, f"{{{NS}}}attributes", {"class": "node"})
    for i, (nom, type_) in enumerate(ATTRIBUTS):
        ET.SubElement(attrs, f"{{{NS}}}attribute", {"id": str(i), "title": nom, "type": type_})
    noeuds = ET.SubElement(graphe, f"{{{NS}}}nodes")
    liens = ET.SubElement(graphe, f"{{{NS}}}edges")
    par_cle: dict[tuple[str, str], str] = {}

    def noeud(cle: tuple[str, str], nom: str, valeurs: dict | None) -> str:
        if cle in par_cle:
            return par_cle[cle]
        ident = f"n{len(par_cle) + 1}"
        par_cle[cle] = ident
        n = ET.SubElement(noeuds, f"{{{NS}}}node", {"id": ident, "label": propre_xml(nom)})
        vals = ET.SubElement(n, f"{{{NS}}}attvalues")
        v = valeurs or {"origine": "extérieur à la recherche"}
        for i, (a, _) in enumerate(ATTRIBUTS):
            if v.get(a):
                ET.SubElement(vals, f"{{{NS}}}attvalue", {"for": str(i), "value": propre_xml(v[a])})
        return ident

    # Un point par FICHE, jamais par nom : deux homonymes (même nom, deux villes) devenaient un seul point, et les liens de l'un passaient à l'autre.
    homonymes: dict[str, list[str]] = {}
    for k, r in enumerate(jeu["lignes"]):
        cle_fiche = ("fiche", str(r.get("id", k)))
        ident = noeud(cle_fiche, r["nom"], {"origine": r["origine_phrase"], "ville": r["ville"], "pays": r["pays"], "fonction": r["fonction"], "decision": r["decision"] or "", "site": r["site"]})
        homonymes.setdefault(r["nom"].casefold().strip(), []).append(ident)

    def cible(vers: str) -> str:
        """Le point d'une fiche de la sortie si son nom n'y désigne qu'elle ; sinon (absent, ou plusieurs homonymes) un point « extérieur » : on ne choisit pas au hasard."""
        memes = homonymes.get(vers.casefold().strip(), [])
        return memes[0] if len(memes) == 1 else noeud(("exterieur", vers.casefold().strip()), vers, None)

    n_liens = 0
    for k, r in enumerate(jeu["lignes"]):
        depart = par_cle[("fiche", str(r.get("id", k)))]
        for x in r["relations"]:
            vers = str(x.get("vers", "")).strip()
            if not vers:
                continue
            n_liens += 1
            type_ = str(x.get("type", ""))
            ident = hashlib.sha1(f"{r['nom']}|{type_}|{vers}".encode()).hexdigest()[:10]
            ET.SubElement(liens, f"{{{NS}}}edge", {"id": f"e{n_liens}_{ident}", "source": depart, "target": cible(vers), "label": propre_xml(type_.replace("_", " "))})
    ET.indent(racine)
    ET.ElementTree(racine).write(chemin, encoding="utf-8", xml_declaration=True)
    return {"fichiers": [chemin]}
