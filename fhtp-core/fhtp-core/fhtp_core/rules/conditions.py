"""Evaluateur d'expressions restreint pour les conditions du referentiel de
regles (section 2.1).

Pourquoi ne pas utiliser eval() directement : les regles sont stockees dans
un referentiel externe (fixtures JSON aujourd'hui, potentiellement editable
par une personne non-developpeuse plus tard, cf. section 2.1 "parametrables
et versionnees"). Un eval() sur du texte venant d'un fichier de donnees est
une porte ouverte a l'execution de code arbitraire si ce fichier est un jour
compromis ou mal valide. Ce module n'autorise qu'un sous-ensemble syntaxique
tres restreint (comparaisons, booleens, acces attribut, litteraux) via
l'arbre syntaxique (`ast`), jamais l'execution de code Python general.

Exemples de conditions supportees :
    "dossier.diagnostic_cim10 == 'R68'"
    "acte.montant_facture > acte.base_remboursement"
    "medicament.duree_traitement_jours > 15 and medicament.pec_id is None"
    "medicament.voie_administration == 'ORALE'"
"""

from __future__ import annotations

import ast
from typing import Any


class ConditionInvalide(ValueError):
    """Levee si une condition utilise une construction non autorisee."""


# Noeuds AST explicitement autorises. Toute construction absente de cette
# liste (appel de fonction, comprehension, import, etc.) est refusee.
_NOEUDS_AUTORISES = (
    ast.Expression,
    ast.BoolOp,
    ast.And,
    ast.Or,
    ast.UnaryOp,
    ast.Not,
    ast.Compare,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.In,
    ast.NotIn,
    ast.Is,
    ast.IsNot,
    ast.Attribute,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.List,
    ast.Tuple,
)


def _valider_noeuds(node: ast.AST) -> None:
    for enfant in ast.walk(node):
        if not isinstance(enfant, _NOEUDS_AUTORISES):
            raise ConditionInvalide(
                f"Construction non autorisee dans une condition : {type(enfant).__name__}"
            )


def _resoudre(node: ast.AST, contexte: dict[str, Any]) -> Any:
    if isinstance(node, ast.Expression):
        return _resoudre(node.body, contexte)

    if isinstance(node, ast.Constant):
        return node.value

    if isinstance(node, ast.Name):
        if node.id not in contexte:
            raise ConditionInvalide(f"Variable inconnue dans le contexte : {node.id!r}")
        return contexte[node.id]

    if isinstance(node, ast.Attribute):
        base = _resoudre(node.value, contexte)
        if base is None:
            # Un attribut lu sur une valeur absente (ex: acte optionnel non
            # fourni) est traite comme None plutot que de lever une erreur --
            # une condition doit pouvoir tester une absence sans planter.
            return None
        return getattr(base, node.attr, None)

    if isinstance(node, ast.List):
        return [_resoudre(elt, contexte) for elt in node.elts]

    if isinstance(node, ast.Tuple):
        return tuple(_resoudre(elt, contexte) for elt in node.elts)

    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return not _resoudre(node.operand, contexte)

    if isinstance(node, ast.BoolOp):
        # Court-circuit explicite, comme le "and"/"or" natif de Python --
        # indispensable ici : une condition comme
        # "medicament.enrole_presta_plus == True and medicament.prix_reference_presta_plus is not None and medicament.prix_unitaire_facture > medicament.prix_reference_presta_plus"
        # doit pouvoir s'arreter avant la troisieme clause si la premiere
        # est deja fausse, sinon la comparaison finale plante sur un None.
        if isinstance(node.op, ast.And):
            for valeur in node.values:
                if not _resoudre(valeur, contexte):
                    return False
            return True
        else:  # ast.Or
            for valeur in node.values:
                if _resoudre(valeur, contexte):
                    return True
            return False

    if isinstance(node, ast.Compare):
        gauche = _resoudre(node.left, contexte)
        for op, comparateur in zip(node.ops, node.comparators):
            droite = _resoudre(comparateur, contexte)
            if not _appliquer_comparaison(op, gauche, droite):
                return False
            gauche = droite
        return True

    raise ConditionInvalide(f"Construction non geree : {type(node).__name__}")


def _appliquer_comparaison(op: ast.cmpop, gauche: Any, droite: Any) -> bool:
    if isinstance(op, ast.Eq):
        return gauche == droite
    if isinstance(op, ast.NotEq):
        return gauche != droite
    if isinstance(op, ast.Lt):
        return gauche < droite
    if isinstance(op, ast.LtE):
        return gauche <= droite
    if isinstance(op, ast.Gt):
        return gauche > droite
    if isinstance(op, ast.GtE):
        return gauche >= droite
    if isinstance(op, ast.In):
        return gauche in droite
    if isinstance(op, ast.NotIn):
        return gauche not in droite
    if isinstance(op, ast.Is):
        return gauche is droite
    if isinstance(op, ast.IsNot):
        return gauche is not droite
    raise ConditionInvalide(f"Operateur de comparaison non gere : {type(op).__name__}")


def evaluer(condition: str, contexte: dict[str, Any]) -> bool:
    """Evalue une condition de regle contre un contexte donne.

    `contexte` associe les noms utilisables dans la condition (typiquement
    "dossier", "acte", "medicament") aux objets Pydantic correspondants.

    Leve ConditionInvalide si la condition utilise une construction non
    autorisee ou une variable absente du contexte -- jamais d'execution
    silencieuse d'une condition mal formee.
    """
    try:
        arbre = ast.parse(condition, mode="eval")
    except SyntaxError as exc:
        raise ConditionInvalide(f"Condition syntaxiquement invalide : {condition!r}") from exc

    _valider_noeuds(arbre)
    resultat = _resoudre(arbre, contexte)
    return bool(resultat)
