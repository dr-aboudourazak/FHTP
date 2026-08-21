# FHTP-ARC-001 — Addendum 6, v0.1
## Architecture Decision Records (ADR)

**Date :** 9 juillet 2026
**Statut :** brouillon pour validation par Dr Amadou
**À intégrer dans :** FHTP-ARC-001 v0.5, nouvelle section 25.

---

## Note de méthode

Aucune décision nouvelle ici. Ce document reprend des choix déjà pris et déjà tracés dans les journaux des versions de FHTP-KNO-001 et FHTP-ARC-001, et les met en forme de fiche structurée (contexte / décision / alternatives écartées / conséquences) — le format qui manquait, pas la substance.

**Gabarit retenu :** Contexte — Décision — Alternatives écartées — Conséquences.

---

### ADR-001 — FHTP Core indépendant du payeur

**Contexte :** l'INAM, la CNSS et les assureurs CAT ont des logiques tarifaires structurellement différentes (R/E/TPC contre lettre-clé/coefficient).
**Décision :** FHTP Core ne raisonne qu'en interfaces génériques (`IConnecteurPayeur`) ; chaque payeur est un connecteur interchangeable.
**Alternatives écartées :** coder la logique de chaque payeur directement dans le moteur de règles — rejeté, rendrait toute extension à un nouveau payeur ou pays coûteuse.
**Conséquences :** un futur connecteur Ghana ou régional s'ajoute sans toucher au Core. *Source : FHTP-KNO-001 section 3.4.*

### ADR-002 — FHTP s'intègre au terrain, il ne le remplace pas

**Contexte :** les centres utilisent déjà des logiciels de vente/SIH, ou parfois seulement Excel.
**Décision :** FHTP se construit comme couche de validation, jamais comme remplacement d'un logiciel de gestion existant.
**Alternatives écartées :** un logiciel de caisse/gestion intégré — rejeté, mettrait FHTP en concurrence inutile avec des éditeurs déjà en place et alourdirait sa responsabilité opérationnelle.
**Conséquences :** connecteurs terrain génériques (Addendum 2, section 17.3) plutôt qu'un produit de gestion. *Source : FHTP-KNO-001 section 3.5.*

### ADR-003 — Aucun FAST_TRACK avant réévaluation en ligne (mode dégradé)

**Contexte :** un dossier créé hors ligne pourrait atteindre le paiement automatique avant toute vérification réelle — faille identifiée à la relecture.
**Décision :** un dossier `MODE_DEGRADE` plafonne à `EN_VALIDATION_LOCALE`, jamais `FAST_TRACK`, avant synchronisation et réévaluation en ligne.
**Alternatives écartées :** faire confiance au cache local pour les cas jugés simples — rejeté, ouvrait une fenêtre d'exploitation en cas de coupure provoquée.
**Conséquences :** un opérateur malveillant ne peut pas exploiter une coupure réseau pour faire valider un dossier fabriqué. *Source : FHTP-ARC-001 section 7.2.*

### ADR-004 — Une PEC est toujours vérifiée par requête au payeur, jamais par le seul format

**Contexte :** incident réel au CHR Dapaong — une PEC réellement accordée mais absente physiquement a été traitée comme un rejet, révélant l'inverse aussi vrai : un numéro plausible mais jamais accordé pourrait passer.
**Décision :** la validité d'une PEC est vérifiée par requête au connecteur payeur, jamais par la seule conformité de format du numéro.
**Alternatives écartées :** valider un numéro de PEC sur sa seule forme (regex, longueur) — rejeté, insuffisant contre la fabrication.
**Conséquences :** même en l'absence de connexion, un scan et un référentiel de modèles de documents (Addendum 1, section 15) restent un filet provisoire, jamais un substitut définitif. *Source : FHTP-ARC-001 section 8.2 (F7).*

### ADR-005 — Ancrage externe (type OpenTimestamps) pour l'intégrité de l'audit et de la licence

**Contexte :** un chaînage interne du Journal de Conformité reste modifiable par un administrateur privilégié ; une horloge locale peut être reculée pour prolonger une licence expirée.
**Décision :** un ancrage périodique externe, public et gratuit, complète le chaînage interne — réutilisé ensuite pour détecter la triche sur l'horloge de licence.
**Alternatives écartées :** infrastructure d'ancrage dédiée (coût récurrent) — rejetée à ce stade de financement du projet.
**Conséquences :** une seule mécanique sert deux besoins (intégrité de l'audit, anti-triche de licence). *Sources : FHTP-ARC-001 section 8.5 ; Addendum 1, section 12.5.*

### ADR-006 — Jeton de licence signé, vérifiable localement

**Contexte :** FHTP doit générer un revenu ; l'accès doit expirer même si FHTP Core est installé localement chez un centre.
**Décision :** un jeton signé embarquant sa propre date d'expiration, vérifié localement sans appel réseau systématique.
**Alternatives écartées :** vérification en ligne à chaque requête — rejetée, incompatible avec la réalité de connectivité déjà documentée et créerait une dépendance réseau sur une fonction commerciale.
**Conséquences :** le mécanisme fonctionne identiquement en cloud ou en Instance Locale. *Source : Addendum 1, section 12.5.*

### ADR-007 — Dégradation progressive de licence plutôt que coupure sèche

**Contexte :** les délais de paiement AMU dépassent parfois 3 mois en pratique ; un renouvellement de licence peut prendre du retard pour des raisons administratives, pas de mauvaise foi.
**Décision :** quatre phases (alerte, grâce, dégradée, suspendue) sur 60 jours, jamais de coupure immédiate à l'échéance.
**Alternatives écartées :** suspension immédiate à J+0 — rejetée, contraire à l'esprit d'aide du projet et validée comme telle par Dr Amadou.
**Conséquences :** seuil de 60 jours validé, présenté comme un préavis plutôt qu'une rupture. *Source : Addendum 1, section 12.6, validé le 9 juillet 2026.*

### ADR-008 — PWA plutôt que trois applications natives

**Contexte :** les téléphones doivent couvrir Android, iOS et Huawei ; les Huawei récents n'ont plus les Services Mobiles Google.
**Décision :** une application web progressive unique, sans dépendance GMS ni HMS.
**Alternatives écartées :** trois applications natives séparées — rejetées, coût de maintenance disproportionné pour une équipe de taille limitée, et contournable de toute façon par la contrainte Huawei.
**Conséquences :** limite connue sur iOS (notifications en arrière-plan), compensée par un canal SMS pour les alertes critiques. *Source : Addendum 2, section 17.2.*

### ADR-009 — Canaux d'ingestion génériques plutôt qu'un connecteur par logiciel terrain

**Contexte :** le terrain togolais change de logiciel ou de format sans préavis ; développer un connecteur par éditeur rencontré n'est pas soutenable.
**Décision :** l'Agent n'expose que trois canaux génériques (dossier surveillé, appel local minimal, repli vers le Portail).
**Alternatives écartées :** un connecteur sur mesure par logiciel rencontré comme réflexe par défaut — rejeté, devient l'exception plutôt que la règle (Addendum 2, section 18.5).
**Conséquences :** une nouvelle intégration terrain devient une question de configuration, pas un projet de développement. *Source : Addendum 2, section 17.3.*

### ADR-010 — Python comme langage de FHTP Core

**Contexte :** un langage devait être choisi pour construire FHTP Core.
**Décision :** Python, confirmé par Dr Amadou.
**Alternatives écartées :** aucune envisagée formellement — préférence directe de Dr Amadou, cohérente avec le principe de stabilité déjà retenu (écosystème mature, largement éprouvé).
**Conséquences :** outillage de test verrouillé en conséquence (pytest, FastAPI/Flask, Locust). *Sources : FHTP-KNO-001 section 3.7 ; Addendum 3, section 21.5.*

### ADR-011 — Séquencement volontaire : quatre scénarios en backlog

**Contexte :** urgences, dentaire, téléconsultation, évacuation sanitaire pourraient être rédigés par anticipation.
**Décision :** rester sur les trois scénarios déjà stabilisés (consultation, hospitalisation, pharmacie) ; les quatre autres restent en backlog volontaire.
**Alternatives écartées :** rédiger les quatre scénarios par anticipation — rejeté, ce sont pour l'essentiel des variations de mécanismes déjà couverts, mieux traitées après un premier retour de terrain réel.
**Conséquences :** effort concentré sur ce qui est déjà en usage plutôt que dispersé sur des scénarios hypothétiques. *Source : FHTP-KNO-001, "Décision de séquencement", 7 juillet 2026.*

---

## Journal des versions

| Version | Date | Auteur | Changements |
|---|---|---|---|
| 0.1 | 9 juillet 2026 | Claude (sur demande de Dr Amadou) | Première formalisation de onze décisions déjà prises et déjà tracées dans les journaux des versions existants, mises en forme de fiche ADR structurée (contexte / décision / alternatives écartées / conséquences). Aucune décision nouvelle. |
