"""Simulateur de connecteur payeur -- section 19.5 (tests d'integration
connecteur).

Implemente IConnecteurPayeur avec un comportement entierement configurable :
disponibilite (pour simuler une panne et declencher le Mode Degrade,
section 7), reponses d'eligibilite, bases de remboursement, statuts de PEC.

Principe de securite retenu par defaut : **fail closed**, pas fail open.
Une reference inconnue (beneficiaire, acte, PEC) ne doit jamais etre
interpretee par defaut comme favorable -- c'est le meme esprit que F7
(section 8.2) : en l'absence d'information positive, ne jamais presumer un
accord.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from fhtp_core.connectors.exceptions import ConnecteurIndisponible
from fhtp_core.connectors.payeur import (
    BaseRemboursement,
    ResultatEligibilite,
    ResultatSoumissionFacture,
)
from fhtp_core.models.dossier import Dossier
from fhtp_core.models.enums import (
    StatutBaseRemboursement,
    StatutEligibilite,
    StatutPEC,
    StatutSoumissionFacture,
    TypeTarification,
)


class SimulateurConnecteurPayeur:
    def __init__(
        self,
        *,
        mode_tarification: TypeTarification = TypeTarification.MODE_ACTE,
        disponible: bool = True,
    ) -> None:
        self.mode_tarification = mode_tarification
        self.disponible = disponible

        self._eligibilites: dict[str, ResultatEligibilite] = {}
        self._bases_remboursement: dict[str, BaseRemboursement] = {}
        self._pecs: dict[str, StatutPEC] = {}
        self._resultats_soumission: dict[str, ResultatSoumissionFacture] = {}

        # Journal des appels -- pratique pour verifier dans les tests que le
        # connecteur a bien ete sollicite, sans dupliquer cette logique dans
        # chaque test.
        self.appels: list[str] = []

    # --- Configuration (utilisee depuis les tests) ------------------------

    def configurer_eligibilite(self, beneficiaire_id: str, resultat: ResultatEligibilite) -> None:
        self._eligibilites[beneficiaire_id] = resultat

    def configurer_base_remboursement(self, code: str, base: BaseRemboursement) -> None:
        self._bases_remboursement[code] = base

    def configurer_pec(self, numero_reference: str, statut: StatutPEC) -> None:
        self._pecs[numero_reference] = statut

    def configurer_resultat_soumission(
        self, dossier_id: str, resultat: ResultatSoumissionFacture
    ) -> None:
        self._resultats_soumission[dossier_id] = resultat

    def definir_disponible(self, disponible: bool) -> None:
        """Bascule la disponibilite simulee -- pour tester le declenchement
        du Mode Degrade (section 7) sur une panne payeur."""
        self.disponible = disponible

    # --- Implementation IConnecteurPayeur ----------------------------------

    def _verifier_disponibilite(self) -> None:
        if not self.disponible:
            raise ConnecteurIndisponible("Connecteur payeur simule marque indisponible")

    def verifier_eligibilite(
        self, identifiant_beneficiaire: str, date_soins: date
    ) -> ResultatEligibilite:
        self.appels.append(f"verifier_eligibilite({identifiant_beneficiaire})")
        self._verifier_disponibilite()
        return self._eligibilites.get(
            identifiant_beneficiaire,
            ResultatEligibilite(statut=StatutEligibilite.INCONNU),
        )

    def obtenir_base_remboursement(
        self, code_acte_ou_dci: str, date_soins: date
    ) -> BaseRemboursement:
        self.appels.append(f"obtenir_base_remboursement({code_acte_ou_dci})")
        self._verifier_disponibilite()
        return self._bases_remboursement.get(
            code_acte_ou_dci,
            BaseRemboursement(statut=StatutBaseRemboursement.NON_COUVERT),
        )

    def soumettre_facture(self, dossier: Dossier) -> ResultatSoumissionFacture:
        self.appels.append(f"soumettre_facture({dossier.id_dossier})")
        self._verifier_disponibilite()
        return self._resultats_soumission.get(
            dossier.id_dossier,
            ResultatSoumissionFacture(statut=StatutSoumissionFacture.EN_ATTENTE),
        )

    def verifier_pec(self, numero_reference: str) -> StatutPEC:
        self.appels.append(f"verifier_pec({numero_reference})")
        self._verifier_disponibilite()
        # Fail closed : une reference inconnue n'est jamais presumee
        # ACCORDE -- c'est exactement la faille corrigee par F7.
        return self._pecs.get(numero_reference, StatutPEC.REFUSE)
