"""Gestionnaire de Dossiers -- FHTP-ARC-001, section 2.2.

Orchestre le cycle de vie complet d'un dossier :

    SOUMIS -> EN_VALIDATION -> [FAST_TRACK | CONTROLE_RAPIDE | AUDIT | EN_VALIDATION_LOCALE]

Chaque transition d'etat est horodatee et enregistree dans le Journal de
Conformite (section 2.4). C'est le seul point d'entree cense etre utilise en
pratique : il assemble le referentiel de regles (fhtp_core.rules), le moteur
d'evaluation (fhtp_core.engine.moteur_regles) et le moteur de decision
(fhtp_core.engine.decision) plutot que de les laisser appeles separement --
ce qui garantit que la regle de securite ADR-003 est systematiquement
respectee, sans dependre de la discipline de chaque appelant.

`soumettre_avec_verification_payeur` est le point d'entree qui interroge
reellement un IConnecteurPayeur (section 3.1) avant d'evaluer le dossier --
c'est ici que ConnecteurIndisponible declenche effectivement le Mode Degrade
(section 7), et que le statut d'eligibilite (section 10.1 : SUSPENDU/
DROITS_FERMES -> ANOMALIE, INCONNU -> A_VERIFIER) et la validite reelle
d'une PEC (F7, section 8.2 -- jamais sur la seule presence d'un numero)
s'integrent au resultat des six piliers.

Resout aussi, quand des registres sont fournis a la construction, les
jointures Prescripteur/FormationSanitaire (`_enrichir_dossier`) -- pour que
des regles comme R-TG-021 (restriction paramedicale) et RG-H11 (clinique
privee) reposent sur une resolution reelle plutot que sur des champs
precalcules fournis sans garantie par l'appelant. Reste retro-compatible :
sans registre fourni, le comportement precedent (champs precalcules
directement sur le Dossier) continue de fonctionner a l'identique.
"""

from __future__ import annotations

from fhtp_core.connectors.exceptions import ConnecteurIndisponible
from fhtp_core.connectors.payeur import IConnecteurPayeur
from fhtp_core.engine.decision import decider
from fhtp_core.engine.journal import JournalConformite
from fhtp_core.engine.moteur_regles import evaluer_dossier
from fhtp_core.engine.referentiels import RegistreFormationsSanitaires, RegistrePrescripteurs
from fhtp_core.models.dossier import Dossier
from fhtp_core.models.enums import (
    DecisionFinale,
    EventType,
    OrigineCreation,
    Pilier,
    StatutDossier,
    StatutEligibilite,
    StatutPEC,
    StatutPilier,
    TypeFormationSanitaire,
    TypePrescripteur,
)
from fhtp_core.rules.models import Regle
from fhtp_core.rules.referentiel_molecules_proscrites import molecule_est_proscrite_paramedical

_CORRESPONDANCE_DECISION_STATUT = {
    DecisionFinale.FAST_TRACK: StatutDossier.FAST_TRACK,
    DecisionFinale.CONTROLE_RAPIDE: StatutDossier.CONTROLE_RAPIDE,
    DecisionFinale.AUDIT_APPROFONDI: StatutDossier.AUDIT,
}

# Ordre de severite pour combiner un statut de pilier deja calcule par les
# regles avec une verification externe (eligibilite, PEC) -- le plus severe
# l'emporte toujours, jamais l'inverse.
_SEVERITE_PILIER = {
    StatutPilier.ANOMALIE: 3,
    StatutPilier.A_VERIFIER: 2,
    StatutPilier.CONFORME: 1,
    StatutPilier.NON_EVALUE: 0,
}


def _combiner_statuts(a: StatutPilier, b: StatutPilier) -> StatutPilier:
    return a if _SEVERITE_PILIER[a] >= _SEVERITE_PILIER[b] else b


class GestionnaireDossiers:
    def __init__(
        self,
        regles: list[Regle],
        journal: JournalConformite,
        *,
        registre_prescripteurs: RegistrePrescripteurs | None = None,
        registre_formations: RegistreFormationsSanitaires | None = None,
    ) -> None:
        self._regles = regles
        self._journal = journal
        self._registre_prescripteurs = registre_prescripteurs
        self._registre_formations = registre_formations

    def _enrichir_dossier(self, dossier: Dossier) -> Dossier:
        """Resout reellement les jointures Prescripteur/FormationSanitaire
        quand les registres correspondants sont fournis, plutot que de
        dependre uniquement de champs precalcules par l'appelant.

        La proscription d'une molecule (molecule_est_proscrite_paramedical)
        est une propriete fixe de la DCI, pas de l'appelant -- elle est
        toujours recalculee, meme sans registre de prescripteurs, puisque
        cette table de reference ne depend d'aucun etat externe.

        Le type de prescripteur (paramedical, medecin, specialiste ou non)
        et le type de formation (clinique privee ou non) ne sont recalcules
        QUE si le registre correspondant est fourni ET que la reference
        existe -- sinon, la valeur deja presente sur le Dossier (champ
        precalcule fourni par l'appelant, potentiellement None) est
        conservee telle quelle. Ca permet a l'ancien mode de fonctionnement
        (sans registre) de continuer a fonctionner a l'identique.
        """
        nouveaux_medicaments = []
        for medicament in dossier.medicaments:
            mise_a_jour: dict = {
                "molecule_proscrite_paramedical": molecule_est_proscrite_paramedical(medicament.dci)
            }
            if self._registre_prescripteurs is not None and medicament.id_prescripteur:
                prescripteur = self._registre_prescripteurs.obtenir(medicament.id_prescripteur)
                if prescripteur is not None:
                    mise_a_jour["prescripteur_paramedical"] = (
                        prescripteur.type_prescripteur == TypePrescripteur.PARAMEDICAL
                    )
                    mise_a_jour["prescripteur_rattache_formation"] = (
                        dossier.id_formation in prescripteur.structures_rattachement
                    )
            nouveaux_medicaments.append(medicament.model_copy(update=mise_a_jour))

        nouveaux_actes = []
        for acte in dossier.actes:
            mise_a_jour_acte: dict = {}
            if self._registre_prescripteurs is not None and acte.id_prescripteur:
                prescripteur = self._registre_prescripteurs.obtenir(acte.id_prescripteur)
                if prescripteur is not None:
                    mise_a_jour_acte["prescripteur_est_medecin"] = (
                        prescripteur.type_prescripteur == TypePrescripteur.MEDECIN
                    )
                    mise_a_jour_acte["prescripteur_est_specialiste"] = bool(
                        prescripteur.type_prescripteur == TypePrescripteur.MEDECIN
                        and prescripteur.specialite_declaree
                    )
                    mise_a_jour_acte["prescripteur_rattache_formation"] = (
                        dossier.id_formation in prescripteur.structures_rattachement
                    )
            nouveaux_actes.append(
                acte.model_copy(update=mise_a_jour_acte) if mise_a_jour_acte else acte
            )

        mise_a_jour_dossier: dict = {"medicaments": nouveaux_medicaments, "actes": nouveaux_actes}
        if self._registre_formations is not None:
            formation = self._registre_formations.obtenir(dossier.id_formation)
            if formation is not None:
                mise_a_jour_dossier["structure_est_clinique_privee"] = (
                    formation.type == TypeFormationSanitaire.CLINIQUE_PRIVEE
                )

        return dossier.model_copy(update=mise_a_jour_dossier)

    def soumettre(
        self,
        dossier: Dossier,
        operateur_id: str,
        verifications_externes: list[tuple[Pilier, StatutPilier, str]] | None = None,
    ) -> Dossier:
        """Fait passer un dossier par le cycle complet : soumission,
        evaluation des six piliers, decision finale. Retourne une nouvelle
        instance de Dossier (jamais de mutation en place).

        `verifications_externes` permet d'injecter le resultat d'une
        verification faite hors du referentiel de regles (eligibilite
        payeur, validite reelle d'une PEC) -- utilise par
        `soumettre_avec_verification_payeur`, pas destine a un appel manuel
        direct dans le cas general.
        """
        dossier = dossier.model_copy(update={"statut": StatutDossier.SOUMIS})
        self._journal.enregistrer(
            id_dossier=dossier.id_dossier,
            event_type=EventType.SOUMISSION,
            resultat=f"Dossier soumis (origine={dossier.origine_creation.value})",
            operateur_id=operateur_id,
        )

        dossier = dossier.model_copy(update={"statut": StatutDossier.EN_VALIDATION})
        dossier = self._enrichir_dossier(dossier)
        dossier = evaluer_dossier(dossier, self._regles)

        if verifications_externes:
            piliers = dict(dossier.evaluation_piliers)
            motifs = list(dossier.motifs_rejet)
            for pilier, statut, motif in verifications_externes:
                piliers[pilier] = _combiner_statuts(
                    piliers.get(pilier, StatutPilier.NON_EVALUE), statut
                )
                motifs.append(motif)
            dossier = dossier.model_copy(update={"evaluation_piliers": piliers, "motifs_rejet": motifs})

        for pilier, statut in dossier.evaluation_piliers.items():
            self._journal.enregistrer(
                id_dossier=dossier.id_dossier,
                event_type=EventType.REGLE_APPLIQUEE,
                resultat=f"{pilier.value}={statut.value}",
                operateur_id=operateur_id,
            )

        resultat_decision = decider(dossier)

        if resultat_decision == StatutDossier.EN_VALIDATION_LOCALE:
            # Garde-fou ADR-003 (section 7.2) : jamais de decision_finale
            # posee pour un dossier MODE_DEGRADE, seulement ce statut plafond.
            dossier = dossier.model_copy(update={"statut": StatutDossier.EN_VALIDATION_LOCALE})
        else:
            dossier = dossier.model_copy(
                update={
                    "statut": _CORRESPONDANCE_DECISION_STATUT[resultat_decision],
                    "decision_finale": resultat_decision,
                }
            )

        self._journal.enregistrer(
            id_dossier=dossier.id_dossier,
            event_type=EventType.DECISION,
            resultat=dossier.statut.value,
            operateur_id=operateur_id,
        )
        return dossier

    def soumettre_avec_verification_payeur(
        self, dossier: Dossier, connecteur: IConnecteurPayeur, operateur_id: str
    ) -> Dossier:
        """Point d'entree complet : interroge reellement le connecteur
        payeur avant d'evaluer le dossier (section 10.1).

        - `ConnecteurIndisponible` (a n'importe quel moment de cette
          methode) -> bascule immediate en Mode Degrade (section 7), via le
          chemin normal de `soumettre()` qui sait deja plafonner un dossier
          MODE_DEGRADE a EN_VALIDATION_LOCALE (ADR-003).
        - Eligibilite SUSPENDU/DROITS_FERMES -> pilier COHERENCE_REGIME force
          a ANOMALIE (section 10.1).
        - Eligibilite INCONNU -> pilier COHERENCE_REGIME force a A_VERIFIER,
          "continuer avec cache" (section 10.1).
        - Chaque PEC referencee par une ligne du dossier (acte ou
          medicament) est verifiee aupres du payeur -- jamais sur la seule
          presence d'un numero au bon format (F7, section 8.2). Une PEC non
          confirmee ACCORDE force le pilier COMPLETUDE_ADMINISTRATIVE a
          ANOMALIE.
        """
        try:
            eligibilite = connecteur.verifier_eligibilite(dossier.id_beneficiaire, dossier.date_soins)
        except ConnecteurIndisponible:
            return self._basculer_mode_degrade(
                dossier, operateur_id, motif="Connecteur payeur indisponible (verification eligibilite)"
            )

        verifications: list[tuple[Pilier, StatutPilier, str]] = []

        if eligibilite.statut in (StatutEligibilite.SUSPENDU, StatutEligibilite.DROITS_FERMES):
            verifications.append(
                (
                    Pilier.COHERENCE_REGIME,
                    StatutPilier.ANOMALIE,
                    f"Eligibilite payeur : {eligibilite.statut.value}",
                )
            )
        elif eligibilite.statut == StatutEligibilite.INCONNU:
            verifications.append(
                (
                    Pilier.COHERENCE_REGIME,
                    StatutPilier.A_VERIFIER,
                    "Eligibilite payeur inconnue -- a verifier",
                )
            )
        # ACTIF -> rien a ajouter, le dossier suit son cours normal.

        for pec_id in self._pec_ids_references(dossier):
            try:
                statut_pec = connecteur.verifier_pec(pec_id)
            except ConnecteurIndisponible:
                return self._basculer_mode_degrade(
                    dossier, operateur_id, motif=f"Connecteur payeur indisponible (verification PEC {pec_id})"
                )
            if statut_pec not in (StatutPEC.ACCORDE, StatutPEC.SILENCE_VAUT_ACCORD):
                verifications.append(
                    (
                        Pilier.COMPLETUDE_ADMINISTRATIVE,
                        StatutPilier.ANOMALIE,
                        f"PEC {pec_id} non confirmee aupres du payeur (statut={statut_pec.value})",
                    )
                )

        return self.soumettre(dossier, operateur_id, verifications_externes=verifications)

    def _basculer_mode_degrade(self, dossier: Dossier, operateur_id: str, *, motif: str) -> Dossier:
        self._journal.enregistrer(
            id_dossier=dossier.id_dossier,
            event_type=EventType.SYNC,
            resultat=f"Bascule Mode Degrade : {motif}",
            operateur_id=operateur_id,
        )
        dossier_degrade = dossier.model_copy(update={"origine_creation": OrigineCreation.MODE_DEGRADE})
        return self.soumettre(dossier_degrade, operateur_id)

    @staticmethod
    def _pec_ids_references(dossier: Dossier) -> set[str]:
        ids: set[str] = set()
        for acte in dossier.actes:
            if acte.pec_id:
                ids.add(acte.pec_id)
        for medicament in dossier.medicaments:
            if medicament.pec_id:
                ids.add(medicament.pec_id)
        return ids

    def resynchroniser(self, dossier: Dossier, operateur_id: str) -> Dossier:
        """Reevalue en ligne un dossier cree en MODE_DEGRADE -- section 7.2.

        C'est le SEUL chemin par lequel un tel dossier peut atteindre
        FAST_TRACK : jamais directement via soumettre(), toujours en
        repassant explicitement par resynchroniser() une fois la connexion
        retablie et les donnees a jour reconfirmees (carte active, PEC
        valide, etc. -- la reconfirmation elle-meme est a la charge de
        l'appelant, via les connecteurs payeurs, avant d'appeler cette
        methode).
        """
        if dossier.origine_creation != OrigineCreation.MODE_DEGRADE:
            raise ValueError(
                "resynchroniser() ne s'applique qu'a un dossier "
                "origine_creation=MODE_DEGRADE ; celui-ci est deja EN_LIGNE."
            )

        dossier_reconnecte = dossier.model_copy(update={"origine_creation": OrigineCreation.EN_LIGNE})
        dossier_reevalue = self.soumettre(dossier_reconnecte, operateur_id)

        self._journal.enregistrer(
            id_dossier=dossier.id_dossier,
            event_type=EventType.SYNC,
            resultat=f"Resynchronise depuis MODE_DEGRADE -> {dossier_reevalue.statut.value}",
            operateur_id=operateur_id,
        )
        return dossier_reevalue
