"""Entites d'identite : beneficiaire, prescripteur, formation sanitaire, contrat payeur.

Reference : FHTP-ARC-001, section 6.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from fhtp_core.models.enums import (
    CategorieContrat,
    GuichetAMU,
    Locale,
    Secteur,
    StatutPrescripteur,
    TypeBaseRemboursement,
    TypeFormationSanitaire,
    TypePrescripteur,
    TypeRegime,
    TypeTarification,
)


class Beneficiaire(BaseModel):
    id_beneficiaire: str
    numero_carte_amu: Optional[str] = None
    type_regime: TypeRegime
    guichet_amu: GuichetAMU
    numero_assurance_privee: Optional[str] = None
    parent_assure_id: Optional[str] = None  # ayant droit
    date_affiliation: date

    # Ajoute par ADR-012 (section 10, note pilier 2). Renseigne uniquement
    # quand le contrat distingue explicitement des niveaux de couverture.
    categorie_contrat: Optional[CategorieContrat] = None


class Prescripteur(BaseModel):
    id_prescripteur: str
    numero_ordre: str
    code_prescripteur_amu: str
    type_prescripteur: TypePrescripteur
    specialite_declaree: Optional[str] = None
    structures_rattachement: list[str] = Field(default_factory=list)
    statut: StatutPrescripteur = StatutPrescripteur.ACTIF


class FormationSanitaire(BaseModel):
    id_formation: str
    code_formation_sanitaire_amu: str
    numero_autorisation_ministere_sante: str
    type: TypeFormationSanitaire
    secteur: Secteur
    date_conventionnement: date

    # Ajoute section 13.4 -- independant du payeur auquel la structure soumet.
    locale_rapport_preferee: Optional[Locale] = None


class ContratPayeur(BaseModel):
    """Rattache chaque dossier a un contrat precis plutot que de supposer un
    bareme unique par payeur (cf. R-TG-024 : deux assures du meme payeur CAT
    peuvent relever de contrats differents)."""

    id_contrat: str
    id_payeur_connecteur: str
    type_tarification: TypeTarification
    type_base_remboursement: TypeBaseRemboursement
    reference_bareme: Optional[str] = None  # inapplicable si FRAIS_REEL
    date_debut_validite: date
    date_fin_validite: Optional[date] = None
