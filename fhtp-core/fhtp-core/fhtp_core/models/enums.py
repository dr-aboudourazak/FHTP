"""Enumerations partagees par le modele de donnees consolide.

Reference : FHTP-ARC-001, section 6.
Chaque valeur reprend exactement le vocabulaire du document maitre -- aucune
enumeration n'est inventee ici, elles sont retranscrites depuis le modele
deja valide par Dr Amadou.
"""

from enum import Enum


class TypeRegime(str, Enum):
    INAM_STANDARD = "INAM_STANDARD"
    INAM_SCOLAIRE = "INAM_SCOLAIRE"
    CNSS = "CNSS"
    PRIVE_SEUL = "PRIVE_SEUL"
    DIRECT = "DIRECT"


class GuichetAMU(str, Enum):
    INAM = "INAM"
    CNSS = "CNSS"
    AUCUN = "AUCUN"


class CategorieContrat(str, Enum):
    """Cf. section 6 -- champ ajoute sur Beneficiaire, renseigne uniquement
    quand le contrat distingue des niveaux de couverture (ADR-012)."""

    CADRE = "CADRE"
    EXECUTANT = "EXECUTANT"
    AUTRE = "AUTRE"


class TypePrescripteur(str, Enum):
    MEDECIN = "MEDECIN"
    PARAMEDICAL = "PARAMEDICAL"
    DENTISTE = "DENTISTE"
    PHARMACIEN = "PHARMACIEN"


class StatutPrescripteur(str, Enum):
    ACTIF = "ACTIF"
    SUSPENDU = "SUSPENDU"
    RADIE = "RADIE"


class TypeFormationSanitaire(str, Enum):
    USP_I = "USP_I"
    USP_II = "USP_II"
    HD = "HD"
    CHR = "CHR"
    CLINIQUE_PRIVEE = "CLINIQUE_PRIVEE"
    OFFICINE = "OFFICINE"
    CABINET = "CABINET"


class Secteur(str, Enum):
    PUBLIC = "PUBLIC"
    PRIVE = "PRIVE"


class TypeScenario(str, Enum):
    CONSULTATION = "CONSULTATION"
    HOSPITALISATION = "HOSPITALISATION"
    PHARMACIE = "PHARMACIE"


class CircuitRemboursement(str, Enum):
    AMU_SEUL = "AMU_SEUL"
    AMU_PLUS_PRIVE = "AMU_PLUS_PRIVE"
    PRIVE_SEUL = "PRIVE_SEUL"
    DIRECT = "DIRECT"


class StatutPilier(str, Enum):
    """Cf. section 2.1 -- logique de decision du moteur de regles."""

    CONFORME = "CONFORME"
    A_VERIFIER = "A_VERIFIER"
    ANOMALIE = "ANOMALIE"
    NON_EVALUE = "NON_EVALUE"


class Pilier(str, Enum):
    """Les six piliers de confiance, section 2.1.

    Le pilier COHERENCE_REGIME couvre desormais aussi la verification des
    exclusions de contrat (ADR-012, corrige depuis une premiere version qui
    la placait au pilier COHERENCE_DOCUMENTAIRE).
    """

    COMPLETUDE_ADMINISTRATIVE = "COMPLETUDE_ADMINISTRATIVE"
    COHERENCE_REGIME = "COHERENCE_REGIME"
    COHERENCE_TARIFAIRE = "COHERENCE_TARIFAIRE"
    COHERENCE_DOCUMENTAIRE = "COHERENCE_DOCUMENTAIRE"
    COHERENCE_PRESCRIPTEUR = "COHERENCE_PRESCRIPTEUR"
    COHERENCE_GRAPHIQUE = "COHERENCE_GRAPHIQUE"


class StatutDossier(str, Enum):
    SOUMIS = "SOUMIS"
    EN_VALIDATION = "EN_VALIDATION"
    EN_VALIDATION_LOCALE = "EN_VALIDATION_LOCALE"  # mode degrade, section 7.2
    EN_ATTENTE_CONFIRMATION_OCR = "EN_ATTENTE_CONFIRMATION_OCR"  # section 14.8
    FAST_TRACK = "FAST_TRACK"
    CONTROLE_RAPIDE = "CONTROLE_RAPIDE"
    AUDIT = "AUDIT"
    PAYE = "PAYE"
    REJETE = "REJETE"


class DecisionFinale(str, Enum):
    FAST_TRACK = "FAST_TRACK"
    CONTROLE_RAPIDE = "CONTROLE_RAPIDE"
    AUDIT_APPROFONDI = "AUDIT_APPROFONDI"
    CONTROLE_RENFORCE = "CONTROLE_RENFORCE"
    REJET = "REJET"


class OrigineCreation(str, Enum):
    EN_LIGNE = "EN_LIGNE"
    MODE_DEGRADE = "MODE_DEGRADE"


class TypeTarification(str, Enum):
    MODE_ACTE = "MODE_ACTE"
    MODE_FORFAIT_DIAGNOSTIC = "MODE_FORFAIT_DIAGNOSTIC"


class TypeBaseRemboursement(str, Enum):
    TARIF_FIXE = "TARIF_FIXE"
    FRAIS_REEL = "FRAIS_REEL"


class VoieAdministration(str, Enum):
    ORALE = "ORALE"
    PARENTERALE = "PARENTERALE"
    TOPIQUE = "TOPIQUE"


class StatutValidationLigne(str, Enum):
    """Statut d'une ligne (acte ou medicament) au sein d'un dossier."""

    CONFORME = "CONFORME"
    A_VERIFIER = "A_VERIFIER"
    ANOMALIE = "ANOMALIE"


class TypeConsentement(str, Enum):
    AFFILIATION_LARGE = "AFFILIATION_LARGE"
    NOTIFICATION_ACTE = "NOTIFICATION_ACTE"


class StatutConsentement(str, Enum):
    ACTIF = "ACTIF"
    REVOQUE = "REVOQUE"


class PartieRecours(str, Enum):
    BENEFICIAIRE = "BENEFICIAIRE"
    PRESTATAIRE = "PRESTATAIRE"


class StatutContestation(str, Enum):
    EN_ATTENTE = "EN_ATTENTE"
    CONTRE_EXPERTISE_EN_COURS = "CONTRE_EXPERTISE_EN_COURS"
    TRANCHEE = "TRANCHEE"


class TypeExclusion(str, Enum):
    """Cf. section 6, entite Exclusion_Contrat (ADR-012, risque R8)."""

    ACTE = "ACTE"
    MEDICAMENT = "MEDICAMENT"
    CATEGORIE_ACTE = "CATEGORIE_ACTE"
    PATHOLOGIE_PREEXISTANTE = "PATHOLOGIE_PREEXISTANTE"


class StatutLicence(str, Enum):
    """Cf. section 12.6 -- degradation progressive, jamais coupure seche."""

    ACTIVE = "ACTIVE"
    GRACE = "GRACE"
    DEGRADEE = "DEGRADEE"
    SUSPENDUE = "SUSPENDUE"


class TypeContratLicence(str, Enum):
    ANNUEL = "ANNUEL"
    TRIMESTRIEL = "TRIMESTRIEL"


class ModeleTarifaireLicence(str, Enum):
    FORFAIT = "FORFAIT"
    FORFAIT_PLUS_VOLUME = "FORFAIT_PLUS_VOLUME"


class Locale(str, Enum):
    """Cf. section 13 -- portee retenue : fr/en de base, +ar/pt/es."""

    FR = "fr"
    EN = "en"
    AR = "ar"
    PT = "pt"
    ES = "es"


class FormatSource(str, Enum):
    JSON = "JSON"
    CSV = "CSV"
    EXCEL = "EXCEL"
    XML = "XML"
    PDF = "PDF"


class CanalSoumission(str, Enum):
    API = "API"
    PORTAIL_UPLOAD = "PORTAIL_UPLOAD"


class StatutLot(str, Enum):
    """Cf. section 14 -- soumission groupee."""

    RECU = "RECU"
    EN_TRAITEMENT = "EN_TRAITEMENT"
    TRAITE_PARTIEL = "TRAITE_PARTIEL"
    TRAITE_COMPLET = "TRAITE_COMPLET"


class ConfigurePar(str, Enum):
    EQUIPE_FHTP = "EQUIPE_FHTP"
    CENTRE = "CENTRE"


class TypeActePEC(str, Enum):
    """Cf. section 15.3 -- Modele_Document_Payeur."""

    HOSPITALISATION = "HOSPITALISATION"
    ANALYSE_BIOLOGIQUE = "ANALYSE_BIOLOGIQUE"
    IMAGERIE = "IMAGERIE"
    PHARMACIE_TPC = "PHARMACIE_TPC"
    KINESITHERAPIE = "KINESITHERAPIE"
    LUNETTERIE = "LUNETTERIE"
    AUTRE = "AUTRE"


class TypeDocumentPayeur(str, Enum):
    PEC_STANDARD = "PEC_STANDARD"
    PEC_URGENCE = "PEC_URGENCE"
    TPC = "TPC"
    AUTRE = "AUTRE"


class StatutPEC(str, Enum):
    EN_ATTENTE = "EN_ATTENTE"
    ACCORDE = "ACCORDE"
    REFUSE = "REFUSE"
    EXPIRE = "EXPIRE"
    SILENCE_VAUT_ACCORD = "SILENCE_VAUT_ACCORD"
    EN_ATTENTE_VERIFICATION_SCAN = "EN_ATTENTE_VERIFICATION_SCAN"  # section 15.4


class TypePEC(str, Enum):
    STANDARD = "STANDARD"
    URGENCE = "URGENCE"
    CHRONIQUE_TPC = "CHRONIQUE_TPC"


class EventType(str, Enum):
    """Cf. section 2.4 -- Journal de Conformite, append-only."""

    SOUMISSION = "SOUMISSION"
    REGLE_APPLIQUEE = "REGLE_APPLIQUEE"
    PEC_DEMANDEE = "PEC_DEMANDEE"
    DECISION = "DECISION"
    PAIEMENT = "PAIEMENT"
    REJET = "REJET"
    SYNC = "SYNC"


class StatutEligibilite(str, Enum):
    """Cf. section 3.1 -- IConnecteurPayeur.verifier_eligibilite."""

    ACTIF = "ACTIF"
    SUSPENDU = "SUSPENDU"
    DROITS_FERMES = "DROITS_FERMES"
    INCONNU = "INCONNU"


class CodeAMU(str, Enum):
    """R / E / TPC -- codes des conventions INAM 2012 (FHTP-KNO-001, glossaire)."""

    R = "R"
    E = "E"
    TPC = "TPC"


class StatutBaseRemboursement(str, Enum):
    """Cf. section 3.1 -- IConnecteurPayeur.obtenir_base_remboursement.
    Etend CodeAMU du seul NON_COUVERT, necessaire quand l'acte ou le
    medicament interroge n'est pas dans le referentiel du payeur."""

    R = "R"
    E = "E"
    TPC = "TPC"
    NON_COUVERT = "NON_COUVERT"


class StatutSoumissionFacture(str, Enum):
    """Cf. section 3.1 -- IConnecteurPayeur.soumettre_facture."""

    ACCEPTE = "ACCEPTE"
    REJETE = "REJETE"
    EN_ATTENTE = "EN_ATTENTE"
