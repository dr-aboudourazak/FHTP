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
    TypeActeImagerie,
    TypeHospitalisation,
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

    # Ajoute pour R-TG-019 (restrictions TDM/IRM). Le type d'acte d'imagerie
    # est resolu en amont a partir de la nomenclature complete de l'acte
    # (pas encore construite comme referentiel, cf. JOURNAL_DEV.md) --
    # jamais devine a partir du seul code_acte brut.
    type_acte_imagerie: Optional[TypeActeImagerie] = None

    # Resolus par _enrichir_dossier (Gestionnaire de Dossiers) quand un
    # RegistrePrescripteurs est fourni et que id_prescripteur s'y trouve --
    # sinon, restent tels que fournis par l'appelant (meme principe que
    # MedicamentPrescrit.prescripteur_paramedical).
    prescripteur_est_medecin: Optional[bool] = None
    prescripteur_est_specialiste: Optional[bool] = None

    # Ajoute pour R-TG-016/RP24-11 (visite de controle repetee pour le meme
    # motif -- tarif de consultation nul attendu). Resolu en amont par
    # comparaison avec les dossiers precedents du meme beneficiaire (le
    # Gestionnaire de Dossiers actuel n'a pas encore acces a l'historique
    # cross-dossier, cf. JOURNAL_DEV.md).
    visite_controle_meme_motif: Optional[bool] = None

    # Ajoute pour RG-H01 (acte sous entente prealable realise sans PEC,
    # hors urgence regularisee). Distinct de pec_id : ce champ indique si
    # CET acte precis est de la categorie qui exige une PEC, pec_id indique
    # si une PEC est effectivement rattachee.
    soumis_pec: Optional[bool] = None

    # Ajoute pour RP24-09 (prescripteur rattache a la formation sanitaire
    # du dossier). Resolu par _enrichir_dossier via RegistrePrescripteurs
    # (Prescripteur.structures_rattachement) quand ce registre est fourni.
    prescripteur_rattache_formation: Optional[bool] = None

    # Ajoute pour RP24-23 (bilans de sante a priori / infertilite exclus de
    # la charge AMU).
    est_bilan_sante_priori_ou_infertilite: Optional[bool] = None

    # Ajoute pour RP24-27 (radiographies de plus de deux segments osseux
    # simultanes exigent une PEC, sauf polytraumatisme -- champ
    # `polytraumatisme` correspondant porte au niveau du Dossier).
    radiographie_plus_de_2_segments: Optional[bool] = None


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
    # None = non encore verifie (ne declenche pas R-TG-004) ; False =
    # verifie et confirme absent de Presta+. Un defaut a False plutot qu'a
    # None ferait declencher R-TG-004 sur tout medicament dont ce champ n'a
    # simplement pas encore ete renseigne -- exactement le genre de
    # confusion "absence de donnee" vs "donnee negative confirmee" que les
    # autres regles de ce referentiel evitent deliberement partout ailleurs
    # (ex: R-TG-022 ne se declenche que sur cloture_triple_trait == False,
    # jamais sur son absence).
    enrole_presta_plus: Optional[bool] = None
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

    # Ajoute pour RG-P11 (prix public de cession inferieur au tarif AMU ->
    # facturer au prix le plus bas).
    prix_public_pharmacie: Optional[float] = None

    # Ajoute pour RP24-09 (prescripteur rattache a la formation sanitaire
    # du dossier), meme logique que sur ActeRealise -- une prescription
    # medicamenteuse est aussi soumise a cette regle.
    prescripteur_rattache_formation: Optional[bool] = None


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

    # Ajoute pour R-TG-002 (delai de soumission, au plus tard le 5 du mois
    # suivant). Calcule en amont plutot que par arithmetique de dates dans
    # l'evaluateur -- meme principe que jours_depuis_prescription.
    hors_delai_soumission: Optional[bool] = None

    # Ajoute pour R-TG-003 (recu du ticket moderateur obligatoire sauf
    # exemption double couverture) et R-TG-008 (cachet du prescripteur avec
    # numero d'Ordre) -- controles de completude administrative de presence
    # documentaire, resolus en amont (saisie, agent, ou OCR section 14.8).
    recu_ticket_moderateur_present: Optional[bool] = None
    exemption_double_couverture: Optional[bool] = None
    cachet_numero_ordre_present: Optional[bool] = None

    # Ajoute pour R-TG-023 (AMU Scolaire, taux 100% -- part patient nulle).
    # Resolu en amont a partir du Beneficiaire (le Gestionnaire de Dossiers
    # ne resout pas encore cette jointure lui-meme).
    beneficiaire_amu_scolaire: Optional[bool] = None

    # Ajoute pour le groupe de regles d'hospitalisation (RG-H02, RG-H03,
    # RG-H05, RG-H06, RG-H09). Champs resolus en amont : le modele ne porte
    # pas encore de veritables dates d'entree/sortie distinctes de
    # date_soins, ni de resolution du secteur -- ajoutes ici plutot que de
    # forcer ces regles a s'appuyer sur des champs deja existants mais
    # semantiquement differents.
    type_hospitalisation: Optional[TypeHospitalisation] = None
    duree_sejour_jours: Optional[int] = None
    justification_medicale_presente: Optional[bool] = None
    rapport_sortie_present: Optional[bool] = None
    delai_transmission_hospitalisation_depasse: Optional[bool] = None
    nombre_nuitees_facturees: Optional[int] = None
    nombre_nuitees_attendues: Optional[int] = None

    # Ajoute pour affiner RG-H01 avec l'exception d'urgence (RG-H07/RP24-17) :
    # une admission d'urgence dispose d'un delai de grace de 24h avant que
    # l'absence de PEC ne devienne une anomalie.
    est_urgence: Optional[bool] = None
    delai_regularisation_urgence_depasse: Optional[bool] = None

    # Ajoute pour RP24-13 (interventions foraines/campagnes mobiles non
    # remboursees) et RP24-27 (exception polytraumatisme pour les
    # radiographies multi-segments).
    intervention_foraine: Optional[bool] = None
    polytraumatisme: Optional[bool] = None

    # Ajoute pour RP24-04 (rajouts manuscrits d'actes/medicaments apres
    # coup). Resolu en amont -- necessite une inspection visuelle ou OCR du
    # document, pas encore construite comme capacite du systeme
    # (cf. section 14.8, meme limite que la reconnaissance de scans de PEC).
    rajout_manuscrit_detecte: Optional[bool] = None

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
