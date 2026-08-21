# FHTP-ARC-001 — Addendum 4, v0.1
## Complément Sécurité (SEC) — modèle de menace, rétention, réponse à incident

**Date :** 9 juillet 2026
**Statut :** brouillon pour validation par Dr Amadou
**À intégrer dans :** FHTP-ARC-001 v0.5, section 8 (Sécurité et Confidentialité), comme nouvelles sous-sections 8.6 à 8.8.

---

## 8.6 Modèle de menace structuré (STRIDE)

La table de failles déjà posée (F1-F7, section 8.2) couvre bien la plupart des catégories STRIDE, mais de façon dispersée. Ce tableau les reclasse, et ajoute deux failles qui n'étaient pas encore couvertes explicitement.

| Catégorie STRIDE | Couvert par | Nouvelle faille identifiée |
|---|---|---|
| **Spoofing** (usurpation) | F4 (RBAC), F5 (secrets scopés par centre) | **F8** — rien n'empêchait qu'un Agent (Addendum 2, section 17.3) falsifié se fasse passer pour l'agent légitime d'un centre. Mitigation retenue : authentification mutuelle (mTLS ou certificat client par agent), pas seulement un jeton applicatif. |
| **Tampering** (altération) | F1 (hash à l'ancrage), F2 (chaînage du Journal de Conformité) | **F9** — sur le profil Instance Locale (Addendum 2, section 17.4), un administrateur local avec accès direct à la base pourrait altérer le cache local des référentiels ou des règles, pas seulement le Journal de Conformité. Mitigation retenue : les référentiels et règles téléchargés localement portent aussi une signature vérifiée à réception, comme les documents de la section 8.4 — une modification locale invalide la signature et déclenche un retour au mode dégradé strict. |
| **Repudiation** (répudiation) | F2 (chaînage + ancrage externe) | — |
| **Information Disclosure** (divulgation) | Privacy by Design (8.1) — aucun contenu médical stocké | — |
| **Denial of Service** | F6 (rate limiting, disjoncteur par connecteur) | Renforcé par la limitation de fréquence différenciée déjà posée pour la soumission groupée (Addendum 1, section 12.8) — un lot anormalement volumineux reste absorbé sans bloquer les autres centres. |
| **Elevation of Privilege** (élévation de privilège) | F4 (RBAC par rôle réel) | — |

## 8.7 Politique de rétention et de suppression des données

FHTP ne stocke jamais le contenu médical brut (8.1) — la question de rétention porte donc sur les métadonnées de facturation, les hash d'intégrité, et le Journal de Conformité.

- **Durée de conservation de l'audit :** à confirmer juridiquement avec Dr Amadou — la durée doit s'aligner sur le délai de prescription applicable aux litiges de remboursement au Togo, pas sur une durée arbitraire. Point explicitement laissé ouvert plutôt que de fixer un chiffre sans base réglementaire.
- **Fin de contrat d'un centre :** les métadonnées et rapports du centre lui appartiennent et restent exportables sur demande (cohérent avec l'accès en lecture toujours garanti même en licence suspendue, Addendum 1, section 12.6). Les données agrégées et anonymisées utiles à la détection de schémas de fraude au niveau du projet peuvent être conservées au-delà — à condition que l'anonymisation soit réelle, pas seulement déclarative.
- **Droit à l'oubli d'un bénéficiaire :** FHTP ne détenant pas le contenu médical, l'essentiel de la demande d'un patient renvoie vers l'établissement qui, lui, détient le dossier — cohérent avec le principe déjà posé en 8.1.

## 8.8 Plan de réponse à incident, en cas de compromission réelle

Le Journal de Conformité chaîné et ancré (F2) devient l'outil central d'investigation, pas seulement un registre passif :

1. **Détection** : alerte automatique sur rupture de chaîne du Journal, échec de signature d'un référentiel local (F9), ou volume anormal détecté par le rate limiting (F6/8.6).
2. **Confinement** : révocation immédiate du jeton compromis (scope limité par centre, F5), rotation des secrets du connecteur concerné.
3. **Notification** : centre concerné, puis payeur si des dossiers de ce centre ont transité vers lui pendant la fenêtre de compromission suspectée.
4. **Investigation** : reconstruction de la portée exacte à partir du Journal de Conformité chaîné — c'est précisément ce que l'ancrage externe (section 8.5) est censé permettre de prouver de façon opposable.
5. **Remédiation et retour d'expérience** : nouvelle entrée dans le registre des risques (RSK, prochaine étape), pas seulement une correction technique isolée.

---

## Journal des versions (entrée à ajouter à la section existante)

| Version | Date | Auteur | Changements |
|---|---|---|---|
| 0.1 | 9 juillet 2026 | Claude (sur demande de Dr Amadou) | Complément de la section Sécurité : modèle de menace STRIDE reclassant F1-F7 et ajoutant deux failles (F8 usurpation d'agent, F9 altération locale du cache sur Instance Locale) ; politique de rétention et de suppression des données, avec la durée de conservation de l'audit explicitement laissée ouverte faute de base réglementaire confirmée ; plan de réponse à incident en cinq étapes s'appuyant sur le Journal de Conformité chaîné comme outil d'investigation central. |
