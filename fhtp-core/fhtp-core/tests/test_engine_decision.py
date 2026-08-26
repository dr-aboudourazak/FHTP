"""Tests du moteur de decision -- FHTP-ARC-001, section 2.1 et ADR-003.

Le test le plus important de ce fichier est test_mode_degrade_jamais_fast_track :
c'est la regle de securite qui corrige la faille identifiee a la relecture de
l'architecture (section 7.2). Elle doit rester vraie meme si le reste de la
logique de decision change -- d'ou un test dedie, independant des autres.
"""

from datetime import date, datetime

import pytest

from fhtp_core.engine.decision import decider, peut_recevoir_fast_track
from fhtp_core.models.dossier import Dossier
from fhtp_core.models.enums import (
    CircuitRemboursement,
    DecisionFinale,
    OrigineCreation,
    Pilier,
    StatutDossier,
    StatutPilier,
    TypeScenario,
)


def _dossier(*, origine: OrigineCreation, piliers: dict[Pilier, StatutPilier]) -> Dossier:
    return Dossier(
        id_dossier="DOS-2026-000042",
        type_scenario=TypeScenario.CONSULTATION,
        id_beneficiaire="BEN-001",
        id_formation="FS-001",
        id_contrat_payeur="CTR-001",
        circuit_remboursement=CircuitRemboursement.AMU_SEUL,
        date_soins=date(2026, 8, 25),
        date_soumission=datetime(2026, 8, 25, 10, 0, 0),
        origine_creation=origine,
        evaluation_piliers=piliers,
    )


class TestReglesSecuriteADR003:
    """Cf. ADR-003 : aucun FAST_TRACK avant reevaluation en ligne."""

    def test_mode_degrade_jamais_fast_track_meme_si_tout_conforme(self) -> None:
        """Le cas critique : TOUS les piliers CONFORME, mais origine
        MODE_DEGRADE -- doit plafonner a EN_VALIDATION_LOCALE, jamais
        FAST_TRACK. C'est exactement le scenario d'exploitation decrit en
        section 7.2 (coupure reseau provoquee)."""
        d = _dossier(
            origine=OrigineCreation.MODE_DEGRADE,
            piliers={
                Pilier.COMPLETUDE_ADMINISTRATIVE: StatutPilier.CONFORME,
                Pilier.COHERENCE_REGIME: StatutPilier.CONFORME,
                Pilier.COHERENCE_TARIFAIRE: StatutPilier.CONFORME,
                Pilier.COHERENCE_DOCUMENTAIRE: StatutPilier.CONFORME,
                Pilier.COHERENCE_PRESCRIPTEUR: StatutPilier.CONFORME,
                Pilier.COHERENCE_GRAPHIQUE: StatutPilier.NON_EVALUE,
            },
        )
        assert decider(d) == StatutDossier.EN_VALIDATION_LOCALE
        assert peut_recevoir_fast_track(d) is False

    def test_mode_degrade_avec_anomalie_reste_en_validation_locale(self) -> None:
        """Meme avec une anomalie, le statut reste EN_VALIDATION_LOCALE en
        mode degrade -- pas AUDIT_APPROFONDI. La reevaluation en ligne
        decidera de la suite reelle a la reconnexion (section 7.2)."""
        d = _dossier(
            origine=OrigineCreation.MODE_DEGRADE,
            piliers={Pilier.COHERENCE_DOCUMENTAIRE: StatutPilier.ANOMALIE},
        )
        assert decider(d) == StatutDossier.EN_VALIDATION_LOCALE

    def test_en_ligne_tout_conforme_donne_fast_track(self) -> None:
        """Le meme dossier, mais cree EN_LIGNE, doit pouvoir atteindre
        FAST_TRACK -- confirme que le garde-fou ne bloque QUE le mode
        degrade, pas le fonctionnement normal."""
        d = _dossier(
            origine=OrigineCreation.EN_LIGNE,
            piliers={
                Pilier.COMPLETUDE_ADMINISTRATIVE: StatutPilier.CONFORME,
                Pilier.COHERENCE_REGIME: StatutPilier.CONFORME,
            },
        )
        assert decider(d) == DecisionFinale.FAST_TRACK
        assert peut_recevoir_fast_track(d) is True


class TestLogiqueDecisionStandard:
    """Cf. section 2.1 -- logique de decision (dossiers EN_LIGNE)."""

    @pytest.mark.parametrize(
        "piliers,attendu",
        [
            pytest.param(
                {Pilier.COMPLETUDE_ADMINISTRATIVE: StatutPilier.CONFORME},
                DecisionFinale.FAST_TRACK,
                id="tout_conforme",
            ),
            pytest.param(
                {Pilier.COHERENCE_TARIFAIRE: StatutPilier.A_VERIFIER},
                DecisionFinale.CONTROLE_RAPIDE,
                id="un_a_verifier_sans_anomalie",
            ),
            pytest.param(
                {Pilier.COHERENCE_DOCUMENTAIRE: StatutPilier.ANOMALIE},
                DecisionFinale.AUDIT_APPROFONDI,
                id="une_anomalie",
            ),
            pytest.param(
                {
                    Pilier.COHERENCE_TARIFAIRE: StatutPilier.A_VERIFIER,
                    Pilier.COHERENCE_DOCUMENTAIRE: StatutPilier.ANOMALIE,
                },
                DecisionFinale.AUDIT_APPROFONDI,
                id="anomalie_prime_sur_a_verifier",
            ),
        ],
    )
    def test_decision_selon_statuts_piliers(
        self, piliers: dict[Pilier, StatutPilier], attendu: DecisionFinale
    ) -> None:
        d = _dossier(origine=OrigineCreation.EN_LIGNE, piliers=piliers)
        assert decider(d) == attendu
