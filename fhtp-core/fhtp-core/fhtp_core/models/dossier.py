"""Dossier -- entite centrale du modele consolide.

Reference : FHTP-ARC-001, section 6.
Un dossier cree en MODE_DEGRADE ne peut jamais recevoir FAST_TRACK avant
reevaluation en ligne (section 7.2, ADR-003) -- cette contrainte est encodee
dans le moteur de decision (fhtp_core.engine), pas ici : ce module ne fait
que decrire la forme des donnees, jamais la logique de decision.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from fhtp_core.models.enums import (
    CircuitRemboursement,
    DecisionFinale,
    OrigineCreation,
    Pilier,
    StatutDossier,
    StatutPilier,
    StatutValidationLigne,
    TypeScenario,
    VoieAdministration,
)


class AlerteRecours(BaseModel):
    """Cf. section 2.2 -- ne fige jamais un delai unique, contextualise
    selon le regime (AMU/CAT/double couverture)."""

    active: bool = False
    regime: Optional[str] = None  # "AMU" | "CAT" | "MIXTE"
    delai_indicatif: Optional[str] = None
    action_recommandee: Optional[str] = None


class ActeRealise(BaseModel):
    id_acte: str
    id_dossier: str
    id_prescripteur: str
    code_acte: str  # nomenclature AMU ou lettre-cle CAT
    diagnostic_cim10: str
    date_realisation: date
    montant_facture: float
    base_remboursement: Optional[float] = None
    taux_payeur: Optional[float] = None
    part_patient: Optional[float] = None
    pec_id: Optional[str] = None
    statut_validation: StatutValidationLigne = StatutValidationLigne.A_VERIFIER


class MedicamentPrescrit(BaseModel):
    id_prescription: str
    id_dossier: str
    dci: str
    nom_commercial: Optional[str] = None
    voie_administration: VoieAdministration
    dosage: Optional[str] = None
    duree_traitement_jours: int
    quantite: int
    prix_unitaire_facture: float
    prix_reference_presta_plus: Optional[float] = None
    enrole_presta_plus: bool = False
    pec_id: Optional[str] = None  # si TPC ou duree > 15 jours
    substituant_dci: Optional[str] = None
    statut_validation: StatutValidationLigne = StatutValidationLigne.A_VERIFIER

    # Ajoute pour l'evaluation de R-TG-014/RG-P06 (validite d'ordonnance,
    # 7 jours). Calcule en amont (saisie, agent, ou API) plutot que par
    # arithmetique de dates dans l'evaluateur de conditions -- garde
    # l'evaluateur de regles au strict minimum syntaxique (section
    # fhtp_core.rules.conditions, motif de securite).
    jours_depuis_prescription: Optional[int] = None


class Dossier(BaseModel):
    id_dossier: str
    type_scenario: TypeScenario
    id_beneficiaire: str
    id_formation: str
    id_contrat_payeur: str  # determine le mode de calcul tarifaire applique
    circuit_remboursement: CircuitRemboursement
    date_soins: date
    date_soumission: datetime

    statut: StatutDossier = StatutDossier.SOUMIS
    evaluation_piliers: dict[Pilier, StatutPilier] = Field(default_factory=dict)
    decision_finale: Optional[DecisionFinale] = None
    motifs_rejet: list[str] = Field(default_factory=list)  # RegleId...
    alerte_recours: AlerteRecours = Field(default_factory=AlerteRecours)

    origine_creation: OrigineCreation = OrigineCreation.EN_LIGNE
    # Cf. section 7.2 : un dossier MODE_DEGRADE ne peut jamais recevoir
    # FAST_TRACK avant reverification en ligne post-synchronisation.

    id_lot: Optional[str] = None  # section 14 -- rattachement a un Lot_Soumission

    actes: list[ActeRealise] = Field(default_factory=list)
    medicaments: list[MedicamentPrescrit] = Field(default_factory=list)

    # Ajoute pour l'evaluation de R-TG-022/RG-P10 (cloture par trois traits
    # obliques). None = non renseigne (ne declenche pas la regle -- une
    # regle ne doit jamais se prononcer sur une donnee absente, seulement
    # sur une donnee positivement non conforme).
    cloture_triple_trait: Optional[bool] = None

    def tous_piliers_conformes(self) -> bool:
        """Vrai si tous les piliers evalues sont CONFORME ou NON_EVALUE.

        Reference : section 2.1, logique de decision.
        """
        return all(
            statut in (StatutPilier.CONFORME, StatutPilier.NON_EVALUE)
            for statut in self.evaluation_piliers.values()
        )

    def a_une_anomalie(self) -> bool:
        return StatutPilier.ANOMALIE in self.evaluation_piliers.values()

    def a_verifier_seulement(self) -> bool:
        return (
            StatutPilier.A_VERIFIER in self.evaluation_piliers.values()
            and not self.a_une_anomalie()
        )
