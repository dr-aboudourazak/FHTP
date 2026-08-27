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

    # Absent du modele canonique d'origine (section 6) -- ajoute pour
    # permettre une resolution reelle du type de prescripteur (R-TG-021),
    # plutot que de dependre uniquement d'un champ precalcule fourni sans
    # garantie. Nullable : une ligne peut encore fonctionner sans, via le
    # champ precalcule prescripteur_paramedical si aucun registre n'est
    # disponible cote appelant.
    id_prescripteur: Optional[str] = None

    # Ajoute pour l'evaluation de R-TG-014/RG-P06 (validite d'ordonnance,
    # 7 jours). Calcule en amont (saisie, agent, ou API) plutot que par
    # arithmetique de dates dans l'evaluateur de conditions -- garde
    # l'evaluateur de regles au strict minimum syntaxique (section
    # fhtp_core.rules.conditions, motif de securite).
    jours_depuis_prescription: Optional[int] = None

    # Ajoute pour RG-P07 (substitution generique plus chere que le produit
    # initial, sans accord medecin traitant + medecin-conseil). Le prix du
    # produit initial est distinct de prix_reference_presta_plus : ce
    # dernier est le tarif de reference, celui-ci est le prix reellement
    # facture pour le produit d'origine avant substitution.
    prix_produit_initial: Optional[float] = None

    # Ajoute pour R-TG-021/RG-P09 (restriction paramedicale). Resolus en
    # amont a partir du type du Prescripteur et de la liste des molecules
    # proscrites (FHTP-REF-001, Partie 4.3) -- le Gestionnaire de Dossiers
    # actuel ne resout pas encore ces jointures lui-meme (cf. JOURNAL_DEV.md).
    prescripteur_paramedical: Optional[bool] = None
    molecule_proscrite_paramedical: Optional[bool] = None


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

    # Ajoute pour l'evaluation de R-TG-020 (max 3 echographies obstetricales
    # par grossesse). Comptage fait en amont (saisie, agent, ou API) plutot
    # que par une fonction de comptage dans l'evaluateur de conditions --
    # meme raisonnement que jours_depuis_prescription : garder l'evaluateur
    # au strict minimum syntaxique (aucune fonction, meme "sans danger",
    # n'y est autorisee).
    nombre_echographies_obstetricales: Optional[int] = None
    pec_echographie_supplementaire_id: Optional[str] = None

    # Ajoute pour l'evaluation de RG-H11 (medicaments oraux non rembourses
    # en clinique privee sous AMU). Resolu en amont a partir du type de la
    # Formation_Sanitaire (section 6) -- le Gestionnaire de Dossiers actuel
    # ne resout pas encore cette jointure lui-meme (cf. JOURNAL_DEV.md).
    structure_est_clinique_privee: Optional[bool] = None

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
