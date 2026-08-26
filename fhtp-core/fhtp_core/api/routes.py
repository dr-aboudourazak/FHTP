"""Routes HTTP -- FHTP-ARC-001, section 12.3.

Rappel du principe pose en section 12.7 : une decision defavorable du
moteur de regles (REJET, AUDIT_APPROFONDI, CONTROLE_RAPIDE) n'est JAMAIS une
erreur HTTP -- toujours un 200 normal, avec `statut`/`decision_finale`
simplement defavorables dans le corps de la reponse. Un code d'erreur ne
concerne que l'acces a l'API elle-meme (auth, format, conflit), jamais le
contenu metier d'un dossier.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from fhtp_core.api.dependencies import get_connecteur_payeur, get_gestionnaire, get_store
from fhtp_core.api.schemas import DossierSoumission, ReponseDossier
from fhtp_core.connectors.payeur import IConnecteurPayeur
from fhtp_core.engine.gestionnaire_dossiers import GestionnaireDossiers
from fhtp_core.models.dossier import Dossier

router = APIRouter(prefix="/api/v1", tags=["dossiers"])


@router.post("/dossiers", response_model=ReponseDossier)
def soumettre_dossier(
    payload: DossierSoumission,
    gestionnaire: GestionnaireDossiers = Depends(get_gestionnaire),
    connecteur: IConnecteurPayeur = Depends(get_connecteur_payeur),
    store: dict[str, Dossier] = Depends(get_store),
) -> ReponseDossier:
    if payload.id_dossier in store:
        # Meme principe d'idempotence que la soumission groupee (section
        # 14.5) : une resoumission avec le meme identifiant n'ecrase jamais
        # silencieusement l'evaluation precedente. Un vrai flux de
        # correction doit passer par un nouvel identifiant, ou par un
        # mecanisme de remplacement explicite -- pas encore specifie ici.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Un dossier {payload.id_dossier!r} existe deja. Resoumission "
                "refusee pour eviter tout double traitement."
            ),
        )

    dossier = payload.vers_dossier()
    resultat = gestionnaire.soumettre_avec_verification_payeur(
        dossier, connecteur, operateur_id="API"
    )
    store[resultat.id_dossier] = resultat
    return ReponseDossier.depuis_dossier(resultat)


@router.get("/dossiers/{dossier_id}", response_model=ReponseDossier)
def obtenir_dossier(
    dossier_id: str, store: dict[str, Dossier] = Depends(get_store)
) -> ReponseDossier:
    dossier = store.get(dossier_id)
    if dossier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dossier introuvable"
        )
    return ReponseDossier.depuis_dossier(dossier)
