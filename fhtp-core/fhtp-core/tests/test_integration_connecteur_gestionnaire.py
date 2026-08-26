"""Tests de soumettre_avec_verification_payeur -- l'integration complete
entre connecteur payeur et Gestionnaire de Dossiers (section 10.1 et 7).

C'est ici que la bascule en Mode Degrade est prouvee comme un comportement
reel declenche par une panne simulee du connecteur, pas seulement comme un
champ positionne a la main dans les tests precedents
(test_engine_gestionnaire_dossiers.py) -- ceux-la restent valides pour
verifier le comportement de decision une fois en MODE_DEGRADE ; ceux-ci
verifient le declenchement lui-meme.
"""

from datetime import date, datetime

import pytest

from fhtp_core.connectors.payeur import BaseRemboursement, ResultatEligibilite
from fhtp_core.connectors.simulateur_payeur import SimulateurConnecteurPayeur
from fhtp_core.engine.gestionnaire_dossiers import GestionnaireDossiers
from fhtp_core.engine.journal import JournalConformite
from fhtp_core.models.dossier import ActeRealise, Dossier, MedicamentPrescrit
from fhtp_core.models.enums import (
    CircuitRemboursement,
    EventType,
    OrigineCreation,
    Pilier,
    StatutDossier,
    StatutEligibilite,
    StatutPEC,
    StatutPilier,
    TypeScenario,
    VoieAdministration,
)
from fhtp_core.rules.loader import charger_regles


@pytest.fixture
def gestionnaire():
    return GestionnaireDossiers(regles=charger_regles(), journal=JournalConformite())


@pytest.fixture
def connecteur():
    return SimulateurConnecteurPayeur()


def _dossier_conforme(id_dossier: str = "DOS-2026-000400") -> Dossier:
    return Dossier(
        id_dossier=id_dossier,
        type_scenario=TypeScenario.CONSULTATION,
        id_beneficiaire="BEN-001",
        id_formation="FS-001",
        id_contrat_payeur="CTR-001",
        circuit_remboursement=CircuitRemboursement.AMU_SEUL,
        date_soins=date(2026, 8, 26),
        date_soumission=datetime(2026, 8, 26, 10, 0, 0),
        cloture_triple_trait=True,
        actes=[
            ActeRealise(
                id_acte="ACT-200",
                id_dossier=id_dossier,
                id_prescripteur="PRE-001",
                code_acte="C",
                diagnostic_cim10="J06.9",
                date_realisation=date(2026, 8, 26),
                montant_facture=7000,
            )
        ],
    )


class TestEligibiliteActive:
    def test_beneficiaire_actif_suit_le_cours_normal(self, gestionnaire, connecteur) -> None:
        d = _dossier_conforme()
        connecteur.configurer_eligibilite(
            "BEN-001", ResultatEligibilite(statut=StatutEligibilite.ACTIF, taux_couverture=0.8)
        )
        resultat = gestionnaire.soumettre_avec_verification_payeur(d, connecteur, "OP-001")
        assert resultat.statut == StatutDossier.FAST_TRACK
        assert resultat.origine_creation == OrigineCreation.EN_LIGNE


class TestEligibiliteDefavorable:
    """Cf. section 10.1 : SUSPENDU/DROITS_FERMES -> ANOMALIE -> REJET/AUDIT."""

    @pytest.mark.parametrize("statut_defavorable", [StatutEligibilite.SUSPENDU, StatutEligibilite.DROITS_FERMES])
    def test_droits_fermes_ou_suspendus_forcent_anomalie(
        self, gestionnaire, connecteur, statut_defavorable
    ) -> None:
        d = _dossier_conforme()
        connecteur.configurer_eligibilite("BEN-001", ResultatEligibilite(statut=statut_defavorable))

        resultat = gestionnaire.soumettre_avec_verification_payeur(d, connecteur, "OP-001")

        assert resultat.evaluation_piliers[Pilier.COHERENCE_REGIME] == StatutPilier.ANOMALIE
        assert resultat.statut == StatutDossier.AUDIT
        assert any("Eligibilite payeur" in m for m in resultat.motifs_rejet)

    def test_eligibilite_inconnue_force_a_verifier_pas_anomalie(self, gestionnaire, connecteur) -> None:
        """Cf. section 10.1 : INCONNU -> A_VERIFIER, 'continuer avec cache' --
        distinct d'un rejet direct."""
        d = _dossier_conforme()
        connecteur.configurer_eligibilite("BEN-001", ResultatEligibilite(statut=StatutEligibilite.INCONNU))

        resultat = gestionnaire.soumettre_avec_verification_payeur(d, connecteur, "OP-001")

        assert resultat.evaluation_piliers[Pilier.COHERENCE_REGIME] == StatutPilier.A_VERIFIER
        assert resultat.statut == StatutDossier.CONTROLE_RAPIDE


class TestBasculeModeDegradeSurPanneReelle:
    """Le coeur de cette suite : la panne du connecteur -- pas un champ
    positionne a la main -- doit reellement produire un dossier plafonne."""

    def test_panne_sur_eligibilite_declenche_mode_degrade(self, gestionnaire, connecteur) -> None:
        d = _dossier_conforme()
        connecteur.definir_disponible(False)

        resultat = gestionnaire.soumettre_avec_verification_payeur(d, connecteur, "OP-001")

        assert resultat.origine_creation == OrigineCreation.MODE_DEGRADE
        assert resultat.statut == StatutDossier.EN_VALIDATION_LOCALE
        assert resultat.statut != StatutDossier.FAST_TRACK
        assert resultat.decision_finale is None

    def test_panne_survenant_apres_eligibilite_mais_avant_verification_pec(
        self, gestionnaire, connecteur
    ) -> None:
        """Cas plus subtil : le connecteur repond correctement a
        l'eligibilite, puis tombe en panne au moment precis de verifier une
        PEC referencee -- doit basculer en Mode Degrade tout autant qu'une
        panne des le depart, pas laisser passer le dossier sur la base de
        la seule eligibilite deja obtenue."""
        d = _dossier_conforme()
        d = d.model_copy(
            update={
                "medicaments": [
                    MedicamentPrescrit(
                        id_prescription="MED-500",
                        id_dossier=d.id_dossier,
                        dci="AMOXICILLINE",
                        voie_administration=VoieAdministration.ORALE,
                        duree_traitement_jours=20,
                        quantite=1,
                        prix_unitaire_facture=1000,
                        pec_id="PEC-999",
                    )
                ]
            }
        )
        connecteur.configurer_eligibilite("BEN-001", ResultatEligibilite(statut=StatutEligibilite.ACTIF))
        # Aucune PEC configuree pour "PEC-999" -- mais la panne intervient
        # avant meme d'atteindre le fail-closed normal.
        connecteur.definir_disponible(True)

        # On simule la panne survenant juste avant l'appel a verifier_pec en
        # rendant le connecteur indisponible seulement apres le premier appel.
        appel_original = connecteur.verifier_eligibilite

        def eligibilite_puis_panne(*args, **kwargs):
            resultat = appel_original(*args, **kwargs)
            connecteur.definir_disponible(False)
            return resultat

        connecteur.verifier_eligibilite = eligibilite_puis_panne  # type: ignore[method-assign]

        resultat = gestionnaire.soumettre_avec_verification_payeur(d, connecteur, "OP-001")

        assert resultat.origine_creation == OrigineCreation.MODE_DEGRADE
        assert resultat.statut == StatutDossier.EN_VALIDATION_LOCALE

    def test_bascule_est_journalisee(self, gestionnaire, connecteur) -> None:
        d = _dossier_conforme()
        connecteur.definir_disponible(False)
        gestionnaire.soumettre_avec_verification_payeur(d, connecteur, "OP-001")

        historique = gestionnaire._journal.historique_dossier(d.id_dossier)
        assert any(
            e.event_type == EventType.SYNC and "indisponible" in e.resultat.lower()
            for e in historique
        )

    def test_apres_bascule_resynchroniser_peut_debloquer(self, gestionnaire, connecteur) -> None:
        """Verifie l'enchainement complet : panne -> Mode Degrade -> panne
        reparee -> resynchronisation -> FAST_TRACK. C'est le cycle complet
        que la section 7 decrit de bout en bout."""
        d = _dossier_conforme()
        connecteur.definir_disponible(False)
        resultat_degrade = gestionnaire.soumettre_avec_verification_payeur(d, connecteur, "OP-001")
        assert resultat_degrade.statut == StatutDossier.EN_VALIDATION_LOCALE

        connecteur.definir_disponible(True)
        connecteur.configurer_eligibilite("BEN-001", ResultatEligibilite(statut=StatutEligibilite.ACTIF))
        resultat_final = gestionnaire.resynchroniser(resultat_degrade, "OP-001")

        assert resultat_final.statut == StatutDossier.FAST_TRACK
        assert resultat_final.origine_creation == OrigineCreation.EN_LIGNE


class TestVerificationPECReelle:
    """Cf. F7 (section 8.2) : la presence d'un pec_id ne suffit jamais, il
    faut la confirmation reelle du payeur."""

    def test_pec_confirmee_accordee_reste_conforme(self, gestionnaire, connecteur) -> None:
        d = _dossier_conforme()
        d = d.model_copy(
            update={
                "medicaments": [
                    MedicamentPrescrit(
                        id_prescription="MED-501",
                        id_dossier=d.id_dossier,
                        dci="AMOXICILLINE",
                        voie_administration=VoieAdministration.ORALE,
                        duree_traitement_jours=20,
                        quantite=1,
                        prix_unitaire_facture=1000,
                        pec_id="PEC-100",
                    )
                ]
            }
        )
        connecteur.configurer_eligibilite("BEN-001", ResultatEligibilite(statut=StatutEligibilite.ACTIF))
        connecteur.configurer_pec("PEC-100", StatutPEC.ACCORDE)

        resultat = gestionnaire.soumettre_avec_verification_payeur(d, connecteur, "OP-001")
        assert resultat.statut == StatutDossier.FAST_TRACK

    def test_pec_non_confirmee_par_le_payeur_declenche_anomalie(self, gestionnaire, connecteur) -> None:
        """Un pec_id present sur le dossier (donc les regles internes sont
        satisfaites) mais que le payeur ne confirme PAS -- exactement
        l'inverse de l'incident du CHR Dapaong : ici le numero est present
        mais n'a en realite jamais ete accorde."""
        d = _dossier_conforme()
        d = d.model_copy(
            update={
                "medicaments": [
                    MedicamentPrescrit(
                        id_prescription="MED-502",
                        id_dossier=d.id_dossier,
                        dci="AMOXICILLINE",
                        voie_administration=VoieAdministration.ORALE,
                        duree_traitement_jours=20,
                        quantite=1,
                        prix_unitaire_facture=1000,
                        pec_id="PEC-FABRIQUEE",
                    )
                ]
            }
        )
        connecteur.configurer_eligibilite("BEN-001", ResultatEligibilite(statut=StatutEligibilite.ACTIF))
        # PEC-FABRIQUEE n'est jamais configuree -> fail closed -> REFUSE.

        resultat = gestionnaire.soumettre_avec_verification_payeur(d, connecteur, "OP-001")

        assert resultat.evaluation_piliers[Pilier.COMPLETUDE_ADMINISTRATIVE] == StatutPilier.ANOMALIE
        assert resultat.statut == StatutDossier.AUDIT
        assert any("PEC-FABRIQUEE" in m for m in resultat.motifs_rejet)
