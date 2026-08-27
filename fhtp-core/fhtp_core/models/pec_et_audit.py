"""PEC/Entente Prealable, consentement patient, contestation, journal d'audit.

Reference : FHTP-ARC-001, section 6.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from fhtp_core.models.enums import (
    EventType,
    PartieRecours,
    StatutConsentement,
    StatutContestation,
    StatutPEC,
    TypeConsentement,
    TypePEC,
)


class PECEntentePrealable(BaseModel):
    id_pec: str
    id_dossier: str
    id_payeur_connecteur: str
    type: TypePEC
    motif: str
    date_demande: date
    date_reponse: Optional[date] = None
    statut: StatutPEC = StatutPEC.EN_ATTENTE
    numero_reference_payeur: Optional[str] = None

    # Ajoute section 15.2 -- trace le document scanne fourni quand le
    # connecteur payeur est injoignable. Ne remplace jamais la verification
    # en ligne (F7, section 8.2) : sert de filet provisoire uniquement.
    scan_hash: Optional[str] = None


class ConsentementPatient(BaseModel):
    """Cf. FHTP-KNO-001 section 3.3. Un dossier ne peut etre soumis a un
    payeur sans consentement ACTIF de type AFFILIATION_LARGE au minimum."""

    id_consentement: str
    id_beneficiaire: str
    type: TypeConsentement
    date_signature: date
    canal_notification: Optional[str] = None  # "SMS" | "EMAIL" | "AUCUN"
    statut: StatutConsentement = StatutConsentement.ACTIF


class ContestationRecours(BaseModel):
    """Cf. Decret n2023-100/PR, art. 11 : frais d'expertise a la charge de la
    partie perdante. Applicable aux dossiers relevant d'un connecteur AMU."""

    id_contestation: str
    id_dossier: str
    partie_demandeuse: PartieRecours
    motif: str
    date_demande: date
    expert_designe: Optional[str] = None
    decision_initiale_id: str  # FK vers l'entree Log_Audit contestee
    statut: StatutContestation = StatutContestation.EN_ATTENTE
    partie_perdante: Optional[PartieRecours] = None


class LogAudit(BaseModel):
    """Append-only, immuable -- section 2.4 et 8.2 (F2 : chainage
    cryptographique, ancrage externe periodique type OpenTimestamps)."""

    id_log: str
    timestamp: datetime
    id_dossier: str
    event_type: EventType
    regle_id: Optional[str] = None
    resultat: str
    payload_hash: str
    operateur_id: str

    # Chainage cryptographique (F2, section 8.2/8.5) : chaque entree porte le
    # hash de la precedente. Calcul reel a implementer dans engine/, pas ici.
    hash_precedent: Optional[str] = None
