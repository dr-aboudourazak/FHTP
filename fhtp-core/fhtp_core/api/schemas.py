"""Schemas d'entree/sortie de l'API -- FHTP-ARC-001, section 12.3.

Le schema de sortie reprend le format illustratif du document maitre
(dossier_id, decision_finale, piliers, motifs, alerte_recours, locale), en
l'etendant d'un champ `statut` explicite : l'exemple du document ne couvre
pas le cas ou un dossier reste plafonne en EN_VALIDATION_LOCALE (mode
degrade, ADR-003) sans `decision_finale` -- ce champ le rend visible plutot
que de le laisser ambigu cote client.

Le schema d'entree (DossierSoumission) n'expose que les champs qu'un client
fournit reellement a la soumission -- jamais statut, evaluation_piliers,
decision_finale ou motifs_rejet, qui sont geres par le serveur et ne
doivent jamais pouvoir etre imposes par l'appelant.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from fhtp_core.models.dossier import ActeRealise, Dossier, MedicamentPrescrit
from fhtp_core.models.enums import (
    CircuitRemboursement,
    DecisionFinale,
    OrigineCreation,
    StatutDossier,
    TypeScenario,
)


class DossierSoumission(BaseModel):
    id_dossier: str
    type_scenario: TypeScenario
    id_beneficiaire: str
    id_formation: str
    id_contrat_payeur: str
    circuit_remboursement: CircuitRemboursement
    date_soins: date
    cloture_triple_trait: Optional[bool] = None
    actes: list[ActeRealise] = Field(default_factory=list)
    medicaments: list[MedicamentPrescrit] = Field(default_factory=list)

    # Le client ne devrait normalement jamais fixer ce champ lui-meme (c'est
    # une panne reseau *cote FHTP* qui le determine, section 7) -- expose
    # ici uniquement pour permettre des tests d'integration realistes sans
    # devoir simuler une vraie coupure. Defaut EN_LIGNE dans tous les cas
    # normaux.
    origine_creation: OrigineCreation = OrigineCreation.EN_LIGNE

    def vers_dossier(self) -> Dossier:
        """Convertit la requete en Dossier interne, en forcant la coherence
        des cles etrangeres id_dossier sur chaque ligne -- plutot que de
        faire confiance a ce que le client a rempli sur ses lignes."""
        actes = [a.model_copy(update={"id_dossier": self.id_dossier}) for a in self.actes]
        medicaments = [
            m.model_copy(update={"id_dossier": self.id_dossier}) for m in self.medicaments
        ]
        return Dossier(
            id_dossier=self.id_dossier,
            type_scenario=self.type_scenario,
            id_beneficiaire=self.id_beneficiaire,
            id_formation=self.id_formation,
            id_contrat_payeur=self.id_contrat_payeur,
            circuit_remboursement=self.circuit_remboursement,
            date_soins=self.date_soins,
            date_soumission=datetime.now(timezone.utc),
            cloture_triple_trait=self.cloture_triple_trait,
            actes=actes,
            medicaments=medicaments,
            origine_creation=self.origine_creation,
        )


class ReponseDossier(BaseModel):
    dossier_id: str
    statut: StatutDossier
    decision_finale: Optional[DecisionFinale] = None
    piliers: dict[str, str]
    motifs: list[str]
    alerte_recours: Optional[dict] = None
    locale: str = "fr"

    @classmethod
    def depuis_dossier(cls, dossier: Dossier, locale: str = "fr") -> "ReponseDossier":
        return cls(
            dossier_id=dossier.id_dossier,
            statut=dossier.statut,
            decision_finale=dossier.decision_finale,
            piliers={
                pilier.value.lower(): statut.value
                for pilier, statut in dossier.evaluation_piliers.items()
            },
            motifs=dossier.motifs_rejet,
            alerte_recours=(
                dossier.alerte_recours.model_dump() if dossier.alerte_recours.active else None
            ),
            locale=locale,
        )
