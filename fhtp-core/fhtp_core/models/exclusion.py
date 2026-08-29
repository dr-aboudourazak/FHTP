"""Exclusion de contrat -- ADR-012, risque R8 (FHTP-KNO-001, section 12).

Verifiee au pilier COHERENCE_REGIME (pilier 2), pas au pilier documentaire :
une exclusion de police est une question de couverture contractuelle, pas un
probleme de piece manquante -- les deux natures de rejet ouvrent des voies de
recours differentes (section 10, note sur le pilier 2).
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel

from fhtp_core.models.enums import CategorieContrat, TypeExclusion


class ExclusionContrat(BaseModel):
    id_exclusion: str
    id_contrat_payeur: str

    # Vide = s'applique a toute la police. Renseigne = ne s'applique qu'a
    # cette categorie (ex : exclusion valable seulement au niveau executant
    # d'un contrat d'entreprise donne).
    categorie_beneficiaire: Optional[CategorieContrat] = None

    type_exclusion: TypeExclusion
    code_ou_categorie: str  # code acte/DCI precis, ou categorie large
    motif: str
    date_version: date
