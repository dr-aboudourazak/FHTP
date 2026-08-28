"""Tests des regles complementaires ajoutees le 27 aout 2026 -- R-TG-020,
RG-P07, R-TG-021, RG-H11.

Meme structure que test_engine_moteur_regles.py : positif (declenche),
negatif (ne declenche pas), et verification du scope scenario ou circuit
quand la regle en a un.
"""

from datetime import date, datetime

import pytest

from fhtp_core.engine.moteur_regles import evaluer_dossier
from fhtp_core.models.dossier import Dossier, MedicamentPrescrit
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
        id_dossier="DOS-2026-000600",
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


class TestChargeurAvecNouvellesRegles:
    def test_quatre_nouvelles_regles_chargees(self, regles) -> None:
        ids = {r.id for r in regles}
        for id_attendu in ["R-TG-020", "RG-P07", "R-TG-021", "RG-H11"]:
            assert id_attendu in ids, f"{id_attendu} absente du referentiel charge"

    def test_toujours_aucun_doublon(self, regles) -> None:
        ids = [r.id for r in regles]
        assert len(ids) == len(set(ids))


class TestEchographiesObstetricales:
    """R-TG-020 -- max 3 echographies obstetricales sans PEC."""

    def test_plus_de_trois_sans_pec_est_anomalie(self, regles) -> None:
        d = _dossier_consultation(
            nombre_echographies_obstetricales=4, pec_echographie_supplementaire_id=None
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.ANOMALIE

    def test_plus_de_trois_avec_pec_est_conforme(self, regles) -> None:
        d = _dossier_consultation(
            nombre_echographies_obstetricales=4, pec_echographie_supplementaire_id="PEC-ECHO-1"
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.CONFORME

    def test_trois_ou_moins_ne_declenche_rien(self, regles) -> None:
        d = _dossier_consultation(nombre_echographies_obstetricales=3)
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.CONFORME

    def test_champ_non_renseigne_ne_declenche_rien(self, regles) -> None:
        """None = non renseigne -- ne doit jamais etre interprete comme
        'plus de 3', une donnee absente n'est pas une donnee positive."""
        d = _dossier_consultation()
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.CONFORME


class TestSubstitutionGenerique:
    """RG-P07 -- substitution plus chere sans accord."""

    def test_substituant_plus_cher_sans_pec_est_anomalie(self, regles) -> None:
        d = _dossier_consultation(
            type_scenario=TypeScenario.PHARMACIE,
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-600",
                    id_dossier="DOS-2026-000600",
                    dci="PARACETAMOL",
                    voie_administration=VoieAdministration.ORALE,
                    duree_traitement_jours=5,
                    quantite=1,
                    prix_unitaire_facture=2000,
                    substituant_dci="PARACETAMOL_GENERIQUE",
                    prix_produit_initial=1500,
                    pec_id=None,
                )
            ],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_TARIFAIRE] == StatutPilier.ANOMALIE

    def test_substituant_moins_cher_est_conforme(self, regles) -> None:
        d = _dossier_consultation(
            type_scenario=TypeScenario.PHARMACIE,
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-601",
                    id_dossier="DOS-2026-000600",
                    dci="PARACETAMOL",
                    voie_administration=VoieAdministration.ORALE,
                    duree_traitement_jours=5,
                    quantite=1,
                    prix_unitaire_facture=1000,
                    substituant_dci="PARACETAMOL_GENERIQUE",
                    prix_produit_initial=1500,
                    pec_id=None,
                )
            ],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_TARIFAIRE] == StatutPilier.CONFORME

    def test_pas_de_substitution_ne_declenche_rien(self, regles) -> None:
        d = _dossier_consultation(
            type_scenario=TypeScenario.PHARMACIE,
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-602",
                    id_dossier="DOS-2026-000600",
                    dci="PARACETAMOL",
                    voie_administration=VoieAdministration.ORALE,
                    duree_traitement_jours=5,
                    quantite=1,
                    prix_unitaire_facture=1000,
                    substituant_dci=None,
                )
            ],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_TARIFAIRE] == StatutPilier.CONFORME


class TestRestrictionParamedicale:
    """R-TG-021 -- molecule proscrite prescrite par un paramedical sans PEC."""

    def test_paramedical_molecule_proscrite_sans_pec_est_anomalie(self, regles) -> None:
        d = _dossier_consultation(
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-603",
                    id_dossier="DOS-2026-000600",
                    dci="LEVOFLOXACINE",
                    voie_administration=VoieAdministration.ORALE,
                    duree_traitement_jours=5,
                    quantite=1,
                    prix_unitaire_facture=5000,
                    prescripteur_paramedical=True,
                    molecule_proscrite_paramedical=True,
                    pec_id=None,
                )
            ]
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == StatutPilier.ANOMALIE

    def test_paramedical_molecule_proscrite_avec_pec_est_conforme(self, regles) -> None:
        d = _dossier_consultation(
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-604",
                    id_dossier="DOS-2026-000600",
                    dci="LEVOFLOXACINE",
                    voie_administration=VoieAdministration.ORALE,
                    duree_traitement_jours=5,
                    quantite=1,
                    prix_unitaire_facture=5000,
                    prescripteur_paramedical=True,
                    molecule_proscrite_paramedical=True,
                    pec_id="PEC-DEROGATION",
                )
            ]
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == StatutPilier.CONFORME

    def test_medecin_meme_molecule_ne_declenche_rien(self, regles) -> None:
        """La restriction est propre aux paramedicaux -- un medecin peut
        prescrire la meme molecule sans PEC."""
        d = _dossier_consultation(
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-605",
                    id_dossier="DOS-2026-000600",
                    dci="LEVOFLOXACINE",
                    voie_administration=VoieAdministration.ORALE,
                    duree_traitement_jours=5,
                    quantite=1,
                    prix_unitaire_facture=5000,
                    prescripteur_paramedical=False,
                    molecule_proscrite_paramedical=True,
                    pec_id=None,
                )
            ]
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == StatutPilier.CONFORME


class TestMedicamentOralCliniquePrivee:
    """RG-H11 -- medicaments oraux exclus en clinique privee sous AMU."""

    def test_oral_en_clinique_privee_est_anomalie(self, regles) -> None:
        d = _dossier_consultation(
            structure_est_clinique_privee=True,
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-606",
                    id_dossier="DOS-2026-000600",
                    dci="AMOXICILLINE",
                    voie_administration=VoieAdministration.ORALE,
                    duree_traitement_jours=5,
                    quantite=1,
                    prix_unitaire_facture=1000,
                )
            ],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_REGIME] == StatutPilier.ANOMALIE

    def test_injectable_en_clinique_privee_est_conforme(self, regles) -> None:
        d = _dossier_consultation(
            structure_est_clinique_privee=True,
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-607",
                    id_dossier="DOS-2026-000600",
                    dci="CEFTRIAXONE",
                    voie_administration=VoieAdministration.PARENTERALE,
                    duree_traitement_jours=3,
                    quantite=3,
                    prix_unitaire_facture=2000,
                )
            ],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_REGIME] == StatutPilier.CONFORME

    def test_oral_hors_clinique_privee_ne_declenche_pas_rgh11(self, regles) -> None:
        """Meme medicament oral, mais structure non marquee clinique
        privee (ex: formation publique) -- ne doit pas declencher RG-H11."""
        d = _dossier_consultation(
            structure_est_clinique_privee=False,
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-608",
                    id_dossier="DOS-2026-000600",
                    dci="AMOXICILLINE",
                    voie_administration=VoieAdministration.ORALE,
                    duree_traitement_jours=5,
                    quantite=1,
                    prix_unitaire_facture=1000,
                )
            ],
        )
        resultat = evaluer_dossier(d, regles)
        assert resultat.evaluation_piliers[Pilier.COHERENCE_REGIME] == StatutPilier.CONFORME
