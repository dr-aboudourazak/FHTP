"""Journal de Conformite -- FHTP-ARC-001, section 2.4, et correction F2
(section 8.2, chainage cryptographique).

Append-only, immuable. Chaque entree porte le hash de la precedente :
c'est ce qui rend une modification retroactive detectable (F2). L'ancrage
externe periodique (type OpenTimestamps, section 8.5) qui rend cette chaine
opposable a un tiers exterieur au systeme n'est PAS implemente ici -- ce
module ne fait que la partie chainage interne, qui est gratuite et locale ;
l'ancrage externe est une integration a part (appel a un service externe),
a construire separement une fois un partenaire technique choisi.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from fhtp_core.models.enums import EventType
from fhtp_core.models.pec_et_audit import LogAudit


class ChaineCompromise(RuntimeError):
    """Levee par verifier_integrite() -- ne devrait jamais arriver en usage
    normal, seulement en cas de modification directe et non autorisee des
    entrees (cf. F2 : administrateur de base de donnees mal intentionne)."""


class JournalConformite:
    def __init__(self) -> None:
        self._entrees: list[LogAudit] = []

    @property
    def entrees(self) -> tuple[LogAudit, ...]:
        """Lecture seule -- jamais de mutation externe de l'historique."""
        return tuple(self._entrees)

    @staticmethod
    def _calculer_hash_chaine(entree: LogAudit) -> str:
        base = "|".join(
            [
                entree.hash_precedent or "",
                entree.payload_hash,
                entree.timestamp.isoformat(),
                entree.id_dossier,
                entree.event_type.value,
                entree.resultat,
            ]
        )
        return hashlib.sha256(base.encode("utf-8")).hexdigest()

    def _dernier_hash_chaine(self) -> Optional[str]:
        if not self._entrees:
            return None
        return self._calculer_hash_chaine(self._entrees[-1])

    def enregistrer(
        self,
        *,
        id_dossier: str,
        event_type: EventType,
        resultat: str,
        operateur_id: str,
        regle_id: Optional[str] = None,
    ) -> LogAudit:
        """Ajoute une entree au journal. Ne modifie jamais une entree
        existante -- append-only, conformement a la section 2.4."""
        timestamp = datetime.now(timezone.utc)
        payload = "|".join([id_dossier, event_type.value, resultat, regle_id or ""])
        payload_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        entree = LogAudit(
            id_log=f"LOG-{uuid4().hex[:16]}",
            timestamp=timestamp,
            id_dossier=id_dossier,
            event_type=event_type,
            regle_id=regle_id,
            resultat=resultat,
            payload_hash=payload_hash,
            operateur_id=operateur_id,
            hash_precedent=self._dernier_hash_chaine(),
        )
        self._entrees.append(entree)
        return entree

    def historique_dossier(self, id_dossier: str) -> list[LogAudit]:
        return [e for e in self._entrees if e.id_dossier == id_dossier]

    def verifier_integrite(self) -> bool:
        """Recalcule la chaine depuis le debut et confirme qu'aucune entree
        n'a ete modifiee apres sa creation (F2, section 8.2).

        Deux verifications independantes, pas une seule :
        1. Le chainage entre entrees (hash_precedent) -- detecte une
           insertion, suppression ou permutation d'entrees.
        2. Le contenu propre de chaque entree, en recalculant son
           payload_hash a partir de ses champs actuels -- detecte la
           modification du contenu d'une entree existante, y compris la
           **derniere** entree du journal, que le seul chainage ne peut pas
           couvrir puisqu'aucune entree suivante ne depend de son hash.

        Retourne False plutot que de lever une exception -- a l'appelant de
        decider de la reaction (alerte, section 8.8 plan de reponse a
        incident), pas a ce module de la lui imposer.
        """
        hash_attendu: Optional[str] = None
        for entree in self._entrees:
            if entree.hash_precedent != hash_attendu:
                return False

            payload = "|".join(
                [entree.id_dossier, entree.event_type.value, entree.resultat, entree.regle_id or ""]
            )
            if hashlib.sha256(payload.encode("utf-8")).hexdigest() != entree.payload_hash:
                return False

            hash_attendu = self._calculer_hash_chaine(entree)
        return True
