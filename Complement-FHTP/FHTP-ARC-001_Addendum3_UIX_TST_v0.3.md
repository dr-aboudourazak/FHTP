# FHTP-ARC-001 — Addendum 3, v0.3
## UX/UI (UIX) et stratégie de test (TST)

**Date :** 9 juillet 2026
**Statut :** brouillon pour validation par Dr Amadou
**À intégrer dans :** FHTP-ARC-001 v0.5, comme nouvelles sections 20 (UX/UI) et 21 (Stratégie de test).
**Documents de référence :** FHTP-ARC-001 v0.5, Addendum 1 (v0.12), Addendum 2 (v0.2)

---

## Note de méthode

Suite à l'état des lieux du 9 juillet 2026 sur les onze aspects du dossier ARC (DAT, RUL, TRUST, API, SEC, UIX, TST, ADR, TRC, RFC, RSK), Dr Amadou a validé la priorité : combler UIX et TST en premier, les deux aspects qui n'avaient encore rien de concret. Ce document ne reprend aucune décision déjà actée ailleurs — il s'appuie sur les rôles RBAC déjà définis (section 8.2, F4), les profils de déploiement (Addendum 2, section 17), et le modèle de confiance à six piliers (section 2.1), sans les redéfinir.

---

## 20. UX/UI (UIX)

### 20.1 Principe directeur

L'interface se conçoit d'abord pour un opérateur en connexion bas débit sur un téléphone, pas pour un poste de bureau confortable — c'est la réalité déjà établie (Addendum 2, section 17.2, 17.6). Chaque écran doit rester utilisable en 2G/3G dégradée, sans image lourde ni dépendance à un rendu complexe.

### 20.2 Écrans principaux par rôle

Les rôles RBAC déjà définis (section 8.2, F4) déterminent ce que chaque écran expose, pas seulement l'apparence :

| Rôle | Écrans principaux |
|---|---|
| **Opérateur_Saisie** | Connexion → Saisie d'un dossier unitaire → Écran de décision (six piliers + décision finale) → Soumission de lot (dépôt de fichier, suivi de progression) → Rapport de lot |
| **Prescripteur** | Mêmes écrans, avec saisie du diagnostic CIM-10, des actes et prescriptions |
| **Médecin_Conseil** | File des dossiers signalés A_VERIFIER/ANOMALIE → Détail d'un dossier avec motifs → Déclenchement de contrôle → Consultation des PEC en attente |
| **Administrateur_Centre** | Gestion des comptes RBAC du centre → Statut de licence (Addendum 1, section 12.6) → Configuration du Profil_Import_Centre (Addendum 1, section 14.7) |

### 20.3 Un concept transversal : la file d'actions en attente

Plusieurs statuts déjà définis dans les addendums bloquent un dossier en attendant une action humaine : `EN_ATTENTE_CONFIRMATION_OCR` (Addendum 1, 14.8), `EN_ATTENTE_VERIFICATION_SCAN` (Addendum 1, 15.4), `CONTROLE_RAPIDE` à régulariser, licence en phase Grâce ou Dégradée (Addendum 1, 12.6). Plutôt que de multiplier les écrans dédiés à chacun, un seul écran transversal — la **file d'actions en attente** — regroupe tout ce qui demande une intervention humaine, trié par urgence. C'est l'écran d'accueil naturel de l'Opérateur_Saisie et de l'Administrateur_Centre.

### 20.4 Lisibilité du statut des six piliers

Les statuts CONFORME / A_VERIFIER / ANOMALIE ne doivent jamais reposer sur la seule couleur (rouge/orange/vert) pour rester lisibles en cas de daltonisme, fréquent, et sur un écran de qualité inégale en usage terrain. Chaque statut porte systématiquement une icône distincte et son intitulé textuel en toutes lettres, résolu selon la langue de l'utilisateur (Addendum 1, section 13).

### 20.5 Multilinguisme et RTL en pratique

Le choix de langue (français, anglais, arabe, portugais, espagnol — Addendum 1, section 13.4) ne se limite pas à traduire le texte : pour l'arabe, la mise en page doit s'inverser correctement (droite à gauche), pas seulement le sens de lecture du texte. Ce point, déjà signalé comme limite technique en 13.4, doit être vérifié concrètement dès les premières maquettes, pas laissé pour la fin du développement.

### 20.6 Version mobile (PWA)

Reprend les mêmes écrans que 20.2, dans une version allégée cohérente avec le mode client fin déjà retenu pour l'accès personnel (Addendum 2, section 17.6) : pas de tableau de bord complet à charger, un accès direct à la tâche du moment (saisir un dossier, vérifier un statut), et une déconnexion plus fréquente puisque l'appareil n'appartient pas au centre.

### 20.7 Première maquette produite

Un premier écran a été maquetté pour valider le concept avant d'aller plus loin : l'écran de décision d'un dossier, avec les six piliers affichés en grille, chaque statut porté par une icône et un intitulé (pas la seule couleur, cf. 20.4), et le motif de rejet ou de vérification affiché en clair sous la grille. Cette maquette illustre concrètement les principes 20.1 à 20.4 ; les écrans suivants (file d'actions en attente, saisie de dossier, version mobile) restent à produire dans le même esprit, de façon incrémentale plutôt que tous à la fois.

### 20.8 Ce qui reste à faire

Les wireframes des écrans restants, le système de composants graphiques complet, et les tests utilisateurs avec de vrais opérateurs de terrain restent à conduire — étape logique suivante une fois ces principes validés par Dr Amadou.

---

## 21. Stratégie de test (TST)

### 21.1 Principe directeur

Les flux de validation déjà décrits en détail (section 10, circuits 10.1 à 10.6) sont, de fait, presque des scripts de test : chaque étape, chaque branchement `<Decision>`, chaque issue attendue y est déjà écrite. La stratégie de test s'appuie sur cet acquis plutôt que d'en repartir de zéro.

### 21.2 Niveaux de test

| Niveau | Objet | Exemple |
|---|---|---|
| **Unitaire** | Une règle isolée du moteur de règles | R-TG-017 : un dossier avec diagnostic R68 doit produire ANOMALIE, quel que soit le reste du dossier |
| **Intégration connecteur** | Comportement face à un payeur simulé (mock), y compris latence et indisponibilité | Connecteur INAM indisponible → bascule en mode dégradé (section 7), jamais de FAST_TRACK direct |
| **Bout en bout par scénario** | Un circuit complet de la section 10, du dépôt du dossier à la décision finale | Rejouer le circuit 10.1 (consultation AMU) avec un dossier conforme, un dossier avec PEC manquante, un dossier R68 |
| **Non-régression** | Un jeu de dossiers de référence, rejoué à chaque nouvelle version du Référentiel de Règles | Vérifier qu'une mise à jour de règle ne change pas le comportement des règles qu'elle ne visait pas à modifier |
| **Charge** | Un lot de plusieurs centaines de dossiers (Addendum 1, section 14) | Vérifier que le traitement en file (14.4) ne bloque jamais l'ensemble du lot à cause d'un seul dossier malformé |
| **Sécurité** | RBAC, falsification, intégrité | Un opérateur d'un centre ne peut jamais lire les dossiers d'un autre centre ; un scan de PEC ne correspondant à aucun modèle connu (Addendum 1, 15.3) est détecté ; une horloge locale reculée est repérée par l'ancrage externe (Addendum 1, 12.5) |
| **OCR** | Reconnaissance de PDF scannés (Addendum 1, 14.8) | Mesurer le taux réel de reconnaissance sur un échantillon de vraies factures scannées, avant d'investir davantage dans ce sous-module — cf. recommandation déjà actée de calibrer avant de construire |
| **Acceptation (UAT)** | Un centre pilote, avant généralisation | Reprend le "test à blanc" déjà prévu à l'onboarding (Addendum 2, section 18.1), formalisé comme jalon de recette explicite |

### 21.3 Données de test

Toujours des données synthétiques ou anonymisées, jamais de vrais dossiers patients — cohérent avec le principe Privacy by Design déjà posé (section 8.1) : FHTP ne stocke jamais le contenu médical brut, un environnement de test n'a pas de raison d'y déroger.

### 21.4 Lien avec le cycle de vie des règles

Chaque nouvelle version d'une règle (section 2.1, versionnage déjà prévu) doit être accompagnée d'un jeu de cas de test associé avant publication — ce qui donne un mécanisme de retrait rapide (rollback) en cas de règle mal calibrée : rejouer le jeu de non-régression suffit à détecter l'écart avant qu'il n'atteigne la production. Ce point rejoint directement le besoin déjà identifié côté workflow opérationnel (Addendum 2, section 18.3, boucle terrain → évolution des règles).

### 21.5 Outillage retenu

**Confirmé par Dr Amadou, 9 juillet 2026 : FHTP Core sera écrit en Python.** L'outillage de test se précise en conséquence :

- **Tests de règles pilotés par les données.** Chaque règle du Référentiel de Règles (section 2.1) est déjà un objet JSON versionné. Les cas de test associés suivent le même principe — des fixtures JSON/YAML (dossier d'entrée + résultat attendu par pilier), rejouées avec `pytest` et son mécanisme de paramétrage (`pytest.mark.parametrize`), pour ajouter un nouveau cas de test sans toucher au code du moteur.
- **Connecteurs payeurs simulés.** Un petit serveur de simulation Python (par exemple via `FastAPI` ou `Flask` en mode test), exposant exactement les contrats déjà définis (`IConnecteurPayeur`, `IConnecteurTerrain`, section 3.1-3.2), avec des scénarios configurables : latence, indisponibilité, réponse ACCORDE/REFUSE sur une PEC.
- **Tests de charge sur la soumission groupée** (Addendum 1, section 14) : `Locust`, qui reste dans l'écosystème Python plutôt que d'introduire un outil dans un autre langage, pour simuler un lot de plusieurs centaines de dossiers.
- **Volume de départ du jeu de non-régression :** au minimum un cas positif et un cas négatif par règle actuellement recensée dans les trois PRD et les RP24 (de l'ordre de 100 à 150 règles) — soit un point de départ d'environ 200 à 300 cas, appelé à grandir au fil des cas remontés du terrain (boucle 21.4 / Addendum 2, section 18.3).
- **Calendrier de recette :** non-régression rejouée automatiquement à chaque nouvelle version de règle (continu) ; test à blanc à chaque onboarding de centre (Addendum 2, section 18.1) ; recette plus large avec le centre pilote à un rythme trimestriel, réaliste pour la taille actuelle de l'équipe.

### 21.6 Ce qui reste à faire

Le choix du framework web précis (FastAPI vs Flask, par exemple) et de l'ORM/base de données restent à trancher au moment du développement — cette section fixe le langage et la logique de test, pas encore chaque bibliothèque.

---

## 22. Journal des versions (entrée à ajouter à la section existante)

| Version | Date | Auteur | Changements |
|---|---|---|---|
| 0.1 | 9 juillet 2026 | Claude (sur demande de Dr Amadou) | Première rédaction des deux aspects identifiés comme non traités lors de l'état des lieux du 9 juillet 2026 : UX/UI (section 20 — écrans par rôle RBAC, concept transversal de file d'actions en attente, lisibilité des statuts sans dépendre de la couleur, RTL en pratique, version mobile allégée) et stratégie de test (section 21 — huit niveaux de test s'appuyant sur les circuits déjà décrits en section 10, données toujours synthétiques, lien direct avec le cycle de vie des règles pour permettre un rollback rapide). Les deux sections posent la structure et les principes ; maquettes et outillage restent à conduire dans une étape suivante. |
| 0.2 | 9 juillet 2026 | Claude (sur demande de Dr Amadou) | Passage aux maquettes et à l'outillage. Première maquette produite (écran de décision d'un dossier, six piliers en grille avec icône et intitulé par statut). Outillage de test précisé sans présumer du choix de langage de FHTP Core, pas encore arrêté : tests de règles pilotés par des fixtures de données plutôt que par du code, connecteurs payeurs simulés respectant les contrats déjà définis, volume de départ chiffré pour le jeu de non-régression (200 à 300 cas), calendrier de recette réaliste au regard de la taille actuelle de l'équipe. |
| 0.3 | 9 juillet 2026 | Claude (confirmation de Dr Amadou) | Python confirmé comme langage de FHTP Core. Outillage verrouillé en conséquence : pytest paramétré pour les fixtures de règles, simulateur de connecteurs en FastAPI/Flask, Locust pour les tests de charge. |
