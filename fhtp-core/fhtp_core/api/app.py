"""Application FastAPI -- FHTP-ARC-001, section 12.

Point d'entree unique de l'API Directe FHTP Core (section 12.2), distincte
des Connecteurs Terrain (section 3.2/5) : c'est la porte que tout le monde
utilise, y compris un centre qui n'a jamais entendu parler d'un SIH.
"""

from __future__ import annotations

from fastapi import FastAPI

from fhtp_core.api.routes import router

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
)

app.include_router(router)


@app.get("/health", tags=["infra"])
def sante() -> dict[str, str]:
    return {"statut": "ok"}
