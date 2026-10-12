"""Variantes d'un même nom (« Fenix Toulouse » / « Fenix Toulouse Handball ») avec nomenklatura (OpenSanctions).

Aucun rapprochement de noms écrit ici : la comparaison est l'algorithme `name-based` de nomenklatura (noms d'organisations
comparés comme le fait OpenSanctions), les décisions sont enregistrées dans son `Resolver` (base SQLite locale) et les
groupes sont ses identifiants canoniques. Ce module choisit seulement quelles paires comparer (deux noms ne sont
comparés que s'ils partagent un mot distinctif) et le seuil de décision, qui est un paramètre documenté.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

SEUIL_DEFAUT = 0.8  # `name-based` : 0,83 pour « Fenix Toulouse » / « Fenix Toulouse Handball », 0,42 entre deux clubs voisins


def _jetons(nom: str) -> set[str]:
    return {t for t in re.split(r"[^\w]+", nom.casefold()) if len(t) > 2}


def regrouper(
    noms: list[str], seuil: float = SEUIL_DEFAUT, base: str | Path = ":memory:", villes: list[str] | None = None
) -> list[list[int]]:
    """Groupes d'indices de `noms` désignant le même acteur. Un nom seul forme un groupe. Déterministe.

    `villes` (facultatif) : commune donnée par un registre pour chaque nom ; deux noms de communes différentes ne sont
    jamais des variantes (« Conseil régional … de Lyon » / « … de Paris » obtiennent 0,91 de `name-based`)."""
    from followthemoney import model
    from nomenklatura.db import close_db, make_session
    from nomenklatura.judgement import Judgement
    from nomenklatura.matching import ScoringConfig, get_algorithm
    from nomenklatura.resolver import Resolver
    import tempfile

    ents = []
    for i, n in enumerate(noms):
        e = model.make_entity("Organization")
        e.id = f"n{i}"
        e.add("name", n)
        ents.append(e)
    algo, cfg = get_algorithm("name-based"), ScoringConfig.defaults()
    tmp = None
    if str(base) == ":memory:":  # base jetable : les décisions d'un appel ne polluent pas le suivant
        tmp = tempfile.TemporaryDirectory()
        base = Path(tmp.name) / "variantes.db"
    url = f"sqlite:///{base}"
    res = Resolver(make_session(url), create=True)
    par_jeton: dict[str, list[int]] = defaultdict(list)
    for i, n in enumerate(noms):
        for t in _jetons(n):
            par_jeton[t].append(i)
    vues: set[tuple[int, int]] = set()
    for idx in par_jeton.values():
        if len(idx) > 300:  # mot trop courant (« club », « handball ») : ne discrimine rien, on ne compare pas
            continue
        for a in range(len(idx)):
            for b in range(a + 1, len(idx)):
                p = (idx[a], idx[b])
                if p in vues:
                    continue
                vues.add(p)
                if villes and villes[p[0]] and villes[p[1]] and villes[p[0]].casefold() != villes[p[1]].casefold():
                    continue
                s = algo.compare(ents[p[0]], ents[p[1]], cfg).score
                if s >= seuil:
                    res.decide(ents[p[0]].id, ents[p[1]].id, Judgement.POSITIVE, score=s)
    groupes: dict[str, list[int]] = defaultdict(list)
    for i, e in enumerate(ents):
        groupes[str(res.get_canonical(e.id))].append(i)
    close_db(url)
    if tmp is not None:
        tmp.cleanup()
    return sorted(groupes.values())
