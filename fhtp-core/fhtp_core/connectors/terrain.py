"""Contrat generique des connecteurs terrain -- FHTP-ARC-001, section 3.2.

Un connecteur terrain (SIH, logiciel d'officine) traduit les donnees
proprietaires du logiciel existant vers le modele generique de FHTP Core --
FHTP s'integre au terrain, il ne le remplace pas (FHTP-KNO-001, section 3.5).
"""

from __future__ import annotations

from datetime import date
from typing import Protocol, runtime_checkable

from fhtp_core.models.dossier import ActeRealise
from fhtp_core.models.enums import StatutDossier


@runtime_checkable
class IConnecteurTerrain(Protocol):
    """Contrat que tout connecteur terrain doit implementer (section 3.2)."""

    def obtenir_actes_du_jour(self, formation_id: str, jour: date) -> list[ActeRealise]:
        """Utilise pour le recoupement avec la facture soumise.

        Leve ConnecteurIndisponible si le logiciel terrain est injoignable."""
        ...

    def envoyer_statut_validation(
        self, dossier_id: str, statut: StatutDossier, motifs: list[str]
    ) -> None:
        """Notifie le logiciel terrain du resultat de validation FHTP.

        Leve ConnecteurIndisponible si le logiciel terrain est injoignable
        -- une notification non delivree ne doit jamais etre confondue avec
        une notification refusee."""
        ...
