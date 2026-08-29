"""Tests du Gestionnaire de Dossiers -- section 2.2.

Le scenario le plus important ici (TestCycleModeDegrade) rejoue de bout en
bout, via le gestionnaire complet plutot qu'en appelant les moteurs
separement, le scenario d'exploitation decrit en section 7.2 : un dossier
degrade avec tous les piliers conformes ne doit jamais atteindre FAST_TRACK
via soumettre(), seulement via resynchroniser().
"""

from datetime import date, datetime

import pytest

from fhtp_core.engine.gestionnaire_dossiers import GestionnaireDossiers
from fhtp_core.engine.journal import JournalConformite
from fhtp_core.models.dossier import ActeRealise, Dossier
from fhtp_core.models.enums import (
    CircuitRemboursement,
    EventType,
    OrigineCreation,
    StatutDossier,
    TypeScenario,
)
from fhtp_core.rules.loader import charger_regles


@pytest.fixture
def gestionnaire():
    return GestionnaireDossiers(regles=charger_regles(), journal=JournalConformite())


def _dossier_conforme(*, origine: OrigineCreation, id_dossier: str = "DOS-2026-000200") -> Dossier:
    return Dossier(
        id_dossier=id_dossier,
        type_scenario=TypeScenario.CONSULTATION,
        id_beneficiaire="BEN-001",
        id_formation="FS-001",
        id_contrat_payeur="CTR-001",
        circuit_remboursement=CircuitRemboursement.AMU_SEUL,
        date_soins=date(2026, 8, 25),
        date_soumission=datetime(2026, 8, 25, 10, 0, 0),
        origine_creation=origine,
        cloture_triple_trait=True,
        actes=[
            ActeRealise(
                id_acte="ACT-100",
                id_dossier=id_dossier,
                id_prescripteur="PRE-001",
                code_acte="C",
                diagnostic_cim10="J06.9",
                date_realisation=date(2026, 8, 25),
                montant_facture=7000,
            )
        ],
    )


class TestCycleDeVieNormal:
    def test_dossier_conforme_en_ligne_atteint_fast_track(self, gestionnaire) -> None:
        d = _dossier_conforme(origine=OrigineCreation.EN_LIGNE)
        resultat = gestionnaire.soumettre(d, operateur_id="OP-CAB-001")
        assert resultat.statut == StatutDossier.FAST_TRACK

    def test_soumission_produit_des_entrees_de_journal(self, gestionnaire) -> None:
        d = _dossier_conforme(origine=OrigineCreation.EN_LIGNE)
        gestionnaire.soumettre(d, operateur_id="OP-CAB-001")
        historique = gestionnaire._journal.historique_dossier(d.id_dossier)

        types_evenements = [e.event_type for e in historique]
        assert EventType.SOUMISSION in types_evenements
        assert EventType.REGLE_APPLIQUEE in types_evenements
        assert EventType.DECISION in types_evenements

    def test_journal_reste_integre_apres_soumission(self, gestionnaire) -> None:
        d = _dossier_conforme(origine=OrigineCreation.EN_LIGNE)
        gestionnaire.soumettre(d, operateur_id="OP-CAB-001")
        assert gestionnaire._journal.verifier_integrite() is True

    def test_dossier_avec_r68_atteint_audit(self, gestionnaire) -> None:
        d = _dossier_conforme(origine=OrigineCreation.EN_LIGNE)
        d = d.model_copy(
            update={
                "actes": [
                    d.actes[0].model_copy(update={"diagnostic_cim10": "R68"})
                ]
            }
        )
        resultat = gestionnaire.soumettre(d, operateur_id="OP-CAB-001")
        assert resultat.statut == StatutDossier.AUDIT


class TestCycleModeDegrade:
    """Cf. section 7.2, ADR-003 -- le coeur de la garantie anti-fraude."""

    def test_dossier_degrade_conforme_ne_depasse_jamais_en_validation_locale(
        self, gestionnaire
    ) -> None:
        """Meme un dossier parfaitement conforme, cree hors ligne, doit
        s'arreter a EN_VALIDATION_LOCALE -- jamais FAST_TRACK -- tant qu'il
        n'a pas ete resynchronise. C'est le scenario d'exploitation exact
        decrit en section 7.2 (coupure reseau provoquee)."""
        d = _dossier_conforme(origine=OrigineCreation.MODE_DEGRADE)
        resultat = gestionnaire.soumettre(d, operateur_id="OP-CAB-001")

        assert resultat.statut == StatutDossier.EN_VALIDATION_LOCALE
        assert resultat.statut != StatutDossier.FAST_TRACK
        assert resultat.decision_finale is None  # aucune decision finale posee

    def test_resynchroniser_dossier_degrade_conforme_atteint_fast_track(
        self, gestionnaire
    ) -> None:
        """Une fois la reconnexion effectuee, le meme dossier doit pouvoir
        atteindre FAST_TRACK -- confirme que resynchroniser() est bien le
        chemin de sortie prevu, pas un blocage permanent."""
        d = _dossier_conforme(origine=OrigineCreation.MODE_DEGRADE)
        gestionnaire.soumettre(d, operateur_id="OP-CAB-001")  # plafonne en local

        resultat = gestionnaire.resynchroniser(d, operateur_id="OP-CAB-001")
        assert resultat.statut == StatutDossier.FAST_TRACK
        assert resultat.origine_creation == OrigineCreation.EN_LIGNE

    def test_resynchroniser_journalise_l_evenement_sync(self, gestionnaire) -> None:
        d = _dossier_conforme(origine=OrigineCreation.MODE_DEGRADE)
        gestionnaire.resynchroniser(d, operateur_id="OP-CAB-001")
        historique = gestionnaire._journal.historique_dossier(d.id_dossier)
        assert any(e.event_type == EventType.SYNC for e in historique)

    def test_resynchroniser_refuse_un_dossier_deja_en_ligne(self, gestionnaire) -> None:
        d = _dossier_conforme(origine=OrigineCreation.EN_LIGNE)
        with pytest.raises(ValueError):
            gestionnaire.resynchroniser(d, operateur_id="OP-CAB-001")

    def test_dossier_degrade_avec_anomalie_reste_aussi_en_validation_locale(
        self, gestionnaire
    ) -> None:
        """Meme cote 'pire cas' (anomalie reelle) : le statut en mode
        degrade reste EN_VALIDATION_LOCALE, pas AUDIT -- la vraie decision
        n'est prise qu'a la resynchronisation (section 7.2)."""
        d = _dossier_conforme(origine=OrigineCreation.MODE_DEGRADE)
        d = d.model_copy(
            update={"actes": [d.actes[0].model_copy(update={"diagnostic_cim10": "R68"})]}
        )
        resultat = gestionnaire.soumettre(d, operateur_id="OP-CAB-001")
        assert resultat.statut == StatutDossier.EN_VALIDATION_LOCALE

        resultat_sync = gestionnaire.resynchroniser(d, operateur_id="OP-CAB-001")
        assert resultat_sync.statut == StatutDossier.AUDIT
