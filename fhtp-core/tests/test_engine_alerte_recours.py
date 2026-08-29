"""Tests de l'alerte recours -- R-TG-009 (section 2.2).

Avant cette correction, `Dossier.alerte_recours` restait a sa valeur par
defaut (active=False) quel que soit le resultat, malgre l'exigence
explicite de la section 2.2 : "Tout rejet declenche la generation
automatique d'une notification de rejet motivee par ecrit [...] ainsi
qu'une alerte recours."
"""

from datetime import date, datetime

import pytest

from fhtp_core.engine.gestionnaire_dossiers import GestionnaireDossiers
from fhtp_core.engine.journal import JournalConformite
from fhtp_core.models.dossier import ActeRealise, Dossier
from fhtp_core.models.enums import (
    CircuitRemboursement,
    StatutDossier,
    TypeScenario,
)
from fhtp_core.rules.loader import charger_regles


@pytest.fixture
def gestionnaire():
    return GestionnaireDossiers(regles=charger_regles(), journal=JournalConformite())


def _dossier(**overrides) -> Dossier:
    base = dict(
        id_dossier="DOS-2026-001100",
        type_scenario=TypeScenario.CONSULTATION,
        id_beneficiaire="BEN-001",
        id_formation="FS-001",
        id_contrat_payeur="CTR-001",
        circuit_remboursement=CircuitRemboursement.AMU_SEUL,
        date_soins=date(2026, 8, 28),
        date_soumission=datetime(2026, 8, 28, 10, 0, 0),
        cloture_triple_trait=True,
    )
    base.update(overrides)
    return Dossier(**base)


class TestAlerteRecoursDeclenchee:
    def test_dossier_avec_anomalie_declenche_l_alerte(self, gestionnaire) -> None:
        d = _dossier(
            actes=[
                ActeRealise(
                    id_acte="ACT-1100",
                    id_dossier="DOS-2026-001100",
                    id_prescripteur="PRE-001",
                    code_acte="C",
                    diagnostic_cim10="R68",
                    date_realisation=date(2026, 8, 28),
                    montant_facture=7000,
                )
            ]
        )
        resultat = gestionnaire.soumettre(d, operateur_id="OP-001")
        assert resultat.statut == StatutDossier.AUDIT
        assert resultat.alerte_recours.active is True
        assert resultat.alerte_recours.regime == "AMU"
        assert resultat.alerte_recours.delai_indicatif is not None
        assert resultat.alerte_recours.action_recommandee is not None

    def test_alerte_indique_le_bon_regime_pour_amu_plus_prive(self, gestionnaire) -> None:
        d = _dossier(
            circuit_remboursement=CircuitRemboursement.AMU_PLUS_PRIVE,
            actes=[
                ActeRealise(
                    id_acte="ACT-1101",
                    id_dossier="DOS-2026-001100",
                    id_prescripteur="PRE-001",
                    code_acte="C",
                    diagnostic_cim10="R68",
                    date_realisation=date(2026, 8, 28),
                    montant_facture=7000,
                )
            ],
        )
        resultat = gestionnaire.soumettre(d, operateur_id="OP-001")
        assert resultat.alerte_recours.regime == "MIXTE"

    def test_alerte_indique_cat_pour_prive_seul(self, gestionnaire) -> None:
        d = _dossier(
            circuit_remboursement=CircuitRemboursement.PRIVE_SEUL,
            actes=[
                ActeRealise(
                    id_acte="ACT-1102",
                    id_dossier="DOS-2026-001100",
                    id_prescripteur="PRE-001",
                    code_acte="C",
                    diagnostic_cim10="R68",
                    date_realisation=date(2026, 8, 28),
                    montant_facture=7000,
                )
            ],
        )
        resultat = gestionnaire.soumettre(d, operateur_id="OP-001")
        assert resultat.alerte_recours.regime == "CAT"


class TestAlerteRecoursNonDeclencheeSiPasNecessaire:
    def test_dossier_conforme_n_a_pas_d_alerte_active(self, gestionnaire) -> None:
        d = _dossier(
            actes=[
                ActeRealise(
                    id_acte="ACT-1103",
                    id_dossier="DOS-2026-001100",
                    id_prescripteur="PRE-001",
                    code_acte="C",
                    diagnostic_cim10="J06.9",
                    date_realisation=date(2026, 8, 28),
                    montant_facture=7000,
                )
            ]
        )
        resultat = gestionnaire.soumettre(d, operateur_id="OP-001")
        assert resultat.statut == StatutDossier.FAST_TRACK
        assert resultat.alerte_recours.active is False

    def test_dossier_a_verifier_n_a_pas_d_alerte_active(self, gestionnaire) -> None:
        """Cf. section 2.2 : l'alerte recours concerne le rejet/l'audit, pas
        le controle rapide, qui a son propre mecanisme de notification
        distinct (delai de regularisation)."""
        from fhtp_core.models.dossier import MedicamentPrescrit
        from fhtp_core.models.enums import VoieAdministration

        d = _dossier(
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-1100",
                    id_dossier="DOS-2026-001100",
                    dci="MOLECULE_HORS_LISTE",
                    voie_administration=VoieAdministration.ORALE,
                    duree_traitement_jours=5,
                    quantite=1,
                    prix_unitaire_facture=3000,
                    enrole_presta_plus=False,
                )
            ]
        )
        resultat = gestionnaire.soumettre(d, operateur_id="OP-001")
        assert resultat.statut == StatutDossier.CONTROLE_RAPIDE
        assert resultat.alerte_recours.active is False
