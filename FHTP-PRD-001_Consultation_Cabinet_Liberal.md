# FHTP-PRD-001
## Product Requirements Document — Scénario 1 : Consultation en cabinet libéral (Togo)

**Version 1.5 — Ajout du décret 2023-100/PR (comité de régulation, voie de recours)**
**Date :** 7 juillet 2026
**Statut :** version de référence
**Document de référence :** FHTP-KNO-001 Knowledge Book v0.19, FHTP-REF-001 v1.3

---

## 1. Objectif du document

Ce PRD spécifie le fonctionnement de la FITTER Health Trust Platform (FHTP) pour le scénario d'une consultation en cabinet médical libéral au Togo. Il régit la conformité et la validation des dossiers de soins externes (consultations, soins ambulatoires, prescriptions de biologie, d'imagerie et de pharmacie) selon les régimes obligatoires (AMU-INAM et AMU-CNSS) et privés (CAT).

---

## 2. Contexte et problème à résoudre

La crise de confiance entre prestataires de soins et assureurs (AMU et privés) engendre des délais de remboursement longs et incertains (dépassant parfois 3 mois), ce qui incite certains centres à surfacturer par anticipation. FHTP vise à ramener ce délai d'environ deux tiers en fiabilisant et en validant automatiquement les dossiers de facturation dès leur transmission.

---

## 3. Acteurs

| Acteur | Rôle |
|---|---|
| Patient | Bénéficiaire des soins (Couvert par l'AMU-INAM/CNSS, par le privé CAT, par les deux, ou en paiement direct). |
| Médecin / Prescripteur | Réalise la consultation, prescrit et facture. Identifié par son numéro d'Ordre et son code prescripteur AMU. |
| Paramédicaux | Infirmiers, sages-femmes ou assistants réalisant des actes de soins sur ordonnance. |
| Cabinet médical | Formation sanitaire privée agréée par le Ministère de la Santé (identifiée par son code formation AMU). |
| Payeur | INAM, CNSS, ou assureur privé (CAT) — connecteur générique. |
| Praticien-conseil | Assure le contrôle médical et valide les ententes préalables (PEC/EP). |

---

## 4. Périmètre

### Dans le périmètre de ce PRD
- Consultation générale ou spécialisée en cabinet médical libéral en présentiel.
- Les quatre circuits de remboursement : AMU seule, double couverture (AMU + complémentaire privé), privé seul, paiement direct.
- La prescription d'actes (biologie, imagerie) et de médicaments associée à la consultation.
- L'application du modèle de confiance à six piliers enrichi des directives AMU 2024 (RP 24) et de la restriction de codage CIM-10 (R68).

### Hors périmètre
- Hospitalisation (FHTP-PRD-002) et Délivrance autonome en pharmacie (FHTP-PRD-003).

---

## 5. Parcours utilisateur

### 5.1 Parcours nominal — Patient couvert par l'AMU (INAM ou CNSS)

**US-01 — Accueil et vérification des droits**
*En tant que réceptionniste du cabinet, je veux saisir ou scanner le numéro de carte AMU du patient afin de vérifier l'éligibilité de ses droits et d'identifier le guichet (INAM pour le public/étudiants, CNSS pour le privé).*
- Les droits du patient sont validés via le connecteur payeur (R-TG-007).
- Si le patient est un élève/étudiant (AMU Scolaire), le taux de couverture est automatiquement fixé à 100% (ticket modérateur = 0 FCFA) (R-TG-023).
- Si absent, une attestation papier transitoire pour enfant de moins de 6 mois (RP 24-12) ou adulte est saisie (dossier marqué pour audit renforcé).

**US-02 — Consultation médicale et diagnostic**
*En tant que médecin, je veux saisir le diagnostic et prescrire des actes ou des médicaments afin de soigner le patient.*
- Le médecin doit obligatoirement encoder le diagnostic sous forme de code **CIM-10** (R-TG-017).
- Le système bloque automatiquement l'usage du code d'affection **R68** ("autres symptômes et signes généraux") proscrit par l'INAM.
- À la fin de la prescription, le médecin trace obligatoirement trois traits obliques (`///`) sous la dernière ligne pour clore le dossier physique/numérique (R-TG-022).

**US-03 — Prescription d'actes (Biologie, Imagerie)**
*En tant que médecin, je veux prescrire des examens complémentaires au patient.*
- Les demandes d'actes lourds (TDM/Scanner ou IRM) sont contrôlées :
  - Le scanner (TDM) est réservé aux médecins (R-TG-019).
  - L'IRM est strictement réservée aux médecins spécialistes déclarés (R-TG-019).
- Pour les échographies obstétricales, la limite est fixée à 3 par grossesse ; au-delà, le système exige une demande d'entente préalable (PEC) (R-TG-020).

**US-04 — Prescription médicamenteuse**
*En tant que médecin, je veux prescrire des médicaments remboursables.*
- Le système croise chaque ligne avec la base **Presta+** (ou catalogue AMU Scolaire).
- Si le prescripteur est un paramédical (infirmier, sage-femme) :
  - Le système bloque la prescription des molécules interdites en exercice paramédical (fluoroquinolones, AINS oraux spécifiques, collyres corticoïdes) sauf si une PEC est rattachée (R-TG-021).
- Si le traitement ambulatoire prescrit dépasse une durée de **15 jours**, le système affiche une alerte exigeant une PEC (R-TG-015).
- En cabinet privé, seuls les médicaments par voie parentérale (injectables) sont remboursés par l'AMU (R-TG-011) ; les médicaments oraux sont signalés "non remboursables en clinique".

**US-05 — Soumission et facturation du dossier**
*En tant que cabinet, je veux soumettre la facture mensuelle avec toutes les pièces justificatives.*
- Le système calcule la part tiers-payant (payeur) et la part ticket modérateur (patient) selon le barème officiel.
- Pour une visite de contrôle intervenant dans les **15 jours** (cabinet privé) ou **30 jours** (structure publique) pour le même motif d'affection, le système applique un tarif de consultation nul (0 FCFA) (R-TG-016).
- Le dossier complet (facture, feuille de soins signée avec le symbole `///`, ordonnance, reçu du ticket modérateur) est soumis au plus tard le 5 du mois suivant (R-TG-002).

---

## 6. Règles métier (FHTP Core - Consultation)

| Code | Règle Métier | Source |
|---|---|---|
| **R-TG-001** | Tout dossier AMU doit comporter un code formation sanitaire et un code prescripteur valides. | Confirmé par Dr Amadou |
| **R-TG-002** | Tout dossier doit être soumis au plus tard le 5 du mois suivant. | Confirmé par Dr Amadou |
| **R-TG-003** | Un reçu de paiement du ticket modérateur est obligatoire, sauf case d'exemption double couverture. | Confirmé par Dr Amadou |
| **R-TG-004** | Tout médicament facturé sous l'AMU doit être enrôlé dans Presta+ (ou catalogue AMU Scolaire). | Confirmé par Dr Amadou |
| **R-TG-005** | Le tarif d'un médicament ne peut pas dépasser le prix de référence de la base Presta+. | Confirmé par Dr Amadou |
| **R-TG-006** | En cas de double couverture, l'AMU rembourse en premier et le privé (CAT) en complémentaire. | Confirmé par Dr Amadou |
| **R-TG-007** | L'AMU ou le privé valide l'éligibilité via le connecteur de services FHTP (API, portail ou import local). | Confirmé par Dr Amadou |
| **R-TG-008** | Le cachet du prescripteur doit obligatoirement mentionner son numéro d'Ordre professionnel. | Convention INAM |
| **R-TG-009** | Tout rejet de dossier doit être motivé par écrit et déclencher une alerte recours contextualisée. Le délai n'est pas figé dans FHTP : il dépend du régime (AMU, CAT, double couverture), du motif et de la pratique terrain. | Confirmé par Dr Amadou |
| **R-TG-010** | Seuls les actes effectués personnellement par un prescripteur qualifié sont remboursables. | Convention CAT / INAM |
| **R-TG-011** | Les majorations (nuit, dimanche) ne s'appliquent qu'au circuit CAT, jamais à l'AMU. En cabinet privé sous AMU, seuls les médicaments parentéraux (injectables) sont remboursés. | Convention CAT / RP 24-33 |
| **R-TG-012** | Le circuit de remboursement est une donnée à vérifier au cas par cas. | Confirmé par Dr Amadou |
| **R-TG-013** | Un médecin ne peut facturer que sous une seule spécialité déclarée. | Confirmé par Dr Amadou |
| **R-TG-014** | Une ordonnance a une validité maximale de **7 jours** pour être honorée en pharmacie. | RP 24-37 / CAT Art. 14 |
| **R-TG-015** | Toute prescription ambulatoire pour une durée de traitement supérieure à **15 jours** exige une PEC. | RP 24-31 / INAM Art. 15 |
| **R-TG-016** | Les visites de suivi ne sont pas facturables si elles surviennent sous 15 jours (privé) ou 30 jours (public) pour le même motif. | RP 24-11 |
| **R-TG-017** | Le codage du diagnostic en code **CIM-10** est obligatoire. L'usage du code **R68** ("autres symptômes") est interdit (rejet d'office). | Note Circulaire R68 / RP 24-10 |
| **R-TG-018** | L'auto-prescription et la prescription à ses propres ayants droit directs sont strictement interdites. | RP 24-05 & RP 24-06 |
| **R-TG-019** | La prescription de scanner (TDM) exige un code médecin (`01`). Celle d'IRM exige un spécialiste. | RP 24-25 & RP 24-26 |
| **R-TG-020** | Maximum 3 échographies obstétricales par grossesse. Au-delà, une PEC préalable est exigée. | RP 24-24 |
| **R-TG-021** | Interdiction aux prescripteurs paramédicaux de prescrire fluoroquinolones, AINS oraux et collyres corticoïdes sans PEC. | Directive Paramédicaux 2024 |
| **R-TG-022** | Toute prescription doit être close par trois traits obliques (`///`) directement sous la dernière ligne. | RP 24-03 |
| **R-TG-023** | Pour le régime AMU Scolaire, le taux de prise en charge INAM est de 100% (ticket modérateur = 0 FCFA). | Référentiel Scolaire 2024 |
| **R-TG-024** | Le taux de remboursement n'est jamais fixe : il varie acte par acte en AMU (fichiers Presta+), et d'un contrat à l'autre en CAT. Pour les contrats CAT en "Frais Réel", la base de remboursement est le montant facturé lui-même : aucune comparaison à un tarif de référence externe n'est possible pour ce type de contrat. | Confirmé par Dr Amadou |
| **R-TG-025** | En cas de décision défavorable du contrôle médical AMU, le bénéficiaire ou le prestataire dispose d'un droit de recours devant le comité de régulation de l'AMU, qui désigne un médecin expert pour une contre-expertise indépendante. Les frais d'expertise sont à la charge de la partie perdante. Un refus de contrôle médical entraîne la suspension du paiement (prestataire) ou de la prise en charge (assuré) pour la période concernée. | Décret n°2023-100/PR, art. 9 et 11 |

---

## 7. Modèle de données (FHTP Core)

- **Patient** : id_patient, numero_carte_AMU, type_regime (Scolaire/Standard), guichet_AMU (INAM/CNSS/aucun), numero_assurance_privee, parent_assure_id (si ayant droit).
- **Prescripteur** : id_prescripteur, numero_ordre, code_prescripteur_AMU (détermine si médecin `01` ou paramédical `02`/`04`), specialite_declaree, structure_rattachement_ids.
- **Acte_Medical** : id_acte, code_acte (CIM-9/AMU), libelle, date, montant_facture, base_remboursement, taux_payeur, part_patient, diagnostic_code (CIM-10), pec_associee_id.
- **Prescription_Medicament** : id_prescription, dci, nom_commercial, dosage, duree_traitement_jours, quantite, voie_administration (orale/parentérale), prix_unitaire, enrole_presta_plus, pec_associee_id.

---

## 8. Modèle de confiance à six piliers

Chaque dossier soumis est analysé par l'FHTP Core selon les critères suivants :

| Pilier | Vérifications effectuées | Statut |
|---|---|---|
| **Cohérence tarifaire** | Conforme aux tarifs réglementaires (Presta+ / AMU Scolaire ou barème CAT). Vérifie R-TG-005, R-TG-011 et R-TG-016 (suivi gratuit). **Nuance confirmée par Dr Amadou (6 juillet 2026) : il n'existe pas de taux fixe unique, ni côté AMU (le taux varie acte par acte selon les fichiers Presta+ réels) ni côté CAT (le barème varie d'un contrat à l'autre). Certains contrats CAT sont en "Frais Réel" : la base de remboursement est directement le montant facturé par le prestataire, sans tarif de référence à comparer. Pour ces contrats, ce pilier se limite à une vérification de cohérence interne (absence de doublons, cohérence avec le diagnostic), sans comparaison tarifaire externe.** | Conforme / À vérifier / Anomalie |
| **Cohérence documentaire** | Diagnostic CIM-10 présent (excluant le code R68). Prescription close par `///`. Correspondance entre actes facturés et ordinogrammes nationaux. | Conforme / À vérifier / Anomalie |
| **Cohérence prescripteur** | Code prescripteur valide et rattaché à l'établissement. Vérification des restrictions paramédicales (R-TG-021) et spécialités d'imagerie (R-TG-019). | Conforme / À vérifier / Anomalie |
| **Cohérence de régime** | Application correcte des règles AMU (pas de majorations, restrictions orales en clinique privée) ou CAT. | Conforme / Anomalie |
| **Complétude administrative** | Présence des codes, dates, signatures, reçu du ticket modérateur, attestations de moins de 6 mois, et numéros de PEC valides (R-TG-015, R-TG-020). | Conforme / Anomalie |
| **Cohérence graphique** | (Backlog) Analyse de régularité de la signature du médecin. | À vérifier |

**Alerte recours / régularisation :** FHTP doit travailler en amont pour éviter les rejets. Lorsqu'un rejet survient malgré les contrôles préventifs, ou lorsqu'un risque de rejet est détecté, le système signale au prestataire qu'une action est nécessaire, liste les pièces ou corrections attendues, et affiche un délai indicatif selon le régime concerné (AMU, CAT ou double couverture). En AMU, si le rejet fait suite à un contrôle médical défavorable, FHTP doit présenter explicitement la voie de recours devant le comité de régulation (R-TG-025), et non se limiter à une simple régularisation administrative.

**Décisions automatisées :**
- Tous les piliers **Conforme** $ightarrow$ **Paiement automatique (Fast-Track)**.
- Un ou plusieurs piliers **À vérifier** et aucun **Anomalie** $ightarrow$ **Contrôle rapide** (évaluation documentaire).
- Au moins un pilier **Anomalie** ou diagnostic **R68** $ightarrow$ **Rejet direct ou Audit approfondi**.
- Attestation papier transitoire $ightarrow$ **Contrôle renforcé systématique**.
