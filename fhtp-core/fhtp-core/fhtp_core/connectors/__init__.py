"""Contrats de connecteurs -- FHTP-ARC-001, section 3.

FHTP Core ne connait que ces interfaces generiques, jamais l'implementation
propre a un payeur ou un logiciel terrain (FHTP-KNO-001, section 3.4-3.5).
"""

from fhtp_core.connectors.exceptions import ConnecteurIndisponible
from fhtp_core.connectors.payeur import (
    BaseRemboursement,
    IConnecteurPayeur,
    ResultatEligibilite,
    ResultatSoumissionFacture,
)
from fhtp_core.connectors.terrain import IConnecteurTerrain

__all__ = [
    "BaseRemboursement",
    "ConnecteurIndisponible",
    "IConnecteurPayeur",
    "IConnecteurTerrain",
    "ResultatEligibilite",
    "ResultatSoumissionFacture",
]
