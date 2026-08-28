"""Tests des regles ajoutees le 27 aout 2026 (lot 2) -- R-TG-002, R-TG-003,
R-TG-004, R-TG-008, R-TG-019 (scanner et IRM).
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
    TypeActeImagerie,
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
        id_dossier="DOS-2026-000800",
        type_scenario=TypeScenario.CONSULTATION,
        id_beneficiaire="BEN-001",
        id_formation="FS-001",
        id_contrat_payeur="CTR-001",
        circuit_remboursement=CircuitRemboursement.AMU_SEUL,
        date_soins=date(2026, 8, 27),
        date_soumission=datetime(2026, 8, 27, 10, 0, 0),
    )
    base.update(overrides)
    return Dossier(**base)


class TestChargeurLot2:
    def test_six_regles_chargees(self, regles) -> None:
        ids = {r.id for r in regles}
        for id_attendu in [
            "R-TG-002", "R-TG-003", "R-TG-004", "R-TG-008",
            "R-TG-019-SCANNER", "R-TG-019-IRM",
        ]:
            assert id_attendu in ids, f"{id_attendu} absente"

    def test_toujours_aucun_doublon(self, regles) -> None:
        ids = [r.id for r in regles]
        assert len(ids) == len(set(ids))


class TestDelaiSoumission:
    """R-TG-002."""

    def test_hors_delai_est_anomalie(self, regles) -> None:
        d = _dossier(hors_delai_soumission=True)
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.ANOMALIE

    def test_dans_les_delais_est_conforme(self, regles) -> None:
        d = _dossier(hors_delai_soumission=False)
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.CONFORME

    def test_non_renseigne_ne_declenche_rien(self, regles) -> None:
        d = _dossier()
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.CONFORME


class TestRecuTicketModerateur:
    """R-TG-003."""

    def test_recu_absent_sans_exemption_est_anomalie(self, regles) -> None:
        d = _dossier(recu_ticket_moderateur_present=False, exemption_double_couverture=False)
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.ANOMALIE

    def test_recu_absent_avec_exemption_est_conforme(self, regles) -> None:
        d = _dossier(recu_ticket_moderateur_present=False, exemption_double_couverture=True)
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.CONFORME

    def test_recu_present_est_conforme(self, regles) -> None:
        d = _dossier(recu_ticket_moderateur_present=True)
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.CONFORME


class TestMedicamentNonEnrolePresta:
    """R-TG-004."""

    def test_non_enrole_est_a_verifier_pas_rejet_total(self, regles) -> None:
        """Cf. section 10.3 : un medicament non couvert fait payer le
        patient integralement sur cette ligne, ca ne rejette pas tout le
        dossier -- A_VERIFIER, pas ANOMALIE."""
        d = _dossier(
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-800",
                    id_dossier="DOS-2026-000800",
                    dci="MOLECULE_HORS_LISTE",
                    voie_administration=VoieAdministration.ORALE,
                    duree_traitement_jours=5,
                    quantite=1,
                    prix_unitaire_facture=3000,
                    enrole_presta_plus=False,
                )
            ]
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_TARIFAIRE] == StatutPilier.A_VERIFIER

    def test_enrole_est_conforme(self, regles) -> None:
        d = _dossier(
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-801",
                    id_dossier="DOS-2026-000800",
                    dci="AMOXICILLINE",
                    voie_administration=VoieAdministration.ORALE,
                    duree_traitement_jours=5,
                    quantite=1,
                    prix_unitaire_facture=1000,
                    enrole_presta_plus=True,
                )
            ]
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_TARIFAIRE] == StatutPilier.CONFORME

    def test_non_renseigne_ne_declenche_pas_r_tg_004(self, regles) -> None:
        """Regression : enrole_presta_plus non renseigne (None, valeur par
        defaut) ne doit JAMAIS declencher R-TG-004 -- seul un False
        explicite (verifie et confirme absent de Presta+) le doit. Un
        premier essai de cette regle avait un defaut a False plutot qu'a
        None, faisant declencher R-TG-004 sur tous les medicaments de test
        existants qui ne s'en souciaient pas -- 5 tests avaient casse avant
        cette correction."""
        d = _dossier(
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-802",
                    id_dossier="DOS-2026-000800",
                    dci="AMOXICILLINE",
                    voie_administration=VoieAdministration.ORALE,
                    duree_traitement_jours=5,
                    quantite=1,
                    prix_unitaire_facture=1000,
                    # enrole_presta_plus non renseigne du tout.
                )
            ]
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_TARIFAIRE] == StatutPilier.CONFORME


class TestCachetNumeroOrdre:
    """R-TG-008."""

    def test_cachet_absent_est_a_verifier(self, regles) -> None:
        d = _dossier(cachet_numero_ordre_present=False)
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.A_VERIFIER

    def test_cachet_present_est_conforme(self, regles) -> None:
        d = _dossier(cachet_numero_ordre_present=True)
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.CONFORME


class TestRestrictionsImagerie:
    """R-TG-019 -- scanner reserve aux medecins, IRM aux specialistes."""

    def test_scanner_par_non_medecin_est_anomalie(self, regles) -> None:
        d = _dossier(
            actes=[
                ActeRealise(
                    id_acte="ACT-800",
                    id_dossier="DOS-2026-000800",
                    id_prescripteur="PRE-001",
                    code_acte="TDM01",
                    diagnostic_cim10="S06.0",
                    date_realisation=date(2026, 8, 27),
                    montant_facture=70000,
                    type_acte_imagerie=TypeActeImagerie.SCANNER,
                    prescripteur_est_medecin=False,
                )
            ]
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == StatutPilier.ANOMALIE

    def test_scanner_par_medecin_est_conforme(self, regles) -> None:
        d = _dossier(
            actes=[
                ActeRealise(
                    id_acte="ACT-801",
                    id_dossier="DOS-2026-000800",
                    id_prescripteur="PRE-001",
                    code_acte="TDM01",
                    diagnostic_cim10="S06.0",
                    date_realisation=date(2026, 8, 27),
                    montant_facture=70000,
                    type_acte_imagerie=TypeActeImagerie.SCANNER,
                    prescripteur_est_medecin=True,
                )
            ]
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == StatutPilier.CONFORME

    def test_irm_par_medecin_non_specialiste_est_anomalie(self, regles) -> None:
        d = _dossier(
            actes=[
                ActeRealise(
                    id_acte="ACT-802",
                    id_dossier="DOS-2026-000800",
                    id_prescripteur="PRE-001",
                    code_acte="IRM01",
                    diagnostic_cim10="S06.0",
                    date_realisation=date(2026, 8, 27),
                    montant_facture=160000,
                    type_acte_imagerie=TypeActeImagerie.IRM,
                    prescripteur_est_medecin=True,
                    prescripteur_est_specialiste=False,
                )
            ]
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == StatutPilier.ANOMALIE

    def test_irm_par_specialiste_est_conforme(self, regles) -> None:
        d = _dossier(
            actes=[
                ActeRealise(
                    id_acte="ACT-803",
                    id_dossier="DOS-2026-000800",
                    id_prescripteur="PRE-001",
                    code_acte="IRM01",
                    diagnostic_cim10="S06.0",
                    date_realisation=date(2026, 8, 27),
                    montant_facture=160000,
                    type_acte_imagerie=TypeActeImagerie.IRM,
                    prescripteur_est_specialiste=True,
                )
            ]
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == StatutPilier.CONFORME

    def test_acte_non_imagerie_ne_declenche_rien(self, regles) -> None:
        d = _dossier(
            actes=[
                ActeRealise(
                    id_acte="ACT-804",
                    id_dossier="DOS-2026-000800",
                    id_prescripteur="PRE-001",
                    code_acte="C",
                    diagnostic_cim10="J06.9",
                    date_realisation=date(2026, 8, 27),
                    montant_facture=7000,
                )
            ]
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == StatutPilier.CONFORME


class TestResolutionReelleImagerie:
    """Preuve que R-TG-019 fonctionne aussi via une vraie resolution de
    registre, pas seulement via des champs fournis a la main (meme esprit
    que test_engine_resolution_referentiels.py)."""

    def test_irm_resolue_via_registre_specialiste(self) -> None:
        registre_prescripteurs = RegistrePrescripteurs()
        registre_prescripteurs.enregistrer(
            Prescripteur(
                id_prescripteur="PRE-SPECIALISTE-01",
                numero_ordre="ORD-010",
                code_prescripteur_amu="01-010",
                type_prescripteur=TypePrescripteur.MEDECIN,
                specialite_declaree="Radiologie",
                statut=StatutPrescripteur.ACTIF,
            )
        )
        gestionnaire = GestionnaireDossiers(
            regles=charger_regles(),
            journal=JournalConformite(),
            registre_prescripteurs=registre_prescripteurs,
            registre_formations=RegistreFormationsSanitaires(),
        )
        d = _dossier(
            actes=[
                ActeRealise(
                    id_acte="ACT-900",
                    id_dossier="DOS-2026-000800",
                    id_prescripteur="PRE-SPECIALISTE-01",
                    code_acte="IRM01",
                    diagnostic_cim10="S06.0",
                    date_realisation=date(2026, 8, 27),
                    montant_facture=160000,
                    type_acte_imagerie=TypeActeImagerie.IRM,
                )
            ]
        )
        resultat = gestionnaire.soumettre(d, operateur_id="OP-001")
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == StatutPilier.CONFORME

    def test_irm_resolue_via_registre_medecin_generaliste_est_anomalie(self) -> None:
        """Un medecin resolu via le registre, mais sans specialite
        declaree -- ne satisfait pas l'exigence 'specialiste' de R-TG-019."""
        registre_prescripteurs = RegistrePrescripteurs()
        registre_prescripteurs.enregistrer(
            Prescripteur(
                id_prescripteur="PRE-GENERALISTE-01",
                numero_ordre="ORD-011",
                code_prescripteur_amu="01-011",
                type_prescripteur=TypePrescripteur.MEDECIN,
                specialite_declaree=None,
                statut=StatutPrescripteur.ACTIF,
            )
        )
        gestionnaire = GestionnaireDossiers(
            regles=charger_regles(),
            journal=JournalConformite(),
            registre_prescripteurs=registre_prescripteurs,
            registre_formations=RegistreFormationsSanitaires(),
        )
        d = _dossier(
            actes=[
                ActeRealise(
                    id_acte="ACT-901",
                    id_dossier="DOS-2026-000800",
                    id_prescripteur="PRE-GENERALISTE-01",
                    code_acte="IRM01",
                    diagnostic_cim10="S06.0",
                    date_realisation=date(2026, 8, 27),
                    montant_facture=160000,
                    type_acte_imagerie=TypeActeImagerie.IRM,
                )
            ]
        )
        resultat = gestionnaire.soumettre(d, operateur_id="OP-001")
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == StatutPilier.ANOMALIE
