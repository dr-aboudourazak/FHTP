"""Authentification et RBAC -- FHTP-ARC-001, section 8.3 (authentification)
et F4/section 8.2 (controle d'acces base sur les roles reels du terrain).

Ceci est un mecanisme SIMPLIFIE, pas le jeton OAuth2 Bearer emis/tourne
decrit en section 8.3, ni le coffre-fort de secrets exige par F5 (section
8.2). Un vrai systeme d'emission, de rotation et de stockage securise des
identifiants reste a construire avant tout usage au-dela des tests et
demonstrations -- ce module pose la structure du controle d'acces (roles
reels, portee par centre) sans encore l'infrastructure de production qui
doit l'entourer. Aucun jeton de demonstration n'est code en dur ici : c'est
a chaque environnement (tests, ou plus tard un vrai service) de les
enregistrer explicitement via `AnnuaireJetons.enregistrer`.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel


class RoleRBAC(str, Enum):
    """Cf. F4 (section 8.2) -- roles reels du terrain, jamais un role
    generique unique."""

    OPERATEUR_SAISIE = "OPERATEUR_SAISIE"
    PRESCRIPTEUR = "PRESCRIPTEUR"
    MEDECIN_CONSEIL = "MEDECIN_CONSEIL"
    ADMINISTRATEUR_CENTRE = "ADMINISTRATEUR_CENTRE"


class ContexteOperateur(BaseModel):
    operateur_id: str
    id_formation: str
    role: RoleRBAC


class AnnuaireJetons:
    """Registre en memoire jeton -> contexte operateur.

    Tient lieu d'annuaire d'identite pour les tests et la demonstration --
    remplace, en beaucoup plus simple, un vrai systeme d'emission/
    verification de jetons signes (section 8.3)."""

    def __init__(self) -> None:
        self._jetons: dict[str, ContexteOperateur] = {}

    def enregistrer(self, jeton: str, contexte: ContexteOperateur) -> None:
        self._jetons[jeton] = contexte

    def resoudre(self, jeton: str) -> Optional[ContexteOperateur]:
        return self._jetons.get(jeton)

    def reinitialiser(self) -> None:
        self._jetons.clear()


# auto_error=False : on gere nous-memes l'erreur (401, pas le 403 par defaut
# de HTTPBearer) pour rester coherent avec le reste de l'API (section 12.7 --
# les codes d'erreur ont un sens precis, pas interchangeable).
_schema_bearer = HTTPBearer(auto_error=False, description="Jeton d'operateur (section 8.3)")


def construire_dependance_authentification(annuaire: AnnuaireJetons):
    """Construit la dependance FastAPI d'authentification, liee a un
    annuaire de jetons precis -- evite une dependance globale figee au
    moment de l'import, pour que les tests puissent utiliser un annuaire
    frais a chaque fois sans se marcher dessus.

    Utilise `HTTPBearer` (plutot qu'un simple en-tete lu a la main) pour que
    l'interface `/docs` generee par FastAPI affiche un bouton "Authorize"
    utilisable directement, sans devoir retaper l'en-tete a chaque requete
    de test manuel.
    """

    def obtenir_operateur_courant(
        identifiants: Optional[HTTPAuthorizationCredentials] = Depends(_schema_bearer),
    ) -> ContexteOperateur:
        if identifiants is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="En-tete 'Authorization: Bearer <jeton>' requis",
            )
        contexte = annuaire.resoudre(identifiants.credentials)
        if contexte is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Jeton invalide ou inconnu",
            )
        return contexte

    return obtenir_operateur_courant
