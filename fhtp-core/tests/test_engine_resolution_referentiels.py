"""Tests de la resolution reelle des jointures Prescripteur et
FormationSanitaire par le Gestionnaire de Dossiers (fhtp_core.engine.referentiels).

Ce que ces tests prouvent, que test_engine_regles_complementaires.py ne
prouve pas : la ou ces tests-la fournissaient directement
`prescripteur_paramedical=True` / `structure_est_clinique_privee=True` a la
main sur le Dossier (simulant un pre-calcul deja fait par un appelant
hypothetique), ceux-ci partent d'un Dossier qui ne connait que des
identifiants (`id_prescripteur`, `id_formation`) et laissent le
Gestionnaire de Dossiers resoudre lui-meme le reste via de vrais registres.
"""

from datetime import date, datetime

import pytest

from fhtp_core.engine.gestionnaire_dossiers import GestionnaireDossiers
from fhtp_core.engine.journal import JournalConformite
from fhtp_core.engine.referentiels import RegistreFormationsSanitaires, RegistrePrescripteurs
from fhtp_core.models.dossier import Dossier, MedicamentPrescrit
from fhtp_core.models.enums import (
    CircuitRemboursement,
    Pilier,
    Secteur,
    StatutDossier,
    StatutPrescripteur,
    TypeFormationSanitaire,
    TypePrescripteur,
    TypeScenario,
    VoieAdministration,
)
from fhtp_core.models.identite import FormationSanitaire, Prescripteur
from fhtp_core.rules.loader import charger_regles


@pytest.fixture
def gestionnaire_sans_registres():
    """Pour confirmer la retro-compatibilite : sans registre, rien ne
    change par rapport a l'ancien comportement."""
    return GestionnaireDossiers(regles=charger_regles(), journal=JournalConformite())


@pytest.fixture
def registres_peuples():
    registre_prescripteurs = RegistrePrescripteurs()
    registre_prescripteurs.enregistrer(
        Prescripteur(
            id_prescripteur="PRE-PARAMEDICAL-01",
            numero_ordre="ORD-001",
            code_prescripteur_amu="02-001",
            type_prescripteur=TypePrescripteur.PARAMEDICAL,
            statut=StatutPrescripteur.ACTIF,
        )
    )
    registre_prescripteurs.enregistrer(
        Prescripteur(
            id_prescripteur="PRE-MEDECIN-01",
            numero_ordre="ORD-002",
            code_prescripteur_amu="01-001",
            type_prescripteur=TypePrescripteur.MEDECIN,
            statut=StatutPrescripteur.ACTIF,
        )
    )

    registre_formations = RegistreFormationsSanitaires()
    registre_formations.enregistrer(
        FormationSanitaire(
            id_formation="FS-CLINIQUE-001",
            code_formation_sanitaire_amu="CODE-001",
            numero_autorisation_ministere_sante="AUT-001",
            type=TypeFormationSanitaire.CLINIQUE_PRIVEE,
            secteur=Secteur.PRIVE,
            date_conventionnement=date(2020, 1, 1),
        )
    )
    registre_formations.enregistrer(
        FormationSanitaire(
            id_formation="FS-CHR-001",
            code_formation_sanitaire_amu="CODE-002",
            numero_autorisation_ministere_sante="AUT-002",
            type=TypeFormationSanitaire.CHR,
            secteur=Secteur.PUBLIC,
            date_conventionnement=date(2015, 1, 1),
        )
    )

    return registre_prescripteurs, registre_formations


@pytest.fixture
def gestionnaire_avec_registres(registres_peuples):
    registre_prescripteurs, registre_formations = registres_peuples
    return GestionnaireDossiers(
        regles=charger_regles(),
        journal=JournalConformite(),
        registre_prescripteurs=registre_prescripteurs,
        registre_formations=registre_formations,
    )


def _dossier_avec_medicament(
    *, id_formation: str, id_prescripteur: str | None, dci: str, voie: VoieAdministration
) -> Dossier:
    id_dossier = "DOS-2026-000700"
    return Dossier(
        id_dossier=id_dossier,
        type_scenario=TypeScenario.CONSULTATION,
        id_beneficiaire="BEN-001",
        id_formation=id_formation,
        id_contrat_payeur="CTR-001",
        circuit_remboursement=CircuitRemboursement.AMU_SEUL,
        date_soins=date(2026, 8, 27),
        date_soumission=datetime(2026, 8, 27, 10, 0, 0),
        cloture_triple_trait=True,
        medicaments=[
            MedicamentPrescrit(
                id_prescription="MED-700",
                id_dossier=id_dossier,
                id_prescripteur=id_prescripteur,
                dci=dci,
                voie_administration=voie,
                duree_traitement_jours=5,
                quantite=1,
                prix_unitaire_facture=5000,
                pec_id=None,
            )
        ],
    )


class TestResolutionReelleParamedicale:
    """R-TG-021, mais resolu via un vrai registre plutot que fourni a la main."""

    def test_prescripteur_paramedical_resolu_declenche_anomalie(
        self, gestionnaire_avec_registres
    ) -> None:
        d = _dossier_avec_medicament(
            id_formation="FS-CHR-001",
            id_prescripteur="PRE-PARAMEDICAL-01",
            dci="LEVOFLOXACINE",
            voie=VoieAdministration.ORALE,
        )
        resultat = gestionnaire_avec_registres.soumettre(d, operateur_id="OP-001")
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == "ANOMALIE"

    def test_prescripteur_medecin_resolu_ne_declenche_rien(
        self, gestionnaire_avec_registres
    ) -> None:
        """Meme molecule, mais prescrite par un medecin (resolu via le
        registre) -- la restriction ne s'applique qu'aux paramedicaux."""
        d = _dossier_avec_medicament(
            id_formation="FS-CHR-001",
            id_prescripteur="PRE-MEDECIN-01",
            dci="LEVOFLOXACINE",
            voie=VoieAdministration.ORALE,
        )
        resultat = gestionnaire_avec_registres.soumettre(d, operateur_id="OP-001")
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == "CONFORME"

    def test_molecule_non_proscrite_ne_declenche_rien_meme_paramedical(
        self, gestionnaire_avec_registres
    ) -> None:
        """La resolution du prescripteur ne suffit pas seule -- il faut
        aussi que la molecule soit reellement dans la liste proscrite
        (referentiel_molecules_proscrites), jamais une supposition."""
        d = _dossier_avec_medicament(
            id_formation="FS-CHR-001",
            id_prescripteur="PRE-PARAMEDICAL-01",
            dci="AMOXICILLINE",
            voie=VoieAdministration.ORALE,
        )
        resultat = gestionnaire_avec_registres.soumettre(d, operateur_id="OP-001")
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == "CONFORME"

    def test_prescripteur_inconnu_du_registre_ne_plante_pas(
        self, gestionnaire_avec_registres
    ) -> None:
        """Un id_prescripteur qui ne correspond a rien dans le registre ne
        doit jamais faire planter le pipeline -- juste ne rien resoudre,
        laissant le champ precalcule (ici absent) tel quel."""
        d = _dossier_avec_medicament(
            id_formation="FS-CHR-001",
            id_prescripteur="PRE-INCONNU-999",
            dci="LEVOFLOXACINE",
            voie=VoieAdministration.ORALE,
        )
        resultat = gestionnaire_avec_registres.soumettre(d, operateur_id="OP-001")
        # Prescripteur non resolu -> prescripteur_paramedical reste None ->
        # la regle ne se declenche pas (None != True).
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == "CONFORME"


class TestResolutionReelleCliniquePrivee:
    """RG-H11, resolu via un vrai registre de formations sanitaires."""

    def test_clinique_privee_resolue_bloque_le_medicament_oral(
        self, gestionnaire_avec_registres
    ) -> None:
        d = _dossier_avec_medicament(
            id_formation="FS-CLINIQUE-001",
            id_prescripteur=None,
            dci="AMOXICILLINE",
            voie=VoieAdministration.ORALE,
        )
        resultat = gestionnaire_avec_registres.soumettre(d, operateur_id="OP-001")
        assert resultat.evaluation_piliers[Pilier.COHERENCE_REGIME] == "ANOMALIE"

    def test_chr_public_resolu_ne_bloque_pas_le_medicament_oral(
        self, gestionnaire_avec_registres
    ) -> None:
        """Meme medicament oral, mais formation resolue comme CHR (secteur
        public) -- RG-H11 ne s'applique qu'aux cliniques privees."""
        d = _dossier_avec_medicament(
            id_formation="FS-CHR-001",
            id_prescripteur=None,
            dci="AMOXICILLINE",
            voie=VoieAdministration.ORALE,
        )
        resultat = gestionnaire_avec_registres.soumettre(d, operateur_id="OP-001")
        assert resultat.evaluation_piliers[Pilier.COHERENCE_REGIME] == "CONFORME"


class TestRetrocompatibiliteSansRegistre:
    """Sans registre fourni au Gestionnaire de Dossiers, le comportement
    precedent (champs precalcules fournis directement) doit continuer de
    fonctionner exactement comme avant cet ajout."""

    def test_sans_registre_id_prescripteur_seul_ne_declenche_rien(
        self, gestionnaire_sans_registres
    ) -> None:
        """Sans registre, un id_prescripteur pointant vers un paramedical
        ne suffit plus a lui seul -- il faut alors fournir explicitement le
        champ precalcule, comme avant cet ajout."""
        d = _dossier_avec_medicament(
            id_formation="FS-CLINIQUE-001",
            id_prescripteur="PRE-PARAMEDICAL-01",  # ignore, faute de registre
            dci="LEVOFLOXACINE",
            voie=VoieAdministration.ORALE,
        )
        resultat = gestionnaire_sans_registres.soumettre(d, operateur_id="OP-001")
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == "CONFORME"

    def test_sans_registre_champ_precalcule_direct_fonctionne_toujours(
        self, gestionnaire_sans_registres
    ) -> None:
        d = Dossier(
            id_dossier="DOS-2026-000701",
            type_scenario=TypeScenario.CONSULTATION,
            id_beneficiaire="BEN-001",
            id_formation="FS-CLINIQUE-001",
            id_contrat_payeur="CTR-001",
            circuit_remboursement=CircuitRemboursement.AMU_SEUL,
            date_soins=date(2026, 8, 27),
            date_soumission=datetime(2026, 8, 27, 10, 0, 0),
            cloture_triple_trait=True,
            medicaments=[
                MedicamentPrescrit(
                    id_prescription="MED-701",
                    id_dossier="DOS-2026-000701",
                    dci="LEVOFLOXACINE",
                    voie_administration=VoieAdministration.ORALE,
                    duree_traitement_jours=5,
                    quantite=1,
                    prix_unitaire_facture=5000,
                    prescripteur_paramedical=True,  # fourni directement, ancien mode
                    pec_id=None,
                )
            ],
        )
        resultat = gestionnaire_sans_registres.soumettre(d, operateur_id="OP-001")
        assert resultat.evaluation_piliers[Pilier.COHERENCE_PRESCRIPTEUR] == "ANOMALIE"
