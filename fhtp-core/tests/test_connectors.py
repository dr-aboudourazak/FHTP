"""Tests des contrats de connecteurs -- section 3, et de leurs simulateurs
(section 19.5).

Trois choses verifiees : (1) le simulateur respecte bien le contrat
Protocol, (2) le comportement fail-closed par defaut (F7, section 8.2),
(3) le declenchement de ConnecteurIndisponible en cas de panne simulee --
c'est ce signal precis qui doit, cote appelant, provoquer un basculement en
Mode Degrade (section 7), jamais une exception generique.
"""

from datetime import date, datetime

import pytest

from fhtp_core.connectors import ConnecteurIndisponible, IConnecteurPayeur, IConnecteurTerrain
from fhtp_core.connectors.payeur import BaseRemboursement, ResultatEligibilite
from fhtp_core.connectors.simulateur_payeur import SimulateurConnecteurPayeur
from fhtp_core.connectors.simulateur_terrain import SimulateurConnecteurTerrain
from fhtp_core.models.dossier import ActeRealise, Dossier
from fhtp_core.models.enums import (
    CircuitRemboursement,
    StatutBaseRemboursement,
    StatutDossier,
    StatutEligibilite,
    StatutPEC,
    TypeScenario,
)


def _dossier_test() -> Dossier:
    return Dossier(
        id_dossier="DOS-2026-000300",
        type_scenario=TypeScenario.CONSULTATION,
        id_beneficiaire="BEN-001",
        id_formation="FS-001",
        id_contrat_payeur="CTR-001",
        circuit_remboursement=CircuitRemboursement.AMU_SEUL,
        date_soins=date(2026, 8, 25),
        date_soumission=datetime(2026, 8, 25, 10, 0, 0),
    )


class TestConformiteAuProtocole:
    """Le simulateur doit satisfaire les Protocol runtime_checkable --
    garantit qu'un futur vrai connecteur INAM/CAT devra faire de meme."""

    def test_simulateur_payeur_respecte_le_protocole(self) -> None:
        assert isinstance(SimulateurConnecteurPayeur(), IConnecteurPayeur)

    def test_simulateur_terrain_respecte_le_protocole(self) -> None:
        assert isinstance(SimulateurConnecteurTerrain(), IConnecteurTerrain)


class TestSimulateurPayeurComportementNormal:
    def test_eligibilite_configuree_est_retournee(self) -> None:
        connecteur = SimulateurConnecteurPayeur()
        connecteur.configurer_eligibilite(
            "BEN-001",
            ResultatEligibilite(
                statut=StatutEligibilite.ACTIF, taux_couverture=0.8, ticket_moderateur_pct=0.2
            ),
        )
        resultat = connecteur.verifier_eligibilite("BEN-001", date(2026, 8, 25))
        assert resultat.statut == StatutEligibilite.ACTIF
        assert resultat.taux_couverture == 0.8

    def test_beneficiaire_inconnu_retourne_inconnu_pas_actif(self) -> None:
        """Fail closed : un beneficiaire non configure ne doit jamais etre
        traite comme ACTIF par defaut."""
        connecteur = SimulateurConnecteurPayeur()
        resultat = connecteur.verifier_eligibilite("BEN-INEXISTANT", date(2026, 8, 25))
        assert resultat.statut == StatutEligibilite.INCONNU

    def test_appels_sont_journalises(self) -> None:
        connecteur = SimulateurConnecteurPayeur()
        connecteur.verifier_eligibilite("BEN-001", date(2026, 8, 25))
        assert any("verifier_eligibilite" in a for a in connecteur.appels)


class TestSimulateurPayeurIndisponibilite:
    """Cf. section 7 -- c'est ce signal qui doit declencher le Mode Degrade
    cote appelant."""

    @pytest.mark.parametrize(
        "methode,args",
        [
            ("verifier_eligibilite", ("BEN-001", date(2026, 8, 25))),
            ("obtenir_base_remboursement", ("C", date(2026, 8, 25))),
            ("verifier_pec", ("PEC-001",)),
        ],
    )
    def test_chaque_methode_leve_indisponible_si_panne(self, methode, args) -> None:
        connecteur = SimulateurConnecteurPayeur(disponible=False)
        with pytest.raises(ConnecteurIndisponible):
            getattr(connecteur, methode)(*args)

    def test_soumettre_facture_leve_indisponible_si_panne(self) -> None:
        connecteur = SimulateurConnecteurPayeur(disponible=False)
        with pytest.raises(ConnecteurIndisponible):
            connecteur.soumettre_facture(_dossier_test())

    def test_bascule_disponible_indisponible_dynamique(self) -> None:
        """Un test doit pouvoir simuler une panne survenant en cours de
        route (ex: coupure pendant une session), pas seulement une panne
        fixee a la construction."""
        connecteur = SimulateurConnecteurPayeur()
        connecteur.verifier_eligibilite("BEN-001", date(2026, 8, 25))  # OK

        connecteur.definir_disponible(False)
        with pytest.raises(ConnecteurIndisponible):
            connecteur.verifier_eligibilite("BEN-001", date(2026, 8, 25))

        connecteur.definir_disponible(True)
        connecteur.verifier_eligibilite("BEN-001", date(2026, 8, 25))  # de nouveau OK


class TestVerificationPECFailClosed:
    """Cf. F7 (section 8.2) -- jamais de validation d'une PEC sur la seule
    presence d'un numero, et jamais de presomption d'accord par defaut."""

    def test_pec_configuree_accordee(self) -> None:
        connecteur = SimulateurConnecteurPayeur()
        connecteur.configurer_pec("PEC-100", StatutPEC.ACCORDE)
        assert connecteur.verifier_pec("PEC-100") == StatutPEC.ACCORDE

    def test_pec_inconnue_est_refusee_par_defaut(self) -> None:
        """C'est le coeur du principe fail-closed : un numero de PEC
        plausible mais jamais configure (jamais reellement accorde par le
        payeur) ne doit jamais passer -- exactement l'incident du CHR
        Dapaong en miroir (FHTP-KNO-001, section 6.1)."""
        connecteur = SimulateurConnecteurPayeur()
        assert connecteur.verifier_pec("PEC-INVENTEE-PAR-FRAUDE") == StatutPEC.REFUSE


class TestSimulateurTerrain:
    def test_actes_du_jour_configures(self) -> None:
        connecteur = SimulateurConnecteurTerrain()
        acte = ActeRealise(
            id_acte="ACT-001",
            id_dossier="DOS-001",
            id_prescripteur="PRE-001",
            code_acte="C",
            diagnostic_cim10="J06.9",
            date_realisation=date(2026, 8, 25),
            montant_facture=7000,
        )
        connecteur.configurer_actes_du_jour("FS-001", date(2026, 8, 25), [acte])
        resultat = connecteur.obtenir_actes_du_jour("FS-001", date(2026, 8, 25))
        assert resultat == [acte]

    def test_notification_est_journalisee(self) -> None:
        connecteur = SimulateurConnecteurTerrain()
        connecteur.envoyer_statut_validation("DOS-001", StatutDossier.FAST_TRACK, [])
        assert connecteur.notifications_envoyees == [("DOS-001", StatutDossier.FAST_TRACK, [])]

    def test_indisponible_leve_exception(self) -> None:
        connecteur = SimulateurConnecteurTerrain(disponible=False)
        with pytest.raises(ConnecteurIndisponible):
            connecteur.obtenir_actes_du_jour("FS-001", date(2026, 8, 25))
