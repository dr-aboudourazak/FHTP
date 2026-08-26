"""Moteur de decision -- FHTP-ARC-001, section 2.1 (logique de decision).

Ce module prend un Dossier deja evalue pilier par pilier (evaluation_piliers
deja rempli par le moteur de regles, a venir separement) et determine la
decision finale. Il ne contient AUCUNE regle metier (R-TG-xxx, RG-Pxxx...) --
celles-la vivent dans le Referentiel de Regles (fhtp_core.rules), pas ici.

Regle de securite critique -- ADR-003 (section 7.2) :
    Un dossier avec origine_creation = MODE_DEGRADE ne peut JAMAIS recevoir
    FAST_TRACK avant d'avoir ete synchronise et reevalue en ligne. Cette
    contrainte prime sur tout le reste : meme un dossier dont tous les
    piliers sont CONFORME plafonne a EN_VALIDATION_LOCALE tant qu'il reste
    en origine MODE_DEGRADE.

    C'est la correction directe d'une faille identifiee a la relecture de
    l'architecture : sans ce plafond, un operateur malveillant pourrait
    provoquer une coupure reseau locale pour faire passer un dossier
    fabrique en paiement automatique, sachant que la verification reelle
    n'interviendrait qu'apres coup.
"""

from __future__ import annotations

from fhtp_core.models.dossier import Dossier
from fhtp_core.models.enums import DecisionFinale, OrigineCreation, StatutDossier


def decider(dossier: Dossier) -> DecisionFinale | StatutDossier:
    """Determine la decision finale d'un dossier deja evalue.

    Retourne soit une DecisionFinale (FAST_TRACK, CONTROLE_RAPIDE,
    AUDIT_APPROFONDI), soit StatutDossier.EN_VALIDATION_LOCALE dans le cas
    special du mode degrade -- qui n'est PAS une decision finale au sens du
    document maitre, mais un plafond intermediaire (section 7.2).

    Reference : section 2.1, "Logique de Decision".
    """
    # --- Garde-fou ADR-003 : prioritaire sur tout le reste de la logique. ---
    if dossier.origine_creation == OrigineCreation.MODE_DEGRADE:
        return StatutDossier.EN_VALIDATION_LOCALE

    if dossier.a_une_anomalie():
        return DecisionFinale.AUDIT_APPROFONDI

    if dossier.a_verifier_seulement():
        return DecisionFinale.CONTROLE_RAPIDE

    if dossier.tous_piliers_conformes():
        return DecisionFinale.FAST_TRACK

    # Cas residuel (ne devrait pas survenir si les trois branches ci-dessus
    # sont exhaustives) : traite comme A_VERIFIER par prudence plutot que de
    # laisser passer un cas non couvert vers un paiement automatique.
    return DecisionFinale.CONTROLE_RAPIDE


def peut_recevoir_fast_track(dossier: Dossier) -> bool:
    """Fonction de garde explicite, destinee a etre appelee par le point
    d'entree API (section 12) avant tout paiement automatique -- une seconde
    ligne de defense independante de `decider()`, pour que la regle ADR-003
    reste verifiable meme si la logique de decision est modifiee ailleurs.
    """
    if dossier.origine_creation == OrigineCreation.MODE_DEGRADE:
        return False
    return decider(dossier) == DecisionFinale.FAST_TRACK
