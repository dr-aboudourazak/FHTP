"""Tests du chargeur de regles et du moteur d'evaluation bout en bout.

Reference : FHTP-ARC-001, section 2.1.
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


def _dossier_consultation(**overrides) -> Dossier:
    base = dict(
        id_dossier="DOS-2026-000100",
        type_scenario=TypeScenario.CONSULTATION,
        id_beneficiaire="BEN-001",
        id_formation="FS-001",
        id_contrat_payeur="CTR-001",
        circuit_remboursement=CircuitRemboursement.AMU_SEUL,
        date_soins=date(2026, 8, 25),
        date_soumission=datetime(2026, 8, 25, 10, 0, 0),
    )
    base.update(overrides)
    return Dossier(**base)


class TestChargeurRegles:
    def test_charge_au_moins_les_regles_attendues(self, regles) -> None:
        ids = {r.id for r in regles}
        assert "R-TG-017" in ids
        assert "R-TG-005" in ids
        assert "R-TG-015" in ids
        assert "RG-H08" in ids

    def test_aucun_doublon_identifiant(self, regles) -> None:
        ids = [r.id for r in regles]
        assert len(ids) == len(set(ids))


class TestMoteurR68:
    """R-TG-017 -- rejet immediat, non regularisable."""

    def test_r68_declenche_anomalie_documentaire(self, regles) -> None:
        d = _dossier_consultation(
            actes=[
                ActeRealise(
                    id_acte="ACT-001",
                    id_dossier="DOS-2026-000100",
                    id_prescripteur="PRE-001",
                    code_acte="C",
                    diagnostic_cim10="R68",
                    date_realisation=date(2026, 8, 25),
                    montant_facture=7000,
                )
            ]
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_DOCUMENTAIRE] == StatutPilier.ANOMALIE
        assert any("R-TG-017" in m for m in resultat.motifs_rejet)

    def test_diagnostic_valide_ne_declenche_rien(self, regles) -> None:
        d = _dossier_consultation(
            actes=[
                ActeRealise(
                    id_acte="ACT-002",
                    id_dossier="DOS-2026-000100",
                    id_prescripteur="PRE-001",
                    code_acte="C",
                    diagnostic_cim10="J06.9",
                    date_realisation=date(2026, 8, 25),
                    montant_facture=7000,
                )
            ]
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_DOCUMENTAIRE] == StatutPilier.CONFORME


class TestMoteurDureeTraitementSansPEC:
    """R-TG-015 -- duree > 15 jours sans PEC."""

    def test_duree_longue_sans_pec_est_anomalie(self, regles) -> None:
        d = _dossier_consultation(
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-001",
                    id_dossier="DOS-2026-000100",
                    dci="AMOXICILLINE",
                    voie_administration=VoieAdministration.ORALE,
                    duree_traitement_jours=30,
                    quantite=1,
                    prix_unitaire_facture=1000,
                    pec_id=None,
                )
            ]
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_TARIFAIRE] == StatutPilier.ANOMALIE

    def test_duree_longue_avec_pec_est_conforme(self, regles) -> None:
        d = _dossier_consultation(
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-002",
                    id_dossier="DOS-2026-000100",
                    dci="AMOXICILLINE",
                    voie_administration=VoieAdministration.ORALE,
                    duree_traitement_jours=30,
                    quantite=1,
                    prix_unitaire_facture=1000,
                    pec_id="PEC-001",
                )
            ]
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_TARIFAIRE] == StatutPilier.CONFORME


class TestMoteurHospitalisationInjectable:
    """RG-H08 -- injectable > 3 jours sans PEC, scenario HOSPITALISATION
    uniquement (ne doit jamais se declencher en CONSULTATION)."""

    def test_injectable_long_en_hospitalisation_sans_pec(self, regles) -> None:
        d = _dossier_consultation(
            type_scenario=TypeScenario.HOSPITALISATION,
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-003",
                    id_dossier="DOS-2026-000100",
                    dci="CEFTRIAXONE",
                    voie_administration=VoieAdministration.PARENTERALE,
                    duree_traitement_jours=5,
                    quantite=5,
                    prix_unitaire_facture=2000,
                    pec_id=None,
                )
            ],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_TARIFAIRE] == StatutPilier.ANOMALIE

    def test_meme_medicament_en_consultation_ne_declenche_pas_rgh08(self, regles) -> None:
        """RG-H08 est scope a HOSPITALISATION (section 6, RG-H08) -- le
        meme medicament dans une consultation ne doit pas le declencher,
        meme s'il est aussi parenteral et long."""
        d = _dossier_consultation(
            type_scenario=TypeScenario.CONSULTATION,
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-004",
                    id_dossier="DOS-2026-000100",
                    dci="CEFTRIAXONE",
                    voie_administration=VoieAdministration.PARENTERALE,
                    duree_traitement_jours=5,
                    quantite=5,
                    prix_unitaire_facture=2000,
                    pec_id=None,
                )
            ],
        )
        resultat = evaluer_dossier(d, regles)
        # RG-H08 ne s'applique pas ; aucune autre regle du pilier tarifaire
        # ne se declenche ici -> CONFORME (regles chargees, aucune declenchee).
        assert resultat.evaluation_piliers[Pilier.COHERENCE_TARIFAIRE] == StatutPilier.CONFORME


class TestPilierNonEvalue:
    def test_pilier_sans_regle_applicable_est_non_evalue(self, regles) -> None:
        """Le pilier COHERENCE_GRAPHIQUE n'a aucune regle dans le
        referentiel actuel (backlog, section 2.1) -- doit rester
        NON_EVALUE, jamais CONFORME par defaut ni ANOMALIE par exces de zele."""
        d = _dossier_consultation()
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_GRAPHIQUE] == StatutPilier.NON_EVALUE


class TestIntegrationAvecMoteurDecision:
    """Verifie que le resultat de evaluer_dossier() s'enchaine correctement
    avec fhtp_core.engine.decision -- les deux modules doivent former un
    pipeline coherent de bout en bout."""

    def test_dossier_propre_va_jusqu_au_fast_track(self, regles) -> None:
        from fhtp_core.engine.decision import decider
        from fhtp_core.models.enums import DecisionFinale

        d = _dossier_consultation(
            cloture_triple_trait=True,
            actes=[
                ActeRealise(
                    id_acte="ACT-010",
                    id_dossier="DOS-2026-000100",
                    id_prescripteur="PRE-001",
                    code_acte="C",
                    diagnostic_cim10="J06.9",
                    date_realisation=date(2026, 8, 25),
                    montant_facture=7000,
                )
            ],
        )
        evalue = evaluer_dossier(d, regles)
        assert decider(evalue) == DecisionFinale.FAST_TRACK

    def test_dossier_avec_r68_va_jusqu_a_audit_approfondi(self, regles) -> None:
        from fhtp_core.engine.decision import decider
        from fhtp_core.models.enums import DecisionFinale

        d = _dossier_consultation(
            cloture_triple_trait=True,
            actes=[
                ActeRealise(
                    id_acte="ACT-011",
                    id_dossier="DOS-2026-000100",
                    id_prescripteur="PRE-001",
                    code_acte="C",
                    diagnostic_cim10="R68",
                    date_realisation=date(2026, 8, 25),
                    montant_facture=7000,
                )
            ],
        )
        evalue = evaluer_dossier(d, regles)
        assert decider(evalue) == DecisionFinale.AUDIT_APPROFONDI
