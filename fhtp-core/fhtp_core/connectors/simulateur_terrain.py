"""Simulateur de connecteur terrain -- section 19.5.

Implemente IConnecteurTerrain avec un comportement configurable, pour tester
le recoupement avec un SIH/logiciel d'officine simule sans dependre d'un
vrai systeme externe.
"""

from __future__ import annotations

from datetime import date

from fhtp_core.connectors.exceptions import ConnecteurIndisponible
from fhtp_core.models.dossier import ActeRealise
from fhtp_core.models.enums import StatutDossier


class SimulateurConnecteurTerrain:
    def __init__(self, *, disponible: bool = True) -> None:
        self.disponible = disponible
        self._actes_du_jour: dict[tuple[str, date], list[ActeRealise]] = {}

        # Journal des notifications envoyees -- pour verifier dans les
        # tests que le logiciel terrain a bien ete notifie du resultat.
        self.notifications_envoyees: list[tuple[str, StatutDossier, list[str]]] = []

    def configurer_actes_du_jour(
        self, formation_id: str, jour: date, actes: list[ActeRealise]
    ) -> None:
        self._actes_du_jour[(formation_id, jour)] = actes

    def definir_disponible(self, disponible: bool) -> None:
        self.disponible = disponible

    def _verifier_disponibilite(self) -> None:
        if not self.disponible:
            raise ConnecteurIndisponible("Connecteur terrain simule marque indisponible")

    def obtenir_actes_du_jour(self, formation_id: str, jour: date) -> list[ActeRealise]:
        self._verifier_disponibilite()
        return self._actes_du_jour.get((formation_id, jour), [])

    def envoyer_statut_validation(
        self, dossier_id: str, statut: StatutDossier, motifs: list[str]
    ) -> None:
        self._verifier_disponibilite()
        self.notifications_envoyees.append((dossier_id, statut, motifs))
