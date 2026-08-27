"""Exceptions communes aux connecteurs payeur et terrain -- section 3.

ConnecteurIndisponible est l'exception que tout connecteur reel doit lever
en cas d'echec (timeout, panne, erreur HTTP 5xx...). C'est elle que le
gestionnaire de dossiers doit intercepter pour basculer en Mode Degrade
(section 7) -- jamais une exception generique qui masquerait la distinction
entre "le payeur a repondu NON" et "le payeur n'a pas repondu du tout".
"""

from __future__ import annotations


class ConnecteurIndisponible(RuntimeError):
    """Le connecteur n'a pas pu joindre le systeme externe (reseau, panne,
    timeout). Distincte d'une reponse metier defavorable (ex: eligibilite
    SUSPENDU) -- une indisponibilite declenche le mode degrade (section 7),
    une reponse defavorable declenche une decision normale du moteur de
    regles."""
