"""Contrat generique des connecteurs payeurs -- FHTP-ARC-001, section 3.1.

L'INAM, la CNSS et les assureurs CAT sont des connecteurs interchangeables :
aucune logique propre a l'un d'eux ne doit penetrer dans FHTP Core
(FHTP-KNO-001, section 3.4). Ce module ne definit QUE le contrat -- aucune
implementation reelle ici, pas plus qu'un simulateur (voir
fhtp_core.connectors.simulateur_payeur pour les tests).

Toute indisponibilite reseau doit etre signalee par
fhtp_core.connectors.exceptions.ConnecteurIndisponible, jamais par un retour
silencieux ou une exception generique -- c'est ce signal precis que le
Gestionnaire de Dossiers utilise pour basculer en Mode Degrade (section 7).
"""

from __future__ import annotations

from datetime import date
from typing import Optional, Protocol, runtime_checkable

from pydantic import BaseModel

from fhtp_core.models.enums import (
    StatutBaseRemboursement,
    StatutEligibilite,
    StatutPEC,
    StatutSoumissionFacture,
    TypeTarification,
)
from fhtp_core.models.dossier import Dossier


class ResultatEligibilite(BaseModel):
    """Retour de verifier_eligibilite (section 3.1)."""

    statut: StatutEligibilite
    taux_couverture: Optional[float] = None  # ex: 1.0 pour AMU Scolaire, 0.8 standard
    ticket_moderateur_pct: Optional[float] = None


class BaseRemboursement(BaseModel):
    """Retour de obtenir_base_remboursement (section 3.1).

    Independant de la nomenclature propre au payeur (R/E/TPC pour AMU,
    lettre-cle/coefficient pour CAT) -- ce modele est deja la traduction
    generique, calculee par le connecteur, jamais par FHTP Core."""

    montant_base: Optional[float] = None
    taux: Optional[float] = None
    statut: StatutBaseRemboursement


class ResultatSoumissionFacture(BaseModel):
    """Retour de soumettre_facture (section 3.1)."""

    statut: StatutSoumissionFacture
    motifs: list[str] = []
    numero_reference: Optional[str] = None


@runtime_checkable
class IConnecteurPayeur(Protocol):
    """Contrat que tout connecteur payeur doit implementer.

    Trois methodes seulement dans le document maitre (section 3.1). Une
    quatrieme, `verifier_pec`, est ajoutee ici pour formaliser une exigence
    deja posee ailleurs dans le meme document mais jamais nommee comme
    methode d'interface : la correction F7 (section 8.2) exige que la
    validite d'une PEC soit "toujours verifiee par requete au connecteur
    payeur concerne, jamais par la seule presence d'un numero au bon
    format" -- ce qui suppose necessairement un point d'entree dedie sur le
    contrat. Cet ajout formalise une exigence deja actee, il n'invente
    aucune regle metier nouvelle.

    Declare aussi son mode de tarification (MODE_ACTE ou
    MODE_FORFAIT_DIAGNOSTIC, FHTP-KNO-001 section 3.6) via
    `mode_tarification`, pour que FHTP Core adapte son evaluation du pilier
    "coherence tarifaire" sans qu'aucune logique propre a un mode ne
    s'infiltre dans le Core.
    """

    mode_tarification: TypeTarification

    def verifier_eligibilite(
        self, identifiant_beneficiaire: str, date_soins: date
    ) -> ResultatEligibilite:
        """Leve ConnecteurIndisponible si le payeur est injoignable."""
        ...

    def obtenir_base_remboursement(
        self, code_acte_ou_dci: str, date_soins: date
    ) -> BaseRemboursement:
        """Leve ConnecteurIndisponible si le payeur est injoignable."""
        ...

    def soumettre_facture(self, dossier: Dossier) -> ResultatSoumissionFacture:
        """Leve ConnecteurIndisponible si le payeur est injoignable."""
        ...

    def verifier_pec(self, numero_reference: str) -> StatutPEC:
        """Cf. F7 (section 8.2) -- jamais de validation d'une PEC sur la
        seule presence d'un numero au bon format. Leve ConnecteurIndisponible
        si le payeur est injoignable (cf. section 15, verification hors
        connexion avec piece scannee comme filet provisoire)."""
        ...
