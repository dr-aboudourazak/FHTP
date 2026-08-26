"""Entites operationnelles ajoutees par les addenda : licence, i18n, batch,
verification de PEC hors connexion.

Reference : FHTP-ARC-001, sections 12 a 15.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from fhtp_core.models.enums import (
    CanalSoumission,
    ConfigurePar,
    FormatSource,
    Locale,
    ModeleTarifaireLicence,
    StatutLicence,
    StatutLot,
    TypeActePEC,
    TypeContratLicence,
    TypeDocumentPayeur,
)


class CleLicence(BaseModel):
    """Cf. section 12.5-12.6. Jeton signe, verifiable localement sans appel
    reseau systematique -- fonctionne identiquement en cloud ou en Instance
    Locale (ADR-006). Degradation en quatre phases sur 60 jours, jamais de
    coupure seche (ADR-007, validee par Dr Amadou le 9 juillet 2026)."""

    id_licence: str
    id_formation: str
    type_contrat: TypeContratLicence
    modele_tarifaire: ModeleTarifaireLicence
    date_debut: date
    date_expiration: date
    statut: StatutLicence = StatutLicence.ACTIVE
    derniere_verification_en_ligne: Optional[datetime] = None
    jeton_signe: str

    def jours_depuis_expiration(self, aujourdhui: date) -> int:
        return (aujourdhui - self.date_expiration).days


class ReferentielLibelle(BaseModel):
    """Separe le texte affiche (par langue) de la logique des regles, qui
    continue de raisonner en identifiants (rule_id), jamais en texte
    (section 13.1-13.2)."""

    id_libelle: str  # ex: MSG-R-TG-017-REJET
    locale: Locale
    texte: str
    version: int = 1


class LotSoumission(BaseModel):
    """Regroupe les dossiers soumis en fin de mois par un centre qui facture
    avec son propre logiciel plutot qu'au fil de l'eau (section 14.1)."""

    id_lot: str
    id_formation: str
    periode_couverte: str  # ex: "2026-06"
    date_soumission: datetime
    format_source: FormatSource
    canal: CanalSoumission
    nombre_dossiers_detectes: int = 0
    statut_lot: StatutLot = StatutLot.RECU


class ProfilImportCentre(BaseModel):
    """FHTP s'adapte au format deja utilise par le centre plutot que
    d'imposer un format unique (section 14.7)."""

    id_profil: str
    id_formation: str
    format_source: FormatSource
    mapping_colonnes: dict[str, str]  # "Colonne C" -> "montant_facture"
    date_configuration: date
    configure_par: ConfigurePar = ConfigurePar.EQUIPE_FHTP


class ModelePayeurSocle(BaseModel):
    """Mentions communes a tous les documents d'un payeur (en-tete, cachet,
    signature du medecin-conseil) -- section 15.3."""

    id_payeur_connecteur: str
    mentions_communes: list[str]
    date_version: date


class ModeleDocumentPayeur(BaseModel):
    """Mentions specifiques a un type d'acte pour un payeur donne -- un meme
    payeur n'a pas le meme format de PEC selon le type d'acte (section 15.3).
    Sert a un controle de coherence structurelle, jamais a une preuve
    cryptographique ni a un substitut de la verification en ligne (F7)."""

    id_modele: str
    id_payeur_connecteur: str
    type_acte: TypeActePEC
    type_document: TypeDocumentPayeur
    mentions_specifiques: list[str]
    date_version: date
    source: str
    variante_centre: Optional[str] = None  # FK Formation_Sanitaire, vide par defaut
