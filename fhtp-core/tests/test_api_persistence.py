"""Tests de StoreDossiersSQLite -- la preuve concrete que la persistance
survit au-dela d'un seul processus, pas seulement une verification
d'interface.

Le test le plus important ici (test_persiste_au_dela_d_une_instance) cree
DEUX instances separees de StoreDossiersSQLite pointant vers le meme
fichier -- exactement ce qui se passe lors d'un vrai redemarrage du
processus API. Un simple test "get apres set sur la meme instance" ne
prouverait rien de plus qu'un dictionnaire en memoire.
"""

import tempfile
from pathlib import Path
from datetime import date, datetime

import pytest

from fhtp_core.api.persistence import StoreDossiersSQLite
from fhtp_core.models.dossier import Dossier
from fhtp_core.models.enums import CircuitRemboursement, TypeScenario


def _dossier_test(id_dossier: str = "DOS-PERSIST-001") -> Dossier:
    return Dossier(
        id_dossier=id_dossier,
        type_scenario=TypeScenario.CONSULTATION,
        id_beneficiaire="BEN-001",
        id_formation="FS-001",
        id_contrat_payeur="CTR-001",
        circuit_remboursement=CircuitRemboursement.AMU_SEUL,
        date_soins=date(2026, 8, 27),
        date_soumission=datetime(2026, 8, 27, 10, 0, 0),
    )


@pytest.fixture
def fichier_bdd_temporaire():
    with tempfile.TemporaryDirectory() as dossier_temp:
        yield Path(dossier_temp) / "test_fhtp.db"


class TestComportementDictLike:
    def test_absent_par_defaut(self, fichier_bdd_temporaire) -> None:
        store = StoreDossiersSQLite(fichier_bdd_temporaire)
        assert "DOS-INEXISTANT" not in store
        assert store.get("DOS-INEXISTANT") is None

    def test_set_puis_get_meme_instance(self, fichier_bdd_temporaire) -> None:
        store = StoreDossiersSQLite(fichier_bdd_temporaire)
        dossier = _dossier_test()
        store["DOS-PERSIST-001"] = dossier

        assert "DOS-PERSIST-001" in store
        recupere = store.get("DOS-PERSIST-001")
        assert recupere is not None
        assert recupere.id_dossier == dossier.id_dossier
        assert recupere.id_beneficiaire == dossier.id_beneficiaire

    def test_remplacement_ecrase_l_ancienne_valeur(self, fichier_bdd_temporaire) -> None:
        store = StoreDossiersSQLite(fichier_bdd_temporaire)
        store["DOS-001"] = _dossier_test("DOS-001")
        store["DOS-001"] = _dossier_test("DOS-001").model_copy(
            update={"id_beneficiaire": "BEN-REMPLACE"}
        )
        recupere = store.get("DOS-001")
        assert recupere.id_beneficiaire == "BEN-REMPLACE"

    def test_clear_vide_le_store(self, fichier_bdd_temporaire) -> None:
        store = StoreDossiersSQLite(fichier_bdd_temporaire)
        store["DOS-001"] = _dossier_test("DOS-001")
        store.clear()
        assert "DOS-001" not in store


class TestPersistanceReelleAuDelaDuProcessus:
    """Le coeur de cette suite : la preuve que les donnees survivent a la
    destruction de l'instance Python qui les a ecrites -- ce qu'un
    dictionnaire en memoire ne pourrait jamais faire."""

    def test_persiste_au_dela_d_une_instance(self, fichier_bdd_temporaire) -> None:
        # Premiere "vie du processus" : ecriture puis fermeture explicite
        # de la connexion, simulant l'arret du serveur.
        premiere_instance = StoreDossiersSQLite(fichier_bdd_temporaire)
        premiere_instance["DOS-REDEMARRAGE"] = _dossier_test("DOS-REDEMARRAGE")
        premiere_instance.fermer()

        # Deuxieme "vie du processus" : nouvelle instance, meme fichier --
        # exactement ce qui se passe au redemarrage d'uvicorn.
        deuxieme_instance = StoreDossiersSQLite(fichier_bdd_temporaire)
        recupere = deuxieme_instance.get("DOS-REDEMARRAGE")

        assert recupere is not None
        assert recupere.id_dossier == "DOS-REDEMARRAGE"

    def test_fichiers_differents_sont_bien_isoles(self, tmp_path) -> None:
        """Verification inverse : deux fichiers distincts ne doivent
        jamais partager de donnees -- confirme que l'isolation utilisee
        dans les tests API (base separee par test) est fiable."""
        store_a = StoreDossiersSQLite(tmp_path / "a.db")
        store_b = StoreDossiersSQLite(tmp_path / "b.db")

        store_a["DOS-A"] = _dossier_test("DOS-A")

        assert "DOS-A" in store_a
        assert "DOS-A" not in store_b

    def test_memoire_partagee_reste_isolee_entre_instances(self) -> None:
        """":memory:" cree une base ephemere propre a chaque connexion --
        deux instances ":memory:" distinctes ne doivent jamais se voir,
        contrairement a un fichier reel."""
        store_1 = StoreDossiersSQLite(":memory:")
        store_2 = StoreDossiersSQLite(":memory:")

        store_1["DOS-MEM"] = _dossier_test("DOS-MEM")

        assert "DOS-MEM" in store_1
        assert "DOS-MEM" not in store_2
