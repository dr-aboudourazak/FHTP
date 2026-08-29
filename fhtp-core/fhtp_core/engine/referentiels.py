"""Registres en memoire pour resoudre les cles etrangeres Prescripteur et
Formation_Sanitaire referencees par un Dossier (section 6).

Meme limite que le store de dossiers de l'API (docs/JOURNAL_DEV.md) : pas de
persistance reelle, un dictionnaire en memoire suffisant pour demontrer et
tester la resolution, a remplacer avant tout usage en production.

Utilises par le Gestionnaire de Dossiers pour resoudre reellement le type de
prescripteur et le type de formation sanitaire quand ils sont fournis --
remplace la dependance a des champs precalcules fournis sans garantie par
l'appelant (R-TG-021, RG-H11), sans pour autant la rendre obligatoire :
quand aucun registre n'est fourni au Gestionnaire de Dossiers, le
comportement precedent (champs precalcules fournis directement sur le
Dossier) continue de fonctionner a l'identique.
"""

from __future__ import annotations

from typing import Optional

from fhtp_core.models.identite import FormationSanitaire, Prescripteur


class RegistrePrescripteurs:
    def __init__(self) -> None:
        self._prescripteurs: dict[str, Prescripteur] = {}

    def enregistrer(self, prescripteur: Prescripteur) -> None:
        self._prescripteurs[prescripteur.id_prescripteur] = prescripteur

    def obtenir(self, id_prescripteur: str) -> Optional[Prescripteur]:
        return self._prescripteurs.get(id_prescripteur)


class RegistreFormationsSanitaires:
    def __init__(self) -> None:
        self._formations: dict[str, FormationSanitaire] = {}

    def enregistrer(self, formation: FormationSanitaire) -> None:
        self._formations[formation.id_formation] = formation

    def obtenir(self, id_formation: str) -> Optional[FormationSanitaire]:
        return self._formations.get(id_formation)
