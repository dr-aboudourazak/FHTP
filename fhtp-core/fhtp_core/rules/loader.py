"""Chargement du referentiel de regles -- FHTP-ARC-001, section 2.1.

Les regles vivent dans des fichiers JSON versionnes (un fichier par
regroupement thematique, section 22 matrice de tracabilite), jamais codees en
dur -- c'est ce qui permet de mettre a jour la reglementation sans toucher au
moteur (section 17.3, boucle terrain -> evolution des regles).
"""

from __future__ import annotations

import json
from pathlib import Path

from fhtp_core.rules.models import Regle

REPERTOIRE_FIXTURES_DEFAUT = Path(__file__).parent / "fixtures"


def charger_regles(repertoire: Path | None = None) -> list[Regle]:
    """Charge toutes les regles depuis les fichiers *.json d'un repertoire.

    Chaque fichier peut contenir soit une seule regle (objet JSON), soit une
    liste de regles -- pour permettre de regrouper les regles par source
    (ex: un fichier par PRD) sans imposer un fichier par regle.
    """
    repertoire = repertoire or REPERTOIRE_FIXTURES_DEFAUT
    regles: list[Regle] = []
    identifiants_vus: set[str] = set()

    for fichier in sorted(repertoire.glob("*.json")):
        contenu = json.loads(fichier.read_text(encoding="utf-8"))
        items = contenu if isinstance(contenu, list) else [contenu]
        for item in items:
            regle = Regle(**item)
            if regle.id in identifiants_vus:
                raise ValueError(
                    f"Regle en double : {regle.id} (trouvee dans {fichier.name})"
                )
            identifiants_vus.add(regle.id)
            regles.append(regle)

    return regles
