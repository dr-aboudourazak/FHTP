"""Store de dossiers persistant (SQLite) -- remplace le dictionnaire en
memoire de `dependencies.py`, qui perdait tout au redemarrage du processus.

Reste volontairement minimal : une seule table cle/valeur (id_dossier ->
JSON serialise du Dossier complet). Suffisant pour ce stade du projet ; une
vraie base relationnelle avec index sur les champs interrogeables
(id_formation, statut, date_soins) reste a construire quand des recherches
au-dela de la consultation par identifiant deviendront necessaires --
section 19.6 laisse ce choix technique ouvert, ce module ne le tranche pas
definitivement, il comble juste l'ecart le plus urgent (tout perdre au
redemarrage).

Interface volontairement compatible avec un dict simple (`__contains__`,
`__setitem__`, `get`, `clear`) pour que les routes de l'API n'aient rien a
changer par rapport a l'ancien store en memoire.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional, Union

from fhtp_core.models.dossier import Dossier


class StoreDossiersSQLite:
    def __init__(self, chemin_bdd: Union[str, Path]) -> None:
        self._chemin = str(chemin_bdd)
        # check_same_thread=False : FastAPI/TestClient peuvent solliciter
        # cette connexion depuis un thread different de celui qui l'a
        # ouverte (pool d'execution des routes synchrones) -- la table est
        # simple et les operations courtes, pas besoin d'un pool de
        # connexions a ce stade.
        self._connexion = sqlite3.connect(self._chemin, check_same_thread=False)
        self._connexion.execute(
            "CREATE TABLE IF NOT EXISTS dossiers ("
            "  id_dossier TEXT PRIMARY KEY,"
            "  donnees TEXT NOT NULL"
            ")"
        )
        self._connexion.commit()

    def __contains__(self, id_dossier: str) -> bool:
        curseur = self._connexion.execute(
            "SELECT 1 FROM dossiers WHERE id_dossier = ?", (id_dossier,)
        )
        return curseur.fetchone() is not None

    def __setitem__(self, id_dossier: str, dossier: Dossier) -> None:
        self._connexion.execute(
            "INSERT OR REPLACE INTO dossiers (id_dossier, donnees) VALUES (?, ?)",
            (id_dossier, dossier.model_dump_json()),
        )
        self._connexion.commit()

    def get(self, id_dossier: str) -> Optional[Dossier]:
        curseur = self._connexion.execute(
            "SELECT donnees FROM dossiers WHERE id_dossier = ?", (id_dossier,)
        )
        ligne = curseur.fetchone()
        if ligne is None:
            return None
        return Dossier.model_validate_json(ligne[0])

    def clear(self) -> None:
        """Vide entierement le store -- destine a la reinitialisation entre
        deux tests, jamais a un usage courant."""
        self._connexion.execute("DELETE FROM dossiers")
        self._connexion.commit()

    def fermer(self) -> None:
        self._connexion.close()
