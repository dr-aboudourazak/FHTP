"""Tests de l'evaluateur de conditions -- fhtp_core.rules.conditions.

Deux familles de tests : le comportement fonctionnel normal, et la garantie
de securite (aucune construction dangereuse ne doit passer).
"""

import pytest

from fhtp_core.rules.conditions import ConditionInvalide, evaluer


class Faux:
    """Objet factice pour tester l'acces attribut sans dependre des modeles
    Pydantic reels."""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class TestEvaluationNormale:
    def test_egalite_simple(self) -> None:
        acte = Faux(diagnostic_cim10="R68")
        assert evaluer("acte.diagnostic_cim10 == 'R68'", {"acte": acte}) is True

    def test_egalite_fausse(self) -> None:
        acte = Faux(diagnostic_cim10="J06")
        assert evaluer("acte.diagnostic_cim10 == 'R68'", {"acte": acte}) is False

    def test_comparaison_numerique(self) -> None:
        med = Faux(duree_traitement_jours=20)
        assert evaluer("medicament.duree_traitement_jours > 15", {"medicament": med}) is True

    def test_and_logique(self) -> None:
        med = Faux(duree_traitement_jours=20, pec_id=None)
        assert (
            evaluer(
                "medicament.duree_traitement_jours > 15 and medicament.pec_id is None",
                {"medicament": med},
            )
            is True
        )

    def test_and_logique_faux_si_pec_presente(self) -> None:
        med = Faux(duree_traitement_jours=20, pec_id="PEC-001")
        assert (
            evaluer(
                "medicament.duree_traitement_jours > 15 and medicament.pec_id is None",
                {"medicament": med},
            )
            is False
        )

    def test_attribut_sur_objet_absent_retourne_none(self) -> None:
        """Un acte optionnel non fourni (None) ne doit pas faire planter une
        condition qui teste un de ses attributs -- elle doit simplement
        evaluer a False/None plutot que lever une exception."""
        assert evaluer("acte.diagnostic_cim10 == 'R68'", {"acte": None}) is False

    def test_is_false_explicite(self) -> None:
        dossier = Faux(cloture_triple_trait=False)
        assert evaluer("dossier.cloture_triple_trait == False", {"dossier": dossier}) is True

    def test_variable_inconnue_leve_erreur(self) -> None:
        with pytest.raises(ConditionInvalide):
            evaluer("variable_qui_n_existe_pas == 1", {})

    def test_court_circuit_and_evite_erreur_sur_none(self) -> None:
        """Regression : 'and' doit s'arreter des que la premiere clause est
        fausse, sans evaluer la suivante -- sinon une condition en trois
        clauses comme R-TG-005 plante des que le champ optionnel de la
        derniere clause est None."""
        med = Faux(enrole_presta_plus=False, prix_reference_presta_plus=None, prix_unitaire_facture=2000)
        resultat = evaluer(
            "medicament.enrole_presta_plus == True and medicament.prix_reference_presta_plus is not None and medicament.prix_unitaire_facture > medicament.prix_reference_presta_plus",
            {"medicament": med},
        )
        assert resultat is False

    def test_court_circuit_or_ne_sur_evalue_pas_la_suite(self) -> None:
        dossier = Faux(circuit_remboursement="AMU_SEUL")
        # Si le court-circuit ne fonctionnait pas, la deuxieme clause
        # leverait ConditionInvalide (variable inconnue) -- ici elle ne doit
        # jamais etre atteinte puisque la premiere clause est deja vraie.
        resultat = evaluer(
            "dossier.circuit_remboursement == 'AMU_SEUL' or variable_inconnue == 1",
            {"dossier": dossier},
        )
        assert resultat is True


class TestSecuriteEvaluateur:
    """Aucune construction dangereuse ne doit pouvoir s'executer -- ces
    conditions imitent des tentatives d'injection dans un referentiel de
    regles potentiellement editable hors du code (section 2.1)."""

    def test_appel_de_fonction_refuse(self) -> None:
        with pytest.raises(ConditionInvalide):
            evaluer("__import__('os').system('echo test')", {})

    def test_import_refuse(self) -> None:
        with pytest.raises(ConditionInvalide):
            evaluer("import os", {})

    def test_syntaxe_invalide_refusee(self) -> None:
        with pytest.raises(ConditionInvalide):
            evaluer("acte. == 'R68'", {"acte": Faux()})

    def test_comprehension_refusee(self) -> None:
        with pytest.raises(ConditionInvalide):
            evaluer("[x for x in range(10)]", {})

    def test_lambda_refuse(self) -> None:
        with pytest.raises(ConditionInvalide):
            evaluer("(lambda: 1)()", {})
