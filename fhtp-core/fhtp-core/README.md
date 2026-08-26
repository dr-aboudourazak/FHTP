# FHTP Core

Moteur de validation des dossiers de facturation de sante -- **FITTER Health Trust Platform**.

Ce depot implemente `FHTP Core` tel que decrit dans `FHTP-ARC-001_Architecture_Technique.md`
(document maitre, repo `dr-aboudourazak/FHTP`). Il ne redefinit aucune regle metier ni aucun
choix d'architecture deja documente : il les met en code.

## Principe de correspondance documentation <-> code

Chaque module de ce depot renvoie explicitement, en commentaire d'en-tete, a la section du
document maitre qui le specifie. En cas de divergence entre le code et la documentation,
**la documentation fait foi** -- le code doit etre corrige, pas l'inverse (coherent avec la
methode du projet : documenter d'abord, concevoir ensuite, coder en dernier).

## Structure

```
fhtp_core/
  models/       Modele de donnees consolide (section 6)
  rules/        Referentiel de regles versionne (section 2.1)
  engine/       Moteur de regles a six piliers + gestionnaire de dossiers (section 2.1-2.2)
  connectors/   Contrats de connecteurs payeur/terrain (section 3)
  api/          Exposition API directe (section 12)
tests/
  fixtures/     Cas de test au format donnees (section 19.5) -- pas de logique en dur
docs/           Notes techniques internes au code, distinctes des documents de reference
```

## Installation (developpement)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Etat d'avancement

Voir `docs/JOURNAL_DEV.md` pour le suivi, en miroir du journal des versions des documents
de reference.
