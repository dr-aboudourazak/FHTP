"""Tests des regles ajoutees le 28 aout 2026 (lot 3) -- R-TG-016, R-TG-023,
RG-H01, RG-H02, RG-H03, RG-H05, RG-H06, RG-H09, RG-P11.
"""

from datetime import date, datetime

import pytest

from fhtp_core.engine.moteur_regles import evaluer_dossier
from fhtp_core.models.dossier import ActeRealise, Dossier, MedicamentPrescrit
from fhtp_core.models.enums import (
    CircuitRemboursement,
    Pilier,
    StatutPilier,
    TypeHospitalisation,
    TypeScenario,
    VoieAdministration,
)
from fhtp_core.rules.loader import charger_regles


@pytest.fixture(scope="module")
def regles():
    return charger_regles()


def _dossier(**overrides) -> Dossier:
    base = dict(
        id_dossier="DOS-2026-000900",
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
        id_acte="ACT-900",
        id_dossier="DOS-2026-000900",
        id_prescripteur="PRE-001",
        code_acte="C",
        diagnostic_cim10="J06.9",
        date_realisation=date(2026, 8, 28),
        montant_facture=7000,
    )
    base.update(overrides)
    return ActeRealise(**base)


class TestChargeurLot3:
    def test_neuf_regles_chargees(self, regles) -> None:
        ids = {r.id for r in regles}
        for id_attendu in [
            "R-TG-016", "R-TG-023", "RG-H01", "RG-H02", "RG-H03",
            "RG-H05", "RG-H06", "RG-H09", "RG-P11",
        ]:
            assert id_attendu in ids, f"{id_attendu} absente"

    def test_toujours_aucun_doublon(self, regles) -> None:
        ids = [r.id for r in regles]
        assert len(ids) == len(set(ids))


class TestVisiteControleMemeMotif:
    """R-TG-016."""

    def test_visite_controle_facturee_est_anomalie(self, regles) -> None:
        d = _dossier(actes=[_acte(visite_controle_meme_motif=True, montant_facture=7000)])
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_TARIFAIRE] == StatutPilier.ANOMALIE

    def test_visite_controle_gratuite_est_conforme(self, regles) -> None:
        d = _dossier(actes=[_acte(visite_controle_meme_motif=True, montant_facture=0)])
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_TARIFAIRE] == StatutPilier.CONFORME

    def test_consultation_normale_ne_declenche_rien(self, regles) -> None:
        d = _dossier(actes=[_acte(montant_facture=7000)])
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_TARIFAIRE] == StatutPilier.CONFORME


class TestAmuScolaire:
    """R-TG-023."""

    def test_part_patient_positive_pour_scolaire_est_anomalie(self, regles) -> None:
        d = _dossier(
            beneficiaire_amu_scolaire=True,
            actes=[_acte(part_patient=500)],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_REGIME] == StatutPilier.ANOMALIE

    def test_part_patient_nulle_pour_scolaire_est_conforme(self, regles) -> None:
        d = _dossier(
            beneficiaire_amu_scolaire=True,
            actes=[_acte(part_patient=0)],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_REGIME] == StatutPilier.CONFORME

    def test_beneficiaire_non_scolaire_avec_part_patient_ne_declenche_rien(self, regles) -> None:
        d = _dossier(
            beneficiaire_amu_scolaire=False,
            actes=[_acte(part_patient=1500)],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_REGIME] == StatutPilier.CONFORME


class TestActeSoumisPecSansPec:
    """RG-H01."""

    def test_acte_soumis_pec_sans_pec_est_anomalie(self, regles) -> None:
        d = _dossier(
            type_scenario=TypeScenario.HOSPITALISATION,
            actes=[_acte(soumis_pec=True, pec_id=None)],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_REGIME] == StatutPilier.ANOMALIE

    def test_acte_soumis_pec_avec_pec_est_conforme(self, regles) -> None:
        d = _dossier(
            type_scenario=TypeScenario.HOSPITALISATION,
            actes=[_acte(soumis_pec=True, pec_id="PEC-900")],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_REGIME] == StatutPilier.CONFORME

    def test_acte_non_soumis_pec_ne_declenche_rien(self, regles) -> None:
        d = _dossier(
            type_scenario=TypeScenario.HOSPITALISATION,
            actes=[_acte(soumis_pec=False, pec_id=None)],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_REGIME] == StatutPilier.CONFORME

    def test_hors_scenario_hospitalisation_ne_declenche_rien(self, regles) -> None:
        d = _dossier(
            type_scenario=TypeScenario.CONSULTATION,
            actes=[_acte(soumis_pec=True, pec_id=None)],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_REGIME] == StatutPilier.CONFORME


class TestMaterniteProlongee:
    """RG-H02."""

    def test_maternite_plus_de_5_jours_sans_justification_est_anomalie(self, regles) -> None:
        d = _dossier(
            type_scenario=TypeScenario.HOSPITALISATION,
            type_hospitalisation=TypeHospitalisation.MATERNITE,
            duree_sejour_jours=7,
            justification_medicale_presente=False,
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_DOCUMENTAIRE] == StatutPilier.ANOMALIE

    def test_maternite_plus_de_5_jours_avec_justification_est_conforme(self, regles) -> None:
        d = _dossier(
            type_scenario=TypeScenario.HOSPITALISATION,
            type_hospitalisation=TypeHospitalisation.MATERNITE,
            duree_sejour_jours=7,
            justification_medicale_presente=True,
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_DOCUMENTAIRE] == StatutPilier.CONFORME

    def test_maternite_5_jours_ou_moins_ne_declenche_rien(self, regles) -> None:
        d = _dossier(
            type_scenario=TypeScenario.HOSPITALISATION,
            type_hospitalisation=TypeHospitalisation.MATERNITE,
            duree_sejour_jours=4,
            justification_medicale_presente=False,
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_DOCUMENTAIRE] == StatutPilier.CONFORME

    def test_chirurgie_longue_ne_declenche_pas_rgh02(self, regles) -> None:
        """RG-H02 est propre a la maternite, pas a n'importe quel sejour long."""
        d = _dossier(
            type_scenario=TypeScenario.HOSPITALISATION,
            type_hospitalisation=TypeHospitalisation.CHIRURGIE,
            duree_sejour_jours=10,
            justification_medicale_presente=False,
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_DOCUMENTAIRE] == StatutPilier.CONFORME


class TestRapportSortieCliniquePrivee:
    """RG-H03."""

    def test_rapport_absent_en_clinique_privee_est_anomalie(self, regles) -> None:
        d = _dossier(
            type_scenario=TypeScenario.HOSPITALISATION,
            structure_est_clinique_privee=True,
            rapport_sortie_present=False,
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.ANOMALIE

    def test_rapport_present_en_clinique_privee_est_conforme(self, regles) -> None:
        d = _dossier(
            type_scenario=TypeScenario.HOSPITALISATION,
            structure_est_clinique_privee=True,
            rapport_sortie_present=True,
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.CONFORME

    def test_rapport_absent_en_secteur_public_ne_declenche_rien(self, regles) -> None:
        """Cf. RG-H03 : l'absence de rapport est toleree en secteur public."""
        d = _dossier(
            type_scenario=TypeScenario.HOSPITALISATION,
            structure_est_clinique_privee=False,
            rapport_sortie_present=False,
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.CONFORME


class TestDelaiTransmissionHospitalisation:
    """RG-H05 -- alerte, jamais un rejet automatique."""

    def test_depassement_est_a_verifier_pas_anomalie(self, regles) -> None:
        d = _dossier(
            type_scenario=TypeScenario.HOSPITALISATION,
            delai_transmission_hospitalisation_depasse=True,
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.A_VERIFIER

    def test_dans_les_delais_est_conforme(self, regles) -> None:
        d = _dossier(
            type_scenario=TypeScenario.HOSPITALISATION,
            delai_transmission_hospitalisation_depasse=False,
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.CONFORME


class TestCalculNuitees:
    """RG-H06 -- fraude type 8 du Knowledge Book."""

    def test_nuitees_facturees_superieures_est_anomalie(self, regles) -> None:
        d = _dossier(
            type_scenario=TypeScenario.HOSPITALISATION,
            nombre_nuitees_facturees=5,
            nombre_nuitees_attendues=4,
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_TARIFAIRE] == StatutPilier.ANOMALIE

    def test_nuitees_facturees_egales_est_conforme(self, regles) -> None:
        d = _dossier(
            type_scenario=TypeScenario.HOSPITALISATION,
            nombre_nuitees_facturees=4,
            nombre_nuitees_attendues=4,
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_TARIFAIRE] == StatutPilier.CONFORME

    def test_nuitees_facturees_inferieures_est_conforme(self, regles) -> None:
        """Facturer moins que prevu n'est pas une anomalie -- seul le
        depassement l'est."""
        d = _dossier(
            type_scenario=TypeScenario.HOSPITALISATION,
            nombre_nuitees_facturees=3,
            nombre_nuitees_attendues=4,
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_TARIFAIRE] == StatutPilier.CONFORME


class TestHopitalDeJour:
    """RG-H09."""

    def test_observation_plus_de_3_jours_est_anomalie(self, regles) -> None:
        d = _dossier(
            type_scenario=TypeScenario.HOSPITALISATION,
            type_hospitalisation=TypeHospitalisation.MISE_EN_OBSERVATION,
            duree_sejour_jours=5,
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_TARIFAIRE] == StatutPilier.ANOMALIE

    def test_observation_3_jours_ou_moins_est_conforme(self, regles) -> None:
        d = _dossier(
            type_scenario=TypeScenario.HOSPITALISATION,
            type_hospitalisation=TypeHospitalisation.MISE_EN_OBSERVATION,
            duree_sejour_jours=3,
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_TARIFAIRE] == StatutPilier.CONFORME

    def test_medecine_longue_ne_declenche_pas_rgh09(self, regles) -> None:
        d = _dossier(
            type_scenario=TypeScenario.HOSPITALISATION,
            type_hospitalisation=TypeHospitalisation.MEDECINE,
            duree_sejour_jours=10,
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_TARIFAIRE] == StatutPilier.CONFORME


class TestPrixPublicLePlusBas:
    """RG-P11."""

    def test_facture_au_dessus_du_prix_public_est_anomalie(self, regles) -> None:
        d = _dossier(
            type_scenario=TypeScenario.PHARMACIE,
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-900",
                    id_dossier="DOS-2026-000900",
                    dci="PARACETAMOL",
                    voie_administration=VoieAdministration.ORALE,
                    duree_traitement_jours=5,
                    quantite=1,
                    prix_unitaire_facture=2000,
                    prix_reference_presta_plus=2500,
                    prix_public_pharmacie=1500,
                )
            ],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_TARIFAIRE] == StatutPilier.ANOMALIE

    def test_facture_au_prix_public_est_conforme(self, regles) -> None:
        d = _dossier(
            type_scenario=TypeScenario.PHARMACIE,
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-901",
                    id_dossier="DOS-2026-000900",
                    dci="PARACETAMOL",
                    voie_administration=VoieAdministration.ORALE,
                    duree_traitement_jours=5,
                    quantite=1,
                    prix_unitaire_facture=1500,
                    prix_reference_presta_plus=2500,
                    prix_public_pharmacie=1500,
                )
            ],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_TARIFAIRE] == StatutPilier.CONFORME

    def test_prix_public_superieur_au_tarif_amu_ne_declenche_rien(self, regles) -> None:
        """Si le prix public est deja plus eleve que le tarif AMU, la
        regle ne s'applique pas (ce n'est pas le cas 'prix le plus bas')."""
        d = _dossier(
            type_scenario=TypeScenario.PHARMACIE,
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-902",
                    id_dossier="DOS-2026-000900",
                    dci="PARACETAMOL",
                    voie_administration=VoieAdministration.ORALE,
                    duree_traitement_jours=5,
                    quantite=1,
                    prix_unitaire_facture=2500,
                    prix_reference_presta_plus=2000,
                    prix_public_pharmacie=2500,
                )
            ],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_TARIFAIRE] == StatutPilier.CONFORME
