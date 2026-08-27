"""Modele d'une regle du referentiel -- FHTP-ARC-001, section 2.1.

Chaque regle est parametrable et versionnee, stockee dans un referentiel
(fixtures JSON ici), jamais codee en dur dans le moteur -- c'est le principe
directeur de la section 2.1 : mettre a jour la reglementation sans
refactoring du code.
"""

from __future__ import annotations

from pydantic import BaseModel

from fhtp_core.models.enums import CircuitRemboursement, Pilier, TypeScenario


class ActionRegle(BaseModel):
    """Action produite si la condition est vraie.

    REJET      -> le pilier concerne devient ANOMALIE (fail-fast, section 2.1)
    ATTENTION  -> le pilier concerne devient A_VERIFIER
    """

    type: str  # "REJET" | "ATTENTION"


class Regle(BaseModel):
    id: str  # ex: "R-TG-017"
    version: str
    pilier: Pilier
    circuit: list[CircuitRemboursement]
    scenario: list[TypeScenario]
    description: str
    condition: str  # expression evaluee par fhtp_core.rules.conditions
    action_si_vrai: str  # "REJET" | "ATTENTION"
    message_id: str  # cf. section 13.2 -- resolu via ReferentielLibelle
    source: str
