"""Tests des regles ajoutees le 28 aout 2026 (lot 5) -- RP24-18, RP24-19,
RP24-21.
"""

from datetime import date, datetime

import pytest

from fhtp_core.engine.moteur_regles import evaluer_dossier
from fhtp_core.models.dossier import ActeRealise, Dossier, MedicamentPrescrit
from fhtp_core.models.enums import (
    CircuitRemboursement,
    Pilier,
    StatutPilier,
    TypeScenario,
    VoieAdministration,
)
from fhtp_core.rules.loader import charger_regles


@pytest.fixture(scope="module")
def regles():
    return charger_regles()


def _dossier(**overrides) -> Dossier:
    base = dict(
        id_dossier="DOS-2026-001200",
        type_scenario=TypeScenario.CONSULTATION,
        id_beneficiaire="BEN-001",
        id_formation="FS-001",
        id_contrat_payeur="CTR-001",
        circuit_remboursement=CircuitRemboursement.AMU_SEUL,
        date_soins=date(2026, 8, 28),
        date_soumission=datetime(2026, 8, 28, 10, 0, 0),
    )
    base.update(overrides)
    return Dossier(**base)


def _acte(**overrides) -> ActeRealise:
    base = dict(
        id_acte="ACT-1200",
        id_dossier="DOS-2026-001200",
        id_prescripteur="PRE-001",
        code_acte="C",
        diagnostic_cim10="J06.9",
        date_realisation=date(2026, 8, 28),
        montant_facture=7000,
    )
    base.update(overrides)
    return ActeRealise(**base)


class TestChargeurLot5:
    def test_regles_chargees(self, regles) -> None:
        ids = {r.id for r in regles}
        for id_attendu in ["RP24-18", "RP24-19", "RP24-21"]:
            assert id_attendu in ids, f"{id_attendu} absente"

    def test_toujours_aucun_doublon(self, regles) -> None:
        ids = [r.id for r in regles]
        assert len(ids) == len(set(ids))


class TestDemandeTPCReserveeMedecins:
    """RP24-18."""

    def test_demande_tpc_par_non_medecin_est_anomalie(self, regles) -> None:
        d = _dossier(
            demande_tpc=True,
            actes=[_acte(prescripteur_est_medecin=False)],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == StatutPilier.ANOMALIE

    def test_demande_tpc_par_medecin_est_conforme(self, regles) -> None:
        d = _dossier(
            demande_tpc=True,
            actes=[_acte(prescripteur_est_medecin=True)],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == StatutPilier.CONFORME

    def test_pas_de_demande_tpc_ne_declenche_rien(self, regles) -> None:
        d = _dossier(
            demande_tpc=False,
            actes=[_acte(prescripteur_est_medecin=False)],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == StatutPilier.CONFORME


class TestDelivranceTPCSansAttestation:
    """RP24-19."""

    def test_necessite_tpc_sans_pec_est_anomalie(self, regles) -> None:
        d = _dossier(
            type_scenario=TypeScenario.PHARMACIE,
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-1200",
                    id_dossier="DOS-2026-001200",
                    dci="INSULINE",
                    voie_administration=VoieAdministration.PARENTERALE,
                    duree_traitement_jours=30,
                    quantite=1,
                    prix_unitaire_facture=15000,
                    necessite_tpc=True,
                    pec_id=None,
                )
            ],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.ANOMALIE

    def test_necessite_tpc_avec_attestation_est_conforme(self, regles) -> None:
        d = _dossier(
            type_scenario=TypeScenario.PHARMACIE,
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-1201",
                    id_dossier="DOS-2026-001200",
                    dci="INSULINE",
                    voie_administration=VoieAdministration.PARENTERALE,
                    duree_traitement_jours=30,
                    quantite=1,
                    prix_unitaire_facture=15000,
                    necessite_tpc=True,
                    pec_id="TPC-2026-001",
                )
            ],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.CONFORME


class TestKinesitherapieNecessitePrescriptionMedicale:
    """RP24-21."""

    def test_kine_sans_prescripteur_medecin_est_anomalie(self, regles) -> None:
        d = _dossier(
            actes=[_acte(necessite_prescription_medicale=True, prescripteur_est_medecin=False)]
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == StatutPilier.ANOMALIE

    def test_kine_avec_prescripteur_medecin_est_conforme(self, regles) -> None:
        d = _dossier(
            actes=[_acte(necessite_prescription_medicale=True, prescripteur_est_medecin=True)]
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == StatutPilier.CONFORME

    def test_acte_non_concerne_ne_declenche_rien(self, regles) -> None:
        d = _dossier(actes=[_acte(necessite_prescription_medicale=False)])
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == StatutPilier.CONFORME
