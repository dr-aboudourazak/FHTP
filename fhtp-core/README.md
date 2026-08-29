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

## Lancer l'API en local

```bash
uvicorn fhtp_core.api.app:app --reload
```

Puis ouvrir `http://127.0.0.1:8000/docs` -- interface interactive generee
automatiquement par FastAPI.

**Mode demo (actif par defaut) :** au demarrage, un bandeau dans la console
affiche un ou deux jetons de test a coller dans le bouton **Authorize** de
`/docs` (cadenas en haut a droite), pour pouvoir essayer `POST
/api/v1/dossiers` sans ecrire de code. Ces jetons sont des donnees de
demonstration en memoire (`fhtp_core/api/demo.py`), **jamais a utiliser en
production** -- desactivables avec la variable d'environnement `FHTP_DEMO=0`
avant de lancer `uvicorn`, une fois qu'un vrai systeme d'emission de jetons
existera (cf. `docs/JOURNAL_DEV.md`).

**A savoir en testant manuellement :** le connecteur payeur simule par
defaut n'a aucun beneficiaire preconfigure. Un dossier soumis avec un
`id_beneficiaire` quelconque recevra donc `CONTROLE_RAPIDE` (eligibilite
`INCONNU`, motif explicite dans la reponse), jamais `FAST_TRACK` -- c'est le
principe **fail-closed** volontairement applique par defaut (jamais
presumer une eligibilite favorable sans confirmation), pas un
dysfonctionnement.

**Persistance :** les dossiers soumis sont stockes dans un fichier SQLite
(`fhtp_dossiers.db`, cree automatiquement au premier lancement dans le
dossier courant) -- ils survivent donc a un redemarrage de l'API.
Personnalisable via la variable d'environnement `FHTP_DB_PATH` (utiliser
`:memory:` pour une base ephemere, perdue a chaque arret).

## Etat d'avancement

Voir `docs/JOURNAL_DEV.md` pour le suivi, en miroir du journal des versions des documents
de reference.
