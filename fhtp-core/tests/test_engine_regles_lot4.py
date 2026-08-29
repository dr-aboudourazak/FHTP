"""Tests des regles ajoutees le 28 aout 2026 (lot 4) -- RP24-09 (acte et
medicament), RP24-04, RP24-13, RP24-23, RP24-27, et le raffinement de
RG-H01 avec l'exception d'urgence (RG-H07).
"""

from datetime import date, datetime

import pytest

from fhtp_core.engine.gestionnaire_dossiers import GestionnaireDossiers
from fhtp_core.engine.journal import JournalConformite
from fhtp_core.engine.moteur_regles import evaluer_dossier
from fhtp_core.engine.referentiels import RegistreFormationsSanitaires, RegistrePrescripteurs
from fhtp_core.models.dossier import ActeRealise, Dossier, MedicamentPrescrit
from fhtp_core.models.enums import (
    CircuitRemboursement,
    Pilier,
    StatutPilier,
    StatutPrescripteur,
    TypePrescripteur,
    TypeScenario,
    VoieAdministration,
)
from fhtp_core.models.identite import Prescripteur
from fhtp_core.rules.loader import charger_regles


@pytest.fixture(scope="module")
def regles():
    return charger_regles()


def _dossier(**overrides) -> Dossier:
    base = dict(
        id_dossier="DOS-2026-001000",
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
        id_acte="ACT-1000",
        id_dossier="DOS-2026-001000",
        id_prescripteur="PRE-001",
        code_acte="C",
        diagnostic_cim10="J06.9",
        date_realisation=date(2026, 8, 28),
        montant_facture=7000,
    )
    base.update(overrides)
    return ActeRealise(**base)


class TestChargeurLot4:
    def test_regles_chargees(self, regles) -> None:
        ids = {r.id for r in regles}
        for id_attendu in [
            "RP24-09-ACTE", "RP24-09-MEDICAMENT", "RP24-04",
            "RP24-13", "RP24-23", "RP24-27",
        ]:
            assert id_attendu in ids, f"{id_attendu} absente"

    def test_toujours_aucun_doublon(self, regles) -> None:
        ids = [r.id for r in regles]
        assert len(ids) == len(set(ids))


class TestExceptionUrgenceRGH01:
    """Raffinement de RG-H01 : la fenetre de grace d'urgence (RG-H07)."""

    def test_non_urgent_sans_pec_est_toujours_anomalie(self, regles) -> None:
        d = _dossier(
            type_scenario=TypeScenario.HOSPITALISATION,
            actes=[_acte(soumis_pec=True, pec_id=None)],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_REGIME] == StatutPilier.ANOMALIE

    def test_urgent_sans_pec_dans_le_delai_de_grace_est_conforme(self, regles) -> None:
        """Le coeur du raffinement : une admission d'urgence encore dans
        les 24h de grace ne doit PAS etre penalisee pour l'absence de PEC."""
        d = _dossier(
            type_scenario=TypeScenario.HOSPITALISATION,
            est_urgence=True,
            delai_regularisation_urgence_depasse=False,
            actes=[_acte(soumis_pec=True, pec_id=None)],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_REGIME] == StatutPilier.CONFORME

    def test_urgent_sans_pec_delai_de_grace_depasse_est_anomalie(self, regles) -> None:
        """Passe le delai de grace, l'exception d'urgence ne protege plus."""
        d = _dossier(
            type_scenario=TypeScenario.HOSPITALISATION,
            est_urgence=True,
            delai_regularisation_urgence_depasse=True,
            actes=[_acte(soumis_pec=True, pec_id=None)],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_REGIME] == StatutPilier.ANOMALIE

    def test_urgent_avec_pec_est_conforme(self, regles) -> None:
        d = _dossier(
            type_scenario=TypeScenario.HOSPITALISATION,
            est_urgence=True,
            actes=[_acte(soumis_pec=True, pec_id="PEC-URG-001")],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_REGIME] == StatutPilier.CONFORME


class TestPrescripteurNonRattacheFormation:
    """RP24-09."""

    def test_acte_non_rattache_est_a_verifier(self, regles) -> None:
        d = _dossier(actes=[_acte(prescripteur_rattache_formation=False)])
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == StatutPilier.A_VERIFIER

    def test_acte_rattache_est_conforme(self, regles) -> None:
        d = _dossier(actes=[_acte(prescripteur_rattache_formation=True)])
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == StatutPilier.CONFORME

    def test_medicament_non_rattache_est_a_verifier(self, regles) -> None:
        d = _dossier(
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-1000",
                    id_dossier="DOS-2026-001000",
                    dci="AMOXICILLINE",
                    voie_administration=VoieAdministration.ORALE,
                    duree_traitement_jours=5,
                    quantite=1,
                    prix_unitaire_facture=1000,
                    prescripteur_rattache_formation=False,
                )
            ]
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == StatutPilier.A_VERIFIER

    def test_resolution_reelle_via_registre(self) -> None:
        """Preuve de resolution reelle, pas seulement d'un champ fourni a
        la main -- meme esprit que les tests de resolution precedents."""
        registre_prescripteurs = RegistrePrescripteurs()
        registre_prescripteurs.enregistrer(
            Prescripteur(
                id_prescripteur="PRE-EXTERNE-01",
                numero_ordre="ORD-020",
                code_prescripteur_amu="01-020",
                type_prescripteur=TypePrescripteur.MEDECIN,
                statut=StatutPrescripteur.ACTIF,
                structures_rattachement=["FS-AUTRE-CENTRE"],  # pas FS-001
            )
        )
        gestionnaire = GestionnaireDossiers(
            regles=charger_regles(),
            journal=JournalConformite(),
            registre_prescripteurs=registre_prescripteurs,
            registre_formations=RegistreFormationsSanitaires(),
        )
        d = _dossier(
            id_formation="FS-001",
            actes=[_acte(id_prescripteur="PRE-EXTERNE-01")],
        )
        resultat = gestionnaire.soumettre(d, operateur_id="OP-001")
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == StatutPilier.A_VERIFIER

    def test_resolution_reelle_prescripteur_bien_rattache(self) -> None:
        registre_prescripteurs = RegistrePrescripteurs()
        registre_prescripteurs.enregistrer(
            Prescripteur(
                id_prescripteur="PRE-LOCAL-01",
                numero_ordre="ORD-021",
                code_prescripteur_amu="01-021",
                type_prescripteur=TypePrescripteur.MEDECIN,
                statut=StatutPrescripteur.ACTIF,
                structures_rattachement=["FS-001"],
            )
        )
        gestionnaire = GestionnaireDossiers(
            regles=charger_regles(),
            journal=JournalConformite(),
            registre_prescripteurs=registre_prescripteurs,
            registre_formations=RegistreFormationsSanitaires(),
        )
        d = _dossier(
            id_formation="FS-001",
            actes=[_acte(id_prescripteur="PRE-LOCAL-01")],
        )
        resultat = gestionnaire.soumettre(d, operateur_id="OP-001")
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == StatutPilier.CONFORME


class TestRajoutManuscrit:
    """RP24-04."""

    def test_rajout_detecte_est_anomalie(self, regles) -> None:
        d = _dossier(rajout_manuscrit_detecte=True)
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_DOCUMENTAIRE] == StatutPilier.ANOMALIE

    def test_aucun_rajout_est_conforme(self, regles) -> None:
        d = _dossier(rajout_manuscrit_detecte=False)
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_DOCUMENTAIRE] == StatutPilier.CONFORME


class TestInterventionForaine:
    """RP24-13."""

    def test_intervention_foraine_est_anomalie(self, regles) -> None:
        d = _dossier(intervention_foraine=True)
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_REGIME] == StatutPilier.ANOMALIE

    def test_hors_intervention_foraine_est_conforme(self, regles) -> None:
        d = _dossier(intervention_foraine=False)
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_REGIME] == StatutPilier.CONFORME


class TestBilanExclu:
    """RP24-23."""

    def test_bilan_a_priori_est_anomalie(self, regles) -> None:
        d = _dossier(actes=[_acte(est_bilan_sante_priori_ou_infertilite=True)])
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_REGIME] == StatutPilier.ANOMALIE

    def test_acte_normal_est_conforme(self, regles) -> None:
        d = _dossier(actes=[_acte(est_bilan_sante_priori_ou_infertilite=False)])
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_REGIME] == StatutPilier.CONFORME


class TestRadiographieMultiSegments:
    """RP24-27."""

    def test_plus_de_2_segments_sans_pec_ni_polytraumatisme_est_anomalie(self, regles) -> None:
        d = _dossier(
            polytraumatisme=False,
            actes=[_acte(radiographie_plus_de_2_segments=True, pec_id=None)],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.ANOMALIE

    def test_plus_de_2_segments_avec_pec_est_conforme(self, regles) -> None:
        d = _dossier(
            polytraumatisme=False,
            actes=[_acte(radiographie_plus_de_2_segments=True, pec_id="PEC-RADIO-01")],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.CONFORME

    def test_polytraumatisme_exempte_meme_sans_pec(self, regles) -> None:
        d = _dossier(
            polytraumatisme=True,
            actes=[_acte(radiographie_plus_de_2_segments=True, pec_id=None)],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.CONFORME
