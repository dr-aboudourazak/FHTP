"""Moteur de regles a six piliers -- FHTP-ARC-001, section 2.1.

Ce module fait le pont entre le referentiel de regles (fhtp_core.rules) et le
Dossier : il evalue chaque regle applicable, et remplit `evaluation_piliers`
avec un statut par pilier -- exactement la donnee que `fhtp_core.engine.decision`
suppose deja disponible.

Logique de decision par pilier (section 2.1) :
    - Si une regle du pilier retourne REJET (condition vraie)   -> ANOMALIE, fail-fast
    - Sinon si une regle du pilier retourne ATTENTION            -> A_VERIFIER
    - Sinon si aucune regle du pilier n'est applicable au dossier -> NON_EVALUE
    - Sinon (regles applicables, aucune declenchee)              -> CONFORME
"""

from __future__ import annotations

from fhtp_core.models.dossier import Dossier
from fhtp_core.models.enums import Pilier, StatutPilier
from fhtp_core.rules.conditions import evaluer
from fhtp_core.rules.models import Regle


class ResultatEvaluation:
    """Resultat de l'evaluation d'une regle sur une ligne (acte/medicament)
    ou sur le dossier entier."""

    __slots__ = ("regle", "declenchee")

    def __init__(self, regle: Regle, declenchee: bool) -> None:
        self.regle = regle
        self.declenchee = declenchee


def _regle_applicable(regle: Regle, dossier: Dossier) -> bool:
    return (
        dossier.circuit_remboursement in regle.circuit
        and dossier.type_scenario in regle.scenario
    )


def _contextes_pour_regle(regle: Regle, dossier: Dossier) -> list[dict]:
    """Determine sur quelles lignes une regle doit etre evaluee, d'apres les
    variables qu'elle reference dans sa condition.

    Une regle qui reference "acte." est evaluee une fois par acte du
    dossier ; une regle qui reference "medicament." une fois par medicament ;
    une regle qui ne reference que "dossier." est evaluee une seule fois.
    Ce decoupage evite d'avoir a declarer explicitement la portee de chaque
    regle dans le referentiel -- elle se deduit de sa propre condition.
    """
    condition = regle.condition
    if "medicament." in condition:
        return [{"dossier": dossier, "medicament": m} for m in dossier.medicaments]
    if "acte." in condition:
        return [{"dossier": dossier, "acte": a} for a in dossier.actes]
    return [{"dossier": dossier}]


def evaluer_regle(regle: Regle, dossier: Dossier) -> list[ResultatEvaluation]:
    """Evalue une regle sur chaque contexte pertinent (acte, medicament, ou
    dossier seul) et retourne un resultat par contexte."""
    resultats = []
    for contexte in _contextes_pour_regle(regle, dossier):
        declenchee = evaluer(regle.condition, contexte)
        resultats.append(ResultatEvaluation(regle=regle, declenchee=declenchee))
    return resultats


def evaluer_dossier(dossier: Dossier, regles: list[Regle]) -> Dossier:
    """Evalue l'ensemble du referentiel de regles applicable au dossier et
    retourne une copie du dossier avec `evaluation_piliers` et
    `motifs_rejet` remplis.

    Ne modifie jamais le dossier en place -- retourne une nouvelle instance,
    coherent avec le style immuable deja utilise dans fhtp_core.engine.decision.
    """
    regles_applicables = [r for r in regles if _regle_applicable(r, dossier)]

    statuts_par_pilier: dict[Pilier, StatutPilier] = {}
    motifs: list[str] = []

    for pilier in Pilier:
        regles_du_pilier = [r for r in regles_applicables if r.pilier == pilier]

        if not regles_du_pilier:
            statuts_par_pilier[pilier] = StatutPilier.NON_EVALUE
            continue

        a_une_anomalie = False
        a_verifier = False

        for regle in regles_du_pilier:
            for resultat in evaluer_regle(regle, dossier):
                if not resultat.declenchee:
                    continue
                if regle.action_si_vrai == "REJET":
                    a_une_anomalie = True
                    motifs.append(f"{regle.id}: {regle.description}")
                elif regle.action_si_vrai == "ATTENTION":
                    a_verifier = True
                    motifs.append(f"{regle.id}: {regle.description}")

        if a_une_anomalie:
            statuts_par_pilier[pilier] = StatutPilier.ANOMALIE
        elif a_verifier:
            statuts_par_pilier[pilier] = StatutPilier.A_VERIFIER
        else:
            statuts_par_pilier[pilier] = StatutPilier.CONFORME

    return dossier.model_copy(
        update={"evaluation_piliers": statuts_par_pilier, "motifs_rejet": motifs}
    )
