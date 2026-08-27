"""Tests des modeles de donnees -- FHTP-ARC-001, section 6.

Ces tests verifient la forme des donnees, pas encore la logique metier du
moteur de regles (a venir dans fhtp_core.engine).
"""

from datetime import date, datetime

import pytest
from pydantic import ValidationError

from fhtp_core.models import Beneficiaire, Dossier, ExclusionContrat
from fhtp_core.models.enums import (
    CategorieContrat,
    CircuitRemboursement,
    GuichetAMU,
    Pilier,
    StatutPilier,
    TypeExclusion,
    TypeRegime,
    TypeScenario,
)


def _dossier_minimal(**overrides) -> Dossier:
    base = dict(
        id_dossier="DOS-2026-000001",
        type_scenario=TypeScenario.CONSULTATION,
        id_beneficiaire="BEN-001",
        id_formation="FS-001",
        id_contrat_payeur="CTR-001",
        circuit_remboursement=CircuitRemboursement.AMU_SEUL,
        date_soins=date(2026, 8, 25),
        date_soumission=datetime(2026, 8, 25, 10, 0, 0),
    )
    base.update(overrides)
    return Dossier(**base)


class TestBeneficiaire:
    def test_categorie_contrat_optionnelle(self) -> None:
        """La categorie_contrat n'est pas obligatoire (ADR-012) -- ne
        s'applique que si le contrat distingue des niveaux de couverture."""
        b = Beneficiaire(
            id_beneficiaire="BEN-002",
            type_regime=TypeRegime.INAM_STANDARD,
            guichet_amu=GuichetAMU.INAM,
            date_affiliation=date(2024, 1, 1),
        )
        assert b.categorie_contrat is None

    def test_type_regime_invalide_rejete(self) -> None:
        with pytest.raises(ValidationError):
            Beneficiaire(
                id_beneficiaire="BEN-003",
                type_regime="REGIME_INEXISTANT",  # type: ignore[arg-type]
                guichet_amu=GuichetAMU.INAM,
                date_affiliation=date(2024, 1, 1),
            )


class TestDossierPiliers:
    """Section 2.1 -- logique de decision du moteur de regles, verifiee ici
    au niveau des methodes utilitaires du modele (pas encore le moteur lui-meme)."""

    def test_tous_conformes_quand_aucun_pilier_evalue(self) -> None:
        d = _dossier_minimal()
        assert d.tous_piliers_conformes() is True
        assert d.a_une_anomalie() is False
        assert d.a_verifier_seulement() is False

    def test_tous_conformes_si_conforme_ou_non_evalue(self) -> None:
        d = _dossier_minimal(
            evaluation_piliers={
                Pilier.COMPLETUDE_ADMINISTRATIVE: StatutPilier.CONFORME,
                Pilier.COHERENCE_GRAPHIQUE: StatutPilier.NON_EVALUE,
            }
        )
        assert d.tous_piliers_conformes() is True

    def test_anomalie_detectee(self) -> None:
        d = _dossier_minimal(
            evaluation_piliers={
                Pilier.COHERENCE_DOCUMENTAIRE: StatutPilier.ANOMALIE,
            }
        )
        assert d.a_une_anomalie() is True
        assert d.tous_piliers_conformes() is False

    def test_a_verifier_seul_sans_anomalie(self) -> None:
        d = _dossier_minimal(
            evaluation_piliers={
                Pilier.COHERENCE_TARIFAIRE: StatutPilier.A_VERIFIER,
            }
        )
        assert d.a_verifier_seulement() is True
        assert d.a_une_anomalie() is False

    def test_anomalie_prime_sur_a_verifier(self) -> None:
        """Un dossier avec A_VERIFIER et ANOMALIE combines n'est pas
        seulement 'a verifier' -- l'anomalie doit dominer (section 2.1,
        logique de decision : au moins un ANOMALIE -> AUDIT_APPROFONDI)."""
        d = _dossier_minimal(
            evaluation_piliers={
                Pilier.COHERENCE_TARIFAIRE: StatutPilier.A_VERIFIER,
                Pilier.COHERENCE_DOCUMENTAIRE: StatutPilier.ANOMALIE,
            }
        )
        assert d.a_verifier_seulement() is False
        assert d.a_une_anomalie() is True


class TestExclusionContrat:
    """ADR-012 / risque R8 -- granularite par categorie de beneficiaire."""

    def test_exclusion_globale_sans_categorie(self) -> None:
        ex = ExclusionContrat(
            id_exclusion="EXC-010",
            id_contrat_payeur="CTR-001",
            type_exclusion=TypeExclusion.MEDICAMENT,
            code_ou_categorie="VITAMINES",
            motif="exclu pour tous les beneficiaires de la police",
            date_version=date(2026, 1, 1),
        )
        assert ex.categorie_beneficiaire is None

    def test_exclusion_ciblee_categorie(self) -> None:
        ex = ExclusionContrat(
            id_exclusion="EXC-011",
            id_contrat_payeur="CTR-001",
            categorie_beneficiaire=CategorieContrat.EXECUTANT,
            type_exclusion=TypeExclusion.CATEGORIE_ACTE,
            code_ou_categorie="actes esthetiques",
            motif="exclu uniquement au niveau executant",
            date_version=date(2026, 1, 1),
        )
        assert ex.categorie_beneficiaire == CategorieContrat.EXECUTANT
