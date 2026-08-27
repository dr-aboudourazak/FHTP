"""Routes HTTP -- FHTP-ARC-001, section 12.3.

Rappel du principe pose en section 12.7 : une decision defavorable du
moteur de regles (REJET, AUDIT_APPROFONDI, CONTROLE_RAPIDE) n'est JAMAIS une
erreur HTTP -- toujours un 200 normal, avec `statut`/`decision_finale`
simplement defavorables dans le corps de la reponse. Un code d'erreur ne
concerne que l'acces a l'API elle-meme (auth, format, conflit, portee),
jamais le contenu metier d'un dossier.

Controle d'acces (F4/F5, section 8.2) : chaque jeton est scope a une
formation sanitaire precise. Un operateur ne peut soumettre que pour sa
propre formation ; il ne peut consulter que ses propres dossiers, sauf role
MEDECIN_CONSEIL qui dispose d'un acces en lecture large (F4 : "acces en
lecture large + declenchement de controle", conforme au Decret
n2023-100/PR art. 6).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from fhtp_core.api.auth import ContexteOperateur, RoleRBAC
from fhtp_core.api.dependencies import get_connecteur_payeur, get_gestionnaire, get_store, obtenir_operateur_courant
from fhtp_core.api.schemas import DossierSoumission, ReponseDossier
from fhtp_core.connectors.payeur import IConnecteurPayeur
from fhtp_core.engine.gestionnaire_dossiers import GestionnaireDossiers
from fhtp_core.models.dossier import Dossier

router = APIRouter(prefix="/api/v1", tags=["dossiers"])


@router.post("/dossiers", response_model=ReponseDossier)
def soumettre_dossier(
    payload: DossierSoumission,
    operateur: ContexteOperateur = Depends(obtenir_operateur_courant),
    gestionnaire: GestionnaireDossiers = Depends(get_gestionnaire),
    connecteur: IConnecteurPayeur = Depends(get_connecteur_payeur),
    store: dict[str, Dossier] = Depends(get_store),
) -> ReponseDossier:
    if payload.id_formation != operateur.id_formation:
        # Cf. F5 (section 8.2) : chaque credential est scope au strict
        # necessaire, un centre ne peut jamais agir au nom d'un autre --
        # meme role MEDECIN_CONSEIL n'a pas de derogation ici, sa lecture
        # large (F4) ne concerne que la consultation, jamais la soumission.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Ce jeton n'est pas habilite pour la formation sanitaire "
                f"{payload.id_formation!r}."
            ),
        )

    if payload.id_dossier in store:
        # Meme principe d'idempotence que la soumission groupee (section
        # 14.5) : une resoumission avec le meme identifiant n'ecrase jamais
        # silencieusement l'evaluation precedente.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Un dossier {payload.id_dossier!r} existe deja. Resoumission "
                "refusee pour eviter tout double traitement."
            ),
        )

    dossier = payload.vers_dossier()
    resultat = gestionnaire.soumettre_avec_verification_payeur(
        dossier, connecteur, operateur_id=operateur.operateur_id
    )
    store[resultat.id_dossier] = resultat
    return ReponseDossier.depuis_dossier(resultat)


@router.get("/dossiers/{dossier_id}", response_model=ReponseDossier)
def obtenir_dossier(
    dossier_id: str,
    operateur: ContexteOperateur = Depends(obtenir_operateur_courant),
    store: dict[str, Dossier] = Depends(get_store),
) -> ReponseDossier:
    dossier = store.get(dossier_id)
    if dossier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dossier introuvable"
        )

    a_acces_large = operateur.role == RoleRBAC.MEDECIN_CONSEIL
    if not a_acces_large and dossier.id_formation != operateur.id_formation:
        # 404 plutot que 403 ici, deliberement : confirmer qu'un dossier
        # d'un AUTRE centre existe a quelqu'un qui n'y a pas droit est deja
        # une fuite d'information sur des donnees de sante -- coherent avec
        # Privacy by Design (section 8.1).
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dossier introuvable"
        )

    return ReponseDossier.depuis_dossier(dossier)
