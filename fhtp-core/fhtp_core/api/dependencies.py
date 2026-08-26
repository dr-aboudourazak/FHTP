"""Dependances de l'API -- assemble le referentiel de regles, le journal, le
gestionnaire de dossiers et un connecteur payeur pour toute la duree de vie
du processus.

Etat en memoire pour l'instant (store de dossiers, connecteur par defaut) --
aucune persistance reelle a ce stade (pas de base de donnees choisie,
section 19.6). Suffisant pour demontrer et tester le pipeline complet de
bout en bout ; a remplacer avant tout usage en production.

Un seul connecteur simule est partage ici, faute de vrais connecteurs
INAM/CNSS/CAT deja ecrits (section 4). A remplacer par un vrai registre
garde par id_contrat_payeur une fois ces connecteurs implementes -- la
fonction `get_connecteur_payeur` est deja le point d'extension prevu pour
ca, pas a reecrire plus tard.
"""

from __future__ import annotations

from fhtp_core.connectors.payeur import IConnecteurPayeur
from fhtp_core.connectors.simulateur_payeur import SimulateurConnecteurPayeur
from fhtp_core.engine.gestionnaire_dossiers import GestionnaireDossiers
from fhtp_core.engine.journal import JournalConformite
from fhtp_core.models.dossier import Dossier
from fhtp_core.rules.loader import charger_regles

_journal = JournalConformite()
_regles = charger_regles()
_gestionnaire = GestionnaireDossiers(regles=_regles, journal=_journal)
_dossiers: dict[str, Dossier] = {}
_connecteur_par_defaut: IConnecteurPayeur = SimulateurConnecteurPayeur()


def get_journal() -> JournalConformite:
    return _journal


def get_gestionnaire() -> GestionnaireDossiers:
    return _gestionnaire


def get_connecteur_payeur() -> IConnecteurPayeur:
    return _connecteur_par_defaut


def get_store() -> dict[str, Dossier]:
    return _dossiers


def reinitialiser_etat_pour_tests() -> None:
    """Reinitialise l'etat en memoire entre deux tests -- jamais destine a
    un usage en dehors de la suite de tests."""
    _dossiers.clear()
