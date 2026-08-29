"""Referentiel des molecules proscrites en prescription paramedicale --
FHTP-REF-001, Partie 4.3.

**Couverture volontairement partielle.** Le document source liste des noms
commerciaux (ACTINAC, AIRTAL, TOBRADEX, CHIBROCADRON...) sans toujours
donner la Denomination Commune Internationale (DCI) correspondante -- or
c'est la DCI, pas le nom commercial, que ce systeme manipule
(`MedicamentPrescrit.dci`). Deviner une correspondance nom commercial -> DCI
serait une erreur medicale potentielle, pas seulement un bug logiciel : ce
module ne code que les correspondances explicitement nommees dans le
document source, jamais une supposition pharmacologique.

Seule la DCI "Levofloxacine" (classe des fluoroquinolones orales) est
couverte ici, parce qu'elle est explicitement nommee comme telle dans
FHTP-REF-001 Partie 4.3. Les AINS oraux et les collyres corticoides cites
dans ce meme document ne le sont que par noms commerciaux -- a faire
verifier et completer par un pharmacien ou par Dr Amadou avant toute
extension, pas a deviner ici.
"""

from __future__ import annotations

DCI_PROSCRITES_PARAMEDICAL: frozenset[str] = frozenset(
    {
        "LEVOFLOXACINE",
    }
)


def molecule_est_proscrite_paramedical(dci: str) -> bool:
    """Vrai si la DCI donnee figure dans la liste des molecules proscrites
    en prescription paramedicale (section 4.3). Comparaison insensible a la
    casse et aux espaces superflus, pour rester robuste a une saisie
    variable (ex: 'levofloxacine', ' LEVOFLOXACINE ')."""
    return dci.strip().upper() in DCI_PROSCRITES_PARAMEDICAL
