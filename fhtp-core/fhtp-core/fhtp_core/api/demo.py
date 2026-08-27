"""Donnees de demonstration pour tester l'API manuellement via /docs.

**JAMAIS a utiliser en production.** Ce module enregistre quelques jetons
factices dans l'annuaire (section 8.3) au demarrage, pour permettre de
jouer avec l'API sans devoir ecrire la moindre ligne de code.

Actif PAR DEFAUT tant qu'aucun vrai systeme d'emission de jetons n'existe
(cf. `docs/JOURNAL_DEV.md`, "Ce qui reste a faire" -- l'annuaire actuel est
deja documente comme un mecanisme simplifie, pas une infrastructure de
securite reelle). Desactivable en positionnant la variable d'environnement
`FHTP_DEMO=0` avant de lancer `uvicorn`.
"""

from __future__ import annotations

from fhtp_core.api.auth import AnnuaireJetons, ContexteOperateur, RoleRBAC

# Deux jetons couvrant les deux cas deja testes en section 8.2 (F4) :
# un operateur de cabinet, scope a sa seule formation, et un medecin-conseil
# avec acces en lecture large (mais jamais en soumission, cf. ADR/tests).
#
# CHR_Dapaong reprend le centre de reference cite tout du long dans
# FHTP-KNO-001 (section 6.1, observation de terrain de Dr Amadou) -- plus
# naturel a utiliser pour des tests manuels que "FS-001".
JETONS_DEMO: dict[str, ContexteOperateur] = {
    "demo-cabinet-fs001": ContexteOperateur(
        operateur_id="OP-DEMO-CABINET",
        id_formation="FS-001",
        role=RoleRBAC.OPERATEUR_SAISIE,
    ),
    "demo-chr-dapaong": ContexteOperateur(
        operateur_id="OP-DEMO-CHR-DAPAONG",
        id_formation="CHR_Dapaong",
        role=RoleRBAC.OPERATEUR_SAISIE,
    ),
    "demo-medecin-conseil": ContexteOperateur(
        operateur_id="MC-DEMO",
        id_formation="FS-PAYEUR-DEMO",
        role=RoleRBAC.MEDECIN_CONSEIL,
    ),
}


def activer_donnees_demo(annuaire: AnnuaireJetons) -> None:
    for jeton, contexte in JETONS_DEMO.items():
        annuaire.enregistrer(jeton, contexte)
