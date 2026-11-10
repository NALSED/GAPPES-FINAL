"""Le nombre d'appels faits par une recherche, lu dans son fichier d'avancement. Séparé de `executer.py` pour pouvoir être essayé sans la bibliothèque grappes.

Le fichier ne fait que grandir et le compte est demandé avant chaque appel d'une source : on ne lit donc que ce qui s'est ajouté depuis la dernière fois.
Le relire en entier coûtait d'autant plus cher que la recherche avançait."""

from __future__ import annotations

import threading

MARQUE = b'"evenement": "appel"'


class CompteurAppels:
    """Peut être interrogé de plusieurs fils à la fois (chaque source tourne dans le sien). Seules les lignes complètes comptent : une ligne en cours d'écriture sera lue la fois suivante."""

    def __init__(self, chemin: str | None):
        self.chemin, self.position, self.n = chemin, 0, 0
        self._verrou = threading.Lock()

    def total(self) -> int:
        if not self.chemin:
            return 0
        with self._verrou:
            try:
                with open(self.chemin, "rb") as f:
                    f.seek(self.position)
                    brut = f.read()
            except FileNotFoundError:
                return self.n
            fin = brut.rfind(b"\n") + 1
            self.position += fin
            self.n += sum(1 for ligne in brut[:fin].splitlines() if MARQUE in ligne)
            return self.n
