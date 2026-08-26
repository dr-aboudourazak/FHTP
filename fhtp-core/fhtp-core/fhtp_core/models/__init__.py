"""Modele de donnees consolide -- FHTP-ARC-001, section 6.

C'est le seul modele que connait FHTP Core (moteur de regles, gestionnaire de
dossiers). Les connecteurs payeurs et terrain traduisent leurs donnees
proprietaires vers ce modele, jamais l'inverse.
"""

from fhtp_core.models.dossier import ActeRealise, AlerteRecours, Dossier, MedicamentPrescrit
from fhtp_core.models.exclusion import ExclusionContrat
from fhtp_core.models.identite import (
    Beneficiaire,
    ContratPayeur,
    FormationSanitaire,
    Prescripteur,
)
from fhtp_core.models.operations import (
    CleLicence,
    LotSoumission,
    ModeleDocumentPayeur,
    ModelePayeurSocle,
    ProfilImportCentre,
    ReferentielLibelle,
)
from fhtp_core.models.pec_et_audit import (
    ConsentementPatient,
    ContestationRecours,
    LogAudit,
    PECEntentePrealable,
)

__all__ = [
    "ActeRealise",
    "AlerteRecours",
    "Beneficiaire",
    "CleLicence",
    "ConsentementPatient",
    "ContestationRecours",
    "ContratPayeur",
    "Dossier",
    "ExclusionContrat",
    "FormationSanitaire",
    "LogAudit",
    "LotSoumission",
    "MedicamentPrescrit",
    "ModeleDocumentPayeur",
    "ModelePayeurSocle",
    "PECEntentePrealable",
    "Prescripteur",
    "ProfilImportCentre",
    "ReferentielLibelle",
]
