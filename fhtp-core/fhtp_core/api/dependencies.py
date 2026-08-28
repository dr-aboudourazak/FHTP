"""Dependances de l'API -- assemble le referentiel de regles, le journal, le
gestionnaire de dossiers, un connecteur payeur et l'annuaire de jetons
(section 8.3/F4) pour toute la duree de vie du processus.

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

import os

from fhtp_core.api.auth import AnnuaireJetons, construire_dependance_authentification
from fhtp_core.api.persistence import StoreDossiersSQLite
from fhtp_core.connectors.payeur import IConnecteurPayeur
from fhtp_core.connectors.simulateur_payeur import SimulateurConnecteurPayeur
from fhtp_core.engine.gestionnaire_dossiers import GestionnaireDossiers
from fhtp_core.engine.journal import JournalConformite
from fhtp_core.engine.referentiels import RegistreFormationsSanitaires, RegistrePrescripteurs
from fhtp_core.rules.loader import charger_regles

_journal = JournalConformite()
_regles = charger_regles()
_registre_prescripteurs = RegistrePrescripteurs()
_registre_formations = RegistreFormationsSanitaires()
_gestionnaire = GestionnaireDossiers(
    regles=_regles,
    journal=_journal,
    registre_prescripteurs=_registre_prescripteurs,
    registre_formations=_registre_formations,
)

# Chemin configurable via FHTP_DB_PATH -- ":memory:" pour une base
# ephemere (utile en test ou en demonstration jetable), un vrai chemin de
# fichier sinon. Par defaut, un fichier local : le premier pas hors du
# "tout en memoire", pas encore une vraie infrastructure de production
# (pas de sauvegarde, pas de replication -- cf. JOURNAL_DEV.md).
_chemin_bdd_dossiers = os.environ.get("FHTP_DB_PATH", "fhtp_dossiers.db")
_dossiers = StoreDossiersSQLite(_chemin_bdd_dossiers)

_connecteur_par_defaut: IConnecteurPayeur = SimulateurConnecteurPayeur()
_annuaire_jetons = AnnuaireJetons()

# Dependance FastAPI d'authentification, liee a l'annuaire de ce module --
# c'est elle que les routes utilisent via Depends(obtenir_operateur_courant).
obtenir_operateur_courant = construire_dependance_authentification(_annuaire_jetons)


def get_journal() -> JournalConformite:
    return _journal


def get_gestionnaire() -> GestionnaireDossiers:
    return _gestionnaire


def get_registre_prescripteurs() -> RegistrePrescripteurs:
    return _registre_prescripteurs


def get_registre_formations() -> RegistreFormationsSanitaires:
    return _registre_formations


def get_connecteur_payeur() -> IConnecteurPayeur:
    return _connecteur_par_defaut


def get_store() -> StoreDossiersSQLite:
    return _dossiers


def get_annuaire_jetons() -> AnnuaireJetons:
    return _annuaire_jetons


def reinitialiser_etat_pour_tests() -> None:
    """Reinitialise l'etat entre deux tests -- jamais destine a un usage en
    dehors de la suite de tests."""
    _dossiers.clear()
    _annuaire_jetons.reinitialiser()
