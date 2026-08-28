"""Application FastAPI -- FHTP-ARC-001, section 12.

Point d'entree unique de l'API Directe FHTP Core (section 12.2), distincte
des Connecteurs Terrain (section 3.2/5) : c'est la porte que tout le monde
utilise, y compris un centre qui n'a jamais entendu parler d'un SIH.
"""

from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from fhtp_core.api.dependencies import get_annuaire_jetons
from fhtp_core.api.routes import router


def _mode_demo_actif() -> bool:
    """Actif par defaut -- se desactive explicitement avec FHTP_DEMO=0,
    pas l'inverse. Coherent avec le stade actuel du projet (aucun vrai
    systeme d'emission de jetons encore construit, cf. JOURNAL_DEV.md)."""
    return os.environ.get("FHTP_DEMO", "1") != "0"


@asynccontextmanager
async def _cycle_de_vie(app: FastAPI):
    if _mode_demo_actif():
        from fhtp_core.api.demo import JETONS_DEMO, activer_donnees_demo

        activer_donnees_demo(get_annuaire_jetons())

        bandeau = [
            "",
            "=" * 72,
            "MODE DEMO ACTIF -- jetons non securises, JAMAIS en production",
            "Desactiver : variable d'environnement FHTP_DEMO=0 avant de lancer uvicorn",
            "-" * 72,
            "Jetons disponibles (a coller dans le bouton Authorize de /docs) :",
        ]
        for jeton, contexte in JETONS_DEMO.items():
            bandeau.append(
                f"  {jeton}   (role={contexte.role.value}, "
                f"formation={contexte.id_formation})"
            )
        bandeau.append("=" * 72)
        bandeau.append("")
        print("\n".join(bandeau), file=sys.stderr)

    yield  # l'application tourne ; rien a nettoyer a l'arret pour l'instant


app = FastAPI(
    title="FHTP Core API",
    version="0.1.0",
    description=(
        "Exposition directe de FHTP Core (section 12). Toute decision "
        "defavorable (REJET, AUDIT_APPROFONDI, CONTROLE_RAPIDE) est une "
        "reponse HTTP 200 normale -- un code d'erreur ne concerne que "
        "l'acces a l'API elle-meme, jamais le contenu metier d'un dossier "
        "(section 12.7)."
    ),
    lifespan=_cycle_de_vie,
)

app.include_router(router)


@app.get("/health", tags=["infra"])
def sante() -> dict[str, str]:
    return {"statut": "ok"}
