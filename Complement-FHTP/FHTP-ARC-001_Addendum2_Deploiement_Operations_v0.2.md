# FHTP-ARC-001 — Addendum 2, v0.2
## Architecture de déploiement et workflows opérationnels côté équipe FHTP

**Date :** 9 juillet 2026
**Statut :** brouillon pour validation par Dr Amadou
**À intégrer dans :** FHTP-ARC-001 v0.5, comme nouvelles sections 17 (Architecture de déploiement) et 18 (Workflows opérationnels FHTP). Si l'Addendum 1 (v0.6 à v0.12, sections 12 à 15 + annexe) est fusionné en premier, le Journal des versions du document maître passe alors en section 19.
**Documents de référence :** FHTP-ARC-001 v0.5, Addendum 1 (v0.12), FHTP-KNO-001 v0.20

---

## Note de méthode

Dr Amadou a fixé le cadre de ce document, 9 juillet 2026 : se concentrer sur le déploiement concret chez un centre et sur les workflows internes de l'équipe FHTP, et ne **pas** chercher à spécifier de connecteur terrain particulier — le terrain togolais change trop vite et trop souvent (nouveaux logiciels, changement de format d'un éditeur, cabinet qui bascule d'Excel à un logiciel) pour que ce soit un bon investissement de conception à ce stade. L'essentiel demandé : rester adaptable à toute éventualité.

Ce principe traverse tout ce document. Plutôt que de décrire un déploiement pour chaque logiciel terrain rencontré, ce document décrit des **profils de déploiement génériques**, et des **workflows opérationnels génériques** pour absorber la variabilité — en s'appuyant sur ce qui existe déjà (Profil_Import_Centre de l'Addendum 1, modèle de données consolidé de la section 6) plutôt qu'en ajoutant une nouvelle couche de flexibilité.

---

## 17. Architecture de déploiement

### 17.1 Trois profils, pas un déploiement unique

Tous les centres n'ont ni la même infrastructure, ni la même connectivité, ni le même volume de dossiers. FHTP retient trois profils de déploiement plutôt qu'un modèle unique imposé partout.

| Profil | Pour qui | Ce qui est installé |
|---|---|---|
| **Portail** | Cabinet sans logiciel, sans personnel technique (module de saisie minimale déjà décrit en section 5.3) | Rien. Accès web pur, y compris en connexion bas débit sur mobile. |
| **Agent** | Centre avec un logiciel existant (SIH, logiciel d'officine, ou simplement un tableur de facturation habituel) | Un agent léger installé aux côtés du logiciel existant, pas à sa place. |
| **Instance Locale** | Grand centre à fort volume et connectivité peu fiable (ex. CHR de référence régionale) | FHTP Core complet, déployé sur site, avec synchronisation périodique plutôt que dépendance continue. |

Le choix du profil se fait à l'onboarding (section 18.1), pas une fois pour toutes : un centre peut évoluer d'un profil à l'autre si sa situation change (un cabinet qui grandit, un centre qui change de logiciel).

### 17.2 Profil Portail — y compris sur téléphone personnel

Aucune installation. Le centre se connecte au portail web de FHTP (le module de saisie minimale, déjà décrit section 5.3), saisit ses dossiers un par un ou dépose un fichier pour une soumission groupée (section 14). Toute la logique tourne côté FHTP Core distant. C'est le profil le plus simple à déployer, et celui qui demande le moins de maintenance côté centre — au prix d'une dépendance complète à la connectivité au moment de l'usage.

**Précision de Dr Amadou, 9 juillet 2026 : le centre peut être sans connexion propre, mais les personnes qui y travaillent ont presque toujours une connexion mobile sur leur téléphone personnel.** C'est une réalité de terrain distincte de la coupure réseau générale déjà couverte par le mode dégradé (section 7) : là, on parle d'un centre qui perd sa connexion et se resynchronise plus tard. Ici, il s'agit d'utiliser directement la connexion mobile d'un membre du personnel comme canal, au moment même où le centre n'a pas la sienne.

**Décision retenue : une application web progressive (PWA), pas trois applications natives séparées.** Le portail doit être utilisable depuis un navigateur mobile — Android, Apple (iOS/Safari), et Huawei — sans passer par un magasin d'applications. Trois raisons à ce choix plutôt qu'un développement natif par plateforme :

- **Contrainte Huawei, à ne pas sous-estimer :** depuis les sanctions américaines de 2019, les téléphones Huawei récents n'embarquent plus les Services Mobiles Google (GMS) — remplacés par les Services Mobiles Huawei (HMS), un écosystème différent. Une application Android classique qui dépend de GMS (notifications push via Firebase, par exemple) ne fonctionne pas forcément correctement sur ces appareils. Une PWA, purement web, contourne entièrement ce problème : elle ne dépend ni de GMS ni de HMS.
- **Un seul développement pour les trois écosystèmes**, plutôt que trois applications natives à maintenir en parallèle — réaliste pour une équipe FHTP de taille limitée à ce stade.
- **Cohérence avec l'existant** : le Profil Portail est déjà pensé "accessible depuis n'importe quel navigateur, y compris mobile en connexion bas débit" (section 5.3). Ce choix ne fait qu'assumer explicitement ce qui était déjà implicite.

**Limite honnête à ne pas cacher :** le support des PWA sur iOS/Safari reste historiquement plus limité que sur Android (synchronisation en arrière-plan, notifications). Une alerte critique (licence, rejet urgent) ne peut donc pas dépendre uniquement d'une notification PWA si une part significative des utilisateurs est sur iPhone. Solution retenue : un canal SMS en complément pour les alertes critiques uniquement (section 17.6), puisque le SMS fonctionne sur n'importe quel téléphone, sans application ni même connexion data.

### 17.3 Profil Agent

**Ce que l'agent fait, et ce qu'il ne fait pas.** L'agent est un petit composant installé sur le poste ou le serveur du centre, à côté du logiciel de facturation ou de vente déjà en place. Il ne remplace jamais ce logiciel (principe déjà posé en FHTP-KNO-001 section 3.5) : il se contente de faire le pont entre ce que le centre produit et FHTP Core.

**Trois canaux d'ingestion génériques, plutôt qu'une intégration par éditeur de logiciel.** C'est le point qui répond directement à la demande de rester adaptable : au lieu de développer une intégration spécifique pour chaque logiciel terrain rencontré — risque réel vu la variabilité déjà constatée sur le terrain (FHTP-KNO-001 section 6.1, CHR Dapaong) — l'agent n'expose que des canaux génériques, réutilisables quel que soit le logiciel en face :

1. **Dossier surveillé (file watch)** : le centre exporte régulièrement un fichier (Excel, CSV, PDF) dans un dossier local ; l'agent détecte le nouveau fichier et le transmet à FHTP Core via le Profil_Import_Centre déjà défini (Addendum 1, section 14.7), qui sait déjà mapper les colonnes propres à ce centre.
2. **Point d'appel local minimal** : pour les rares logiciels capables d'appeler une API locale, l'agent expose un point d'entrée HTTP restreint à `localhost`, qui relaie ensuite vers FHTP Core.
3. **Saisie de secours** : en cas de défaillance des deux canaux précédents, l'agent redirige simplement vers le Profil Portail (17.2), y compris sa variante mobile — jamais de blocage total faute d'intégration technique.

**Cache local et mode dégradé.** L'agent embarque une copie locale des référentiels nécessaires (tarifs, règles, libellés) selon les seuils de fraîcheur déjà retenus (section 8.5), et applique le mode dégradé déjà défini (section 7) en cas de coupure — aucune logique nouvelle, l'agent est un point d'accès au mécanisme déjà conçu, pas un système parallèle.

**Conséquence pour la conception à venir :** quand un nouveau logiciel terrain est rencontré, la première question n'est pas "faut-il développer un connecteur dédié ?" mais "l'un des trois canaux génériques suffit-il ?". Le développement d'un connecteur sur mesure (au sens de la section 3) reste possible, mais devient l'exception plutôt que la règle par défaut — cf. workflow 18.5.

### 17.6 Le téléphone personnel comme canal, pas comme extension du centre

Deux usages concrets du téléphone personnel, à distinguer :

1. **Relais de connectivité** : un membre du personnel active le partage de connexion (hotspot) de son téléphone pour donner un accès internet temporaire au poste du centre qui exécute l'Agent ou accède au Portail. FHTP ne pilote pas ce choix — c'est une pratique terrain, pas une fonctionnalité logicielle — mais l'architecture doit rester indifférente à l'origine de la connexion : une requête HTTPS via un hotspot personnel n'est pas différente d'une requête via la ligne fixe du centre. Aucune logique spécifique à ajouter, seulement ne jamais supposer une seule source de connectivité possible.
2. **Accès direct depuis le téléphone** : le membre du personnel consulte ou soumet un dossier directement depuis le navigateur de son propre téléphone, sans passer par le poste du centre.

**Le deuxième usage change la donne côté sécurité.** Un téléphone personnel n'est pas un appareil du centre : il peut être perdu, volé, revendu, prêté, avec un niveau de contrôle bien plus faible qu'un poste fixe. Le principe déjà posé pour le cache local (section 7.3 : *"un poste ou téléphone perdu ou volé ne doit pas exposer de données en clair"*) anticipait déjà ce cas — cette section l'active concrètement plutôt que de le laisser théorique.

**Conséquence de conception : sur téléphone personnel, FHTP se comporte en client fin, pas en cache lourd.** Contrairement à l'Agent (17.3), qui conserve une copie locale persistante des référentiels, l'accès via téléphone personnel reste transitoire par défaut : authentification à chaque session, aucune conservation prolongée de PEC ou de référentiels sensibles sur l'appareil au-delà de la session en cours. C'est le même arbitrage que celui déjà fait entre Agent et Instance Locale (17.1) : plus l'appareil est personnel et hors du contrôle du centre, plus FHTP y stocke peu, quitte à demander une nouvelle authentification plus souvent.

### 17.7 Alertes critiques par SMS, en complément du portail

Pour ne pas dépendre uniquement d'une notification applicative — limitation déjà notée pour iOS en 17.2 — les alertes réellement critiques (échéance de licence proche, rejet nécessitant une action urgente) sont doublées par SMS vers le numéro enregistré de l'opérateur responsable. Le SMS ne demande ni application installée, ni même connexion data active, seulement une couverture réseau mobile — cohérence directe avec le constat de départ de Dr Amadou : la connexion mobile est presque toujours là, même quand la connexion du centre ne l'est pas.

### 17.4 Profil Instance Locale

Réservé aux centres où le volume et la fragilité de la connectivité justifient de faire tourner FHTP Core lui-même sur place, pas seulement un agent. Le CHR Dapaong, déjà cité comme centre de référence régionale avec une connectivité limitée (FHTP-KNO-001 section 6.1), est le candidat naturel à ce profil.

**Fonctionnement :** moteur de règles, gestionnaire de dossiers et cache des référentiels tournent localement. La instance locale ne dépend du réseau que pour :
- la vérification en ligne des PEC auprès des connecteurs payeurs (jamais contournable, cf. F7, section 8.2) ;
- la synchronisation périodique des référentiels et des règles (mise à jour, pas dépendance continue) ;
- l'ancrage externe déjà retenu pour l'intégrité du Journal de Conformité et, désormais, pour la licence (Addendum 1, section 12.5).

**Sécurité :** mêmes exigences que le cache local déjà définies section 7.3 (chiffrement au repos, réauthentification locale), renforcées ici par le fait que l'instance héberge davantage de logique, pas seulement des données en attente de synchronisation.

### 17.5 Propagation des mises à jour, quel que soit le profil

Référentiels, règles versionnées, libellés (Addendum 1, section 13) se propagent selon le même mécanisme quel que soit le profil : une file de mise à jour, consommée à la reconnexion pour les profils Agent et Instance Locale, immédiate pour le profil Portail qui n'a pas de cache local. Une seule mécanique de diffusion, pas une par profil.

---

## 18. Workflows opérationnels côté équipe FHTP

### 18.1 Onboarding d'un centre

1. **Qualification du profil de déploiement** (17.1) : volumétrie attendue, connectivité réelle du site, présence ou non d'un logiciel existant. Décision documentée, pas supposée.
2. **Configuration** : émission de la Cle_Licence (Addendum 1, section 12.5) avec le palier tarifaire retenu ; si soumission groupée prévue, configuration du Profil_Import_Centre à partir d'un exemple réel du fichier du centre (Addendum 1, section 14.7).
3. **Attribution des rôles RBAC** (section 8.2, F4) au personnel du centre.
4. **Test à blanc** : quelques dossiers réels traités avant la bascule en production, pour vérifier le mapping et la compréhension des rapports par l'équipe du centre — pas de mise en production directe sans ce passage.

### 18.2 Support et remontée d'incident

Distinction à maintenir entre deux natures d'incident, orientées vers des traitements différents :
- **Incident technique** (connectivité, agent en panne, fichier mal formé) : traitement rapide, souvent résolu par la relecture du Profil_Import_Centre ou un redémarrage de l'agent.
- **Incident métier** (contestation d'un rejet, question sur l'application d'une règle) : orienté vers la même logique d'alerte recours déjà définie dans les PRD, jamais traité comme un simple bug.

Canal de remontée réaliste plutôt que théorique : téléphone ou message direct dans un premier temps (cohérent avec la réalité déjà documentée des échanges terrain), consolidé ensuite dans un suivi structuré pour ne pas perdre la trace d'un problème récurrent.

### 18.3 Boucle terrain → évolution des règles

Un problème remonté du terrain (une règle mal comprise, un cas non prévu) ne modifie jamais directement le Référentiel de Règles. Il suit le même principe de rigueur que le reste du projet : toute modification de règle doit être motivée et sourcée avant publication d'une nouvelle version (cohérent avec la discipline déjà appliquée dans le Knowledge Book, section 3.1 — aucune règle sans source vérifiable). L'équipe FHTP centralise ces remontées, les qualifie, et ne pousse une nouvelle version qu'après validation.

### 18.4 Suivi opérationnel de la licence

Le mécanisme technique (Addendum 1, section 12.6) gère la dégradation automatique. Côté équipe, un tableau de bord des échéances (J-30, J-15...) doit déclencher un contact humain — appel ou message — **avant** que la dégradation automatique ne s'enclenche. L'automatisation gère le filet de sécurité commercial ; l'équipe garde la main sur la relation, dans le même esprit d'aide maximale déjà validé pour le mécanisme lui-même.

### 18.5 Nouvelle intégration terrain rencontrée — workflow générique

C'est le workflow qui répond directement à la variabilité du terrain. Plutôt que de traiter chaque nouveau logiciel ou format rencontré comme un projet de développement, la démarche reste volontairement légère et se limite à trois étapes, dans l'ordre :

1. **Observer et documenter** l'existant, comme cela a déjà été fait pour le CHR Dapaong (FHTP-KNO-001 section 6.1) — jamais supposer un format avant de l'avoir constaté.
2. **Configurer avec les mécanismes génériques déjà en place** : un des trois canaux de l'agent (17.3), ou un nouveau Profil_Import_Centre. Dans l'immense majorité des cas, ça suffit.
3. **Escalader vers un connecteur sur mesure** (au sens de la section 3) seulement si les mécanismes génériques se révèlent réellement insuffisants — l'exception, pas le réflexe par défaut.

### 18.6 Supervision

Suivi des dossiers restés en attente d'action humaine — `EN_ATTENTE_CONFIRMATION_OCR` (Addendum 1, section 14.8), `EN_ATTENTE_VERIFICATION_SCAN` (Addendum 1, section 15.4) — avec un délai de traitement à définir, pour qu'un dossier ne reste jamais bloqué indéfiniment faute d'attention. Suivi également des instances locales (17.4) dont la dernière synchronisation dépasse le seuil de fraîcheur retenu : alerte vers l'équipe, pas seulement vers le centre, pour anticiper une intervention plutôt que la découvrir a posteriori.

---

## 19. Journal des versions (entrée à ajouter à la section existante)

| Version | Date | Auteur | Changements |
|---|---|---|---|
| 0.1 | 9 juillet 2026 | Claude (sur demande de Dr Amadou) | Première rédaction de l'architecture de déploiement (section 17 : trois profils — Portail, Agent, Instance Locale — avec canaux d'ingestion génériques plutôt qu'intégration par éditeur de logiciel) et des workflows opérationnels côté équipe FHTP (section 18 : onboarding, support, boucle terrain → règles, suivi de licence, workflow générique de nouvelle intégration terrain, supervision). Conçu volontairement sans spécifier de connecteur terrain particulier, sur demande explicite de Dr Amadou, pour rester adaptable à un terrain reconnu comme changeant. |
| 0.2 | 9 juillet 2026 | Claude (sur demande de Dr Amadou) | Consolidation de l'accès mobile (section 17.2 étendue, nouvelles sections 17.6 et 17.7) : décision d'une PWA plutôt que trois applications natives, pour contourner l'absence des Services Mobiles Google sur les téléphones Huawei récents et éviter de maintenir trois codebases ; distinction entre le téléphone comme simple relais de connectivité (hotspot) et comme accès direct, avec un traitement sécurité en client fin sur accès direct (pas de cache persistant sur un appareil personnel) ; ajout d'un canal SMS de secours pour les alertes critiques, en complément d'une notification applicative peu fiable sur iOS. |
