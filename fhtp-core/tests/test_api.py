"""Tests de l'API -- FHTP-ARC-001, section 12.

Verifie le contrat HTTP lui-meme (codes, format de reponse, idempotence) et
confirme le principe de section 12.7 : une decision defavorable du moteur de
regles reste un 200, jamais un code d'erreur.
"""

import pytest
from fastapi.testclient import TestClient

from fhtp_core.api.app import app
from fhtp_core.api.auth import ContexteOperateur, RoleRBAC
from fhtp_core.api.dependencies import (
    get_annuaire_jetons,
    get_connecteur_payeur,
    reinitialiser_etat_pour_tests,
)
from fhtp_core.connectors.payeur import ResultatEligibilite
from fhtp_core.connectors.simulateur_payeur import SimulateurConnecteurPayeur
from fhtp_core.models.enums import StatutEligibilite

JETON_CAB_001 = "test-jeton-cab-001"
JETON_CAB_002 = "test-jeton-cab-002"
JETON_MEDECIN_CONSEIL = "test-jeton-medecin-conseil"


@pytest.fixture(autouse=True)
def _reinitialiser_etat():
    reinitialiser_etat_pour_tests()
    annuaire = get_annuaire_jetons()
    annuaire.enregistrer(
        JETON_CAB_001,
        ContexteOperateur(operateur_id="OP-CAB-001", id_formation="FS-001", role=RoleRBAC.OPERATEUR_SAISIE),
    )
    annuaire.enregistrer(
        JETON_CAB_002,
        ContexteOperateur(operateur_id="OP-CAB-002", id_formation="FS-002", role=RoleRBAC.OPERATEUR_SAISIE),
    )
    annuaire.enregistrer(
        JETON_MEDECIN_CONSEIL,
        ContexteOperateur(
            operateur_id="MC-001", id_formation="FS-PAYEUR", role=RoleRBAC.MEDECIN_CONSEIL
        ),
    )
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


def _entete(jeton: str = JETON_CAB_001) -> dict:
    return {"Authorization": f"Bearer {jeton}"}


def _corps_dossier_conforme(id_dossier: str = "DOS-API-001", id_formation: str = "FS-001") -> dict:
    return {
        "id_dossier": id_dossier,
        "type_scenario": "CONSULTATION",
        "id_beneficiaire": "BEN-001",
        "id_formation": id_formation,
        "id_contrat_payeur": "CTR-001",
        "circuit_remboursement": "AMU_SEUL",
        "date_soins": "2026-08-26",
        "cloture_triple_trait": True,
        "actes": [
            {
                "id_acte": "ACT-001",
                "id_dossier": id_dossier,
                "id_prescripteur": "PRE-001",
                "code_acte": "C",
                "diagnostic_cim10": "J06.9",
                "date_realisation": "2026-08-26",
                "montant_facture": 7000,
            }
        ],
        "medicaments": [],
    }


class TestSante:
    def test_health_check(self, client) -> None:
        reponse = client.get("/health")
        assert reponse.status_code == 200
        assert reponse.json() == {"statut": "ok"}


class TestAuthentification:
    """Cf. section 8.3 -- aucune route metier ne doit etre accessible sans
    jeton valide."""

    def test_soumission_sans_entete_authorization_retourne_401(self, client) -> None:
        reponse = client.post("/api/v1/dossiers", json=_corps_dossier_conforme())
        assert reponse.status_code == 401

    def test_soumission_avec_jeton_invalide_retourne_401(self, client) -> None:
        reponse = client.post(
            "/api/v1/dossiers",
            json=_corps_dossier_conforme(),
            headers={"Authorization": "Bearer jeton-qui-n-existe-pas"},
        )
        assert reponse.status_code == 401

    def test_entete_mal_forme_retourne_401(self, client) -> None:
        reponse = client.post(
            "/api/v1/dossiers",
            json=_corps_dossier_conforme(),
            headers={"Authorization": "PasBearer xyz"},
        )
        assert reponse.status_code == 401

    def test_consultation_sans_jeton_retourne_401(self, client) -> None:
        reponse = client.get("/api/v1/dossiers/DOS-INEXISTANT")
        assert reponse.status_code == 401


class TestSoumissionDossier:
    def test_soumission_conforme_retourne_200(self, client) -> None:
        reponse = client.post(
            "/api/v1/dossiers", json=_corps_dossier_conforme(), headers=_entete()
        )
        assert reponse.status_code == 200
        corps = reponse.json()
        assert corps["dossier_id"] == "DOS-API-001"
        assert "piliers" in corps
        assert "motifs" in corps

    def test_soumission_avec_r68_reste_un_200(self, client) -> None:
        """Cf. section 12.7 -- une decision defavorable n'est jamais une
        erreur HTTP."""
        payload = _corps_dossier_conforme("DOS-API-002")
        payload["actes"][0]["diagnostic_cim10"] = "R68"
        reponse = client.post("/api/v1/dossiers", json=payload, headers=_entete())

        assert reponse.status_code == 200
        corps = reponse.json()
        assert corps["statut"] == "AUDIT"
        assert corps["piliers"]["coherence_documentaire"] == "ANOMALIE"

    def test_champ_obligatoire_manquant_retourne_422(self, client) -> None:
        payload = _corps_dossier_conforme()
        del payload["id_beneficiaire"]
        reponse = client.post("/api/v1/dossiers", json=payload, headers=_entete())
        assert reponse.status_code == 422

    def test_resoumission_meme_id_retourne_409(self, client) -> None:
        payload = _corps_dossier_conforme("DOS-API-003")
        premiere = client.post("/api/v1/dossiers", json=payload, headers=_entete())
        assert premiere.status_code == 200

        deuxieme = client.post("/api/v1/dossiers", json=payload, headers=_entete())
        assert deuxieme.status_code == 409


class TestPorteeParCentreRBAC:
    """Cf. F4/F5 (section 8.2) -- un centre ne peut jamais agir au nom d'un
    autre, meme par erreur d'integration cote client."""

    def test_soumission_pour_une_autre_formation_retourne_403(self, client) -> None:
        """Le jeton FS-001 tente de soumettre un dossier declare pour FS-002."""
        payload = _corps_dossier_conforme("DOS-API-010", id_formation="FS-002")
        reponse = client.post("/api/v1/dossiers", json=payload, headers=_entete(JETON_CAB_001))
        assert reponse.status_code == 403

    def test_consultation_d_un_dossier_d_un_autre_centre_retourne_404(self, client) -> None:
        """Cf. Privacy by Design (section 8.1) : 404 plutot que 403, pour ne
        pas confirmer l'existence d'un dossier de sante a qui n'y a pas droit."""
        payload = _corps_dossier_conforme("DOS-API-011", id_formation="FS-001")
        client.post("/api/v1/dossiers", json=payload, headers=_entete(JETON_CAB_001))

        reponse = client.get("/api/v1/dossiers/DOS-API-011", headers=_entete(JETON_CAB_002))
        assert reponse.status_code == 404

    def test_medecin_conseil_peut_consulter_un_dossier_d_un_autre_centre(self, client) -> None:
        """Cf. F4 : le Medecin_Conseil dispose d'un acces en lecture large,
        conforme au Decret n2023-100/PR art. 6 -- seule exception a la
        portee stricte par centre, et seulement en lecture."""
        payload = _corps_dossier_conforme("DOS-API-012", id_formation="FS-001")
        client.post("/api/v1/dossiers", json=payload, headers=_entete(JETON_CAB_001))

        reponse = client.get("/api/v1/dossiers/DOS-API-012", headers=_entete(JETON_MEDECIN_CONSEIL))
        assert reponse.status_code == 200

    def test_medecin_conseil_ne_peut_pas_soumettre_pour_un_centre(self, client) -> None:
        """La lecture large de F4 ne s'etend jamais a la soumission -- ce
        n'est pas une derogation generale, seulement un droit de lecture."""
        payload = _corps_dossier_conforme("DOS-API-013", id_formation="FS-001")
        reponse = client.post(
            "/api/v1/dossiers", json=payload, headers=_entete(JETON_MEDECIN_CONSEIL)
        )
        assert reponse.status_code == 403


class TestConsultationDossier:
    def test_get_apres_post_retourne_le_meme_resultat(self, client) -> None:
        payload = _corps_dossier_conforme("DOS-API-004")
        reponse_post = client.post("/api/v1/dossiers", json=payload, headers=_entete())
        reponse_get = client.get("/api/v1/dossiers/DOS-API-004", headers=_entete())

        assert reponse_get.status_code == 200
        assert reponse_get.json() == reponse_post.json()

    def test_get_dossier_inexistant_retourne_404(self, client) -> None:
        reponse = client.get("/api/v1/dossiers/DOS-INEXISTANT", headers=_entete())
        assert reponse.status_code == 404


class TestIntegrationConnecteurViaAPI:
    """Confirme que la substitution du connecteur (dependency override, le
    mecanisme idiomatique FastAPI) atteint bien le pipeline complet --
    eligibilite defavorable et panne simulee, jusqu'a la reponse HTTP."""

    def test_eligibilite_suspendue_donne_audit_via_api(self, client) -> None:
        connecteur = SimulateurConnecteurPayeur()
        connecteur.configurer_eligibilite(
            "BEN-001", ResultatEligibilite(statut=StatutEligibilite.SUSPENDU)
        )
        app.dependency_overrides[get_connecteur_payeur] = lambda: connecteur

        reponse = client.post(
            "/api/v1/dossiers", json=_corps_dossier_conforme("DOS-API-005"), headers=_entete()
        )

        assert reponse.status_code == 200
        corps = reponse.json()
        assert corps["statut"] == "AUDIT"
        assert corps["piliers"]["coherence_regime"] == "ANOMALIE"

    def test_panne_connecteur_donne_en_validation_locale_via_api(self, client) -> None:
        connecteur = SimulateurConnecteurPayeur(disponible=False)
        app.dependency_overrides[get_connecteur_payeur] = lambda: connecteur

        reponse = client.post(
            "/api/v1/dossiers", json=_corps_dossier_conforme("DOS-API-006"), headers=_entete()
        )

        assert reponse.status_code == 200
        corps = reponse.json()
        assert corps["statut"] == "EN_VALIDATION_LOCALE"
        assert corps["decision_finale"] is None
