"""Tests du Journal de Conformite -- section 2.4 et correction F2 (section 8.2).

Le test le plus important : verifier_integrite() doit reellement detecter
une modification retroactive d'une entree, pas seulement passer par
construction sur un journal jamais altere.
"""

from fhtp_core.engine.journal import JournalConformite
from fhtp_core.models.enums import EventType


class TestJournalConformiteBase:
    def test_premiere_entree_sans_hash_precedent(self) -> None:
        journal = JournalConformite()
        entree = journal.enregistrer(
            id_dossier="DOS-001",
            event_type=EventType.SOUMISSION,
            resultat="Dossier soumis",
            operateur_id="OP-001",
        )
        assert entree.hash_precedent is None

    def test_deuxieme_entree_chaine_sur_la_premiere(self) -> None:
        journal = JournalConformite()
        premiere = journal.enregistrer(
            id_dossier="DOS-001",
            event_type=EventType.SOUMISSION,
            resultat="Dossier soumis",
            operateur_id="OP-001",
        )
        deuxieme = journal.enregistrer(
            id_dossier="DOS-001",
            event_type=EventType.DECISION,
            resultat="FAST_TRACK",
            operateur_id="OP-001",
        )
        hash_attendu = journal._calculer_hash_chaine(premiere)
        assert deuxieme.hash_precedent == hash_attendu

    def test_historique_dossier_filtre_correctement(self) -> None:
        journal = JournalConformite()
        journal.enregistrer(
            id_dossier="DOS-001", event_type=EventType.SOUMISSION,
            resultat="x", operateur_id="OP-001",
        )
        journal.enregistrer(
            id_dossier="DOS-002", event_type=EventType.SOUMISSION,
            resultat="y", operateur_id="OP-001",
        )
        journal.enregistrer(
            id_dossier="DOS-001", event_type=EventType.DECISION,
            resultat="FAST_TRACK", operateur_id="OP-001",
        )
        historique = journal.historique_dossier("DOS-001")
        assert len(historique) == 2
        assert all(e.id_dossier == "DOS-001" for e in historique)


class TestIntegriteChaine:
    """Cf. F2 (section 8.2) : le chainage doit rendre une modification
    retroactive detectable."""

    def test_journal_vide_est_integre(self) -> None:
        assert JournalConformite().verifier_integrite() is True

    def test_journal_non_altere_est_integre(self) -> None:
        journal = JournalConformite()
        for i in range(5):
            journal.enregistrer(
                id_dossier=f"DOS-{i}",
                event_type=EventType.SOUMISSION,
                resultat="ok",
                operateur_id="OP-001",
            )
        assert journal.verifier_integrite() is True

    def test_modification_du_resultat_casse_la_chaine(self) -> None:
        """Le scenario exact de la faille F2 : un administrateur avec acces
        privilegie modifie directement une entree deja enregistree."""
        journal = JournalConformite()
        journal.enregistrer(
            id_dossier="DOS-001", event_type=EventType.SOUMISSION,
            resultat="Dossier soumis", operateur_id="OP-001",
        )
        journal.enregistrer(
            id_dossier="DOS-001", event_type=EventType.DECISION,
            resultat="AUDIT_APPROFONDI", operateur_id="OP-001",
        )
        assert journal.verifier_integrite() is True

        # Falsification directe : on maquille un rejet en paiement accepte.
        journal._entrees[1] = journal._entrees[1].model_copy(
            update={"resultat": "FAST_TRACK"}
        )

        assert journal.verifier_integrite() is False

    def test_falsification_de_la_toute_derniere_entree_est_detectee(self) -> None:
        """Cas limite important : la derniere entree du journal n'a aucune
        entree suivante dont le hash_precedent pourrait reveler
        l'incoherence par simple chainage. Sans revalidation du
        payload_hash propre a chaque entree, ce cas passerait inapercu --
        c'est exactement le trou que la premiere version de ce module
        laissait ouvert."""
        journal = JournalConformite()
        journal.enregistrer(
            id_dossier="DOS-001", event_type=EventType.SOUMISSION,
            resultat="Dossier soumis", operateur_id="OP-001",
        )
        journal.enregistrer(
            id_dossier="DOS-001", event_type=EventType.DECISION,
            resultat="AUDIT_APPROFONDI", operateur_id="OP-001",
        )
        assert journal.verifier_integrite() is True

        # On falsifie la DERNIERE entree -- rien apres elle dans la chaine.
        journal._entrees[-1] = journal._entrees[-1].model_copy(
            update={"resultat": "FAST_TRACK"}
        )

        assert journal.verifier_integrite() is False

    def test_insertion_d_une_entree_au_milieu_casse_la_chaine(self) -> None:
        journal = JournalConformite()
        journal.enregistrer(
            id_dossier="DOS-001", event_type=EventType.SOUMISSION,
            resultat="a", operateur_id="OP-001",
        )
        journal.enregistrer(
            id_dossier="DOS-001", event_type=EventType.DECISION,
            resultat="b", operateur_id="OP-001",
        )
        fausse_entree = journal.enregistrer(
            id_dossier="DOS-999", event_type=EventType.SOUMISSION,
            resultat="entree fabriquee", operateur_id="OP-INCONNU",
        ).model_copy(update={"hash_precedent": None})
        journal._entrees.insert(1, fausse_entree)

        assert journal.verifier_integrite() is False
