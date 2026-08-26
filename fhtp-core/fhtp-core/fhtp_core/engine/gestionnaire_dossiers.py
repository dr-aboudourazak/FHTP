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
"""

from __future__ import annotations

from fhtp_core.engine.decision import decider
from fhtp_core.engine.journal import JournalConformite
from fhtp_core.engine.moteur_regles import evaluer_dossier
from fhtp_core.models.dossier import Dossier
from fhtp_core.models.enums import (
    DecisionFinale,
    EventType,
    OrigineCreation,
    StatutDossier,
)
from fhtp_core.rules.models import Regle

_CORRESPONDANCE_DECISION_STATUT = {
    DecisionFinale.FAST_TRACK: StatutDossier.FAST_TRACK,
    DecisionFinale.CONTROLE_RAPIDE: StatutDossier.CONTROLE_RAPIDE,
    DecisionFinale.AUDIT_APPROFONDI: StatutDossier.AUDIT,
}


class GestionnaireDossiers:
    def __init__(self, regles: list[Regle], journal: JournalConformite) -> None:
        self._regles = regles
        self._journal = journal

    def soumettre(self, dossier: Dossier, operateur_id: str) -> Dossier:
        """Fait passer un dossier par le cycle complet : soumission,
        evaluation des six piliers, decision finale. Retourne une nouvelle
        instance de Dossier (jamais de mutation en place)."""
        dossier = dossier.model_copy(update={"statut": StatutDossier.SOUMIS})
        self._journal.enregistrer(
            id_dossier=dossier.id_dossier,
            event_type=EventType.SOUMISSION,
            resultat=f"Dossier soumis (origine={dossier.origine_creation.value})",
            operateur_id=operateur_id,
        )

        dossier = dossier.model_copy(update={"statut": StatutDossier.EN_VALIDATION})
        dossier = evaluer_dossier(dossier, self._regles)

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
