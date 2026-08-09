# FHTP-PRD-003
## Product Requirements Document — Scénario 3 : Délivrance en pharmacie (Togo)

**Version 1.4 — Renvoi vers le décret 2023-100/PR (comité de régulation)**
**Date :** 6 juillet 2026
**Statut :** version de référence
**Documents de référence :** FHTP-KNO-001 Knowledge Book v0.19, FHTP-PRD-001 v1.5, FHTP-PRD-002 v1.5, FHTP-REF-001 v1.3

---

## 1. Objet

Ce document spécifie le comportement attendu de la FITTER Health Trust Platform (FHTP) pour le scénario de la délivrance de médicaments en pharmacie d'officine au Togo (prescription ponctuelle ou renouvellement chronique). Il s'intègre aux logiciels de vente existants en officine.

---

## 2. Contexte

Les logiciels de vente des pharmacies togolaises intègrent déjà les bases locales de Presta+. FHTP intervient comme couche de contrôle et de validation pour vérifier la conformité de l'ordonnance (validité temporelle, habilitation du prescripteur, règles de substitution de génériques, et ententes préalables).

---

## 3. Acteurs
Identiques à FHTP-PRD-001 (les intervenants clés sont le patient, le pharmacien d'officine et le médecin prescripteur).

---

## 4. Périmètre

### Dans le périmètre
- Délivrance sur ordonnance ponctuelle ou mensuelle chronique (TPC).
- Validation de la conformité de l'ordonnance et du ticket modérateur.
- Contrôle de la validité temporelle de la prescription.
- Contrôle des substitutions de génériques.

### Hors périmètre
- Consultation externe (PRD-001) et administration de médicaments en hospitalisation (PRD-002).

---

## 5. Parcours utilisateur

### 5.1 Parcours nominal — Délivrance en Tiers-Payant AMU

**US-01 — Présentation de l'ordonnance et vérification**
- Le patient présente sa carte AMU et son ordonnance.
- Le pharmacien vérifie les mentions de l'ordonnance.
- Le système FHTP vérifie la validité de la prescription : `Date de délivrance - Date de prescription` doit être **inférieur ou égal à 7 jours** (RG-P06). Si supérieur, l'ordonnance est expirée et le remboursement AMU est bloqué.

**US-02 — Contrôle de la prescription paramédicale**
- Le système FHTP extrait le code prescripteur de l'ordonnance.
- Si le prescripteur n'est pas médecin (`01`) ni dentiste (`03`) :
  - Le système bloque automatiquement la délivrance de médicaments proscrits aux paramédicaux ( fluoroquinolones, AINS oraux, injectables) sauf si un numéro de PEC valide est rattaché (RG-P09).

**US-03 — Substitution générique (DCI)**
- Le pharmacien propose une substitution par un bioéquivalent générique.
- Le système FHTP valide la substitution si :
  - La base de remboursement du médicament substitué est **inférieure ou égale** à celle du médicament initial (RG-P07).
  - Si le prix du substituant dépasse celui du produit initial, le pharmacien doit saisir l'accord du médecin traitant et l'approbation du médecin-conseil pour obtenir le remboursement.
  - Le pharmacien inscrit le substituant en rouge sur la feuille physique.

**US-04 — Limitation des quantités (Durée de traitement)**
- Le système FHTP contrôle les quantités prescrites.
- Si la prescription ambulatoire d'un médicament dépasse **15 jours de traitement** (plusieurs boîtes), le système bloque le tiers-payant tant qu'aucun accord préalable (PEC) n'est fourni (RG-P12).
- Le système vérifie que le document de prescription est bien clos par trois traits obliques (`///`) sous la dernière ligne pour prévenir les rajouts de complaisance (RG-P10).

**US-05 — Facturation et vente**
- Si le prix public de cession de la pharmacie est inférieur au prix de base AMU de Presta+, le médicament doit être facturé au prix public de la pharmacie, le plus bas (RG-P11).
- Le patient règle le ticket modérateur et reçoit son reçu.

---

## 6. Règles métier (Pharmacie d'officine)

| Code | Règle Métier | Source |
|---|---|---|
| **RG-P01** | Un médicament non enrôlé dans Presta+ (ou catalogue AMU Scolaire) n'est pas remboursé par l'AMU. | Confirmé par Dr Amadou |
| **RG-P02** | Pour les pathologies chroniques, le payeur délivre 3 à 6 PEC/EP mensuelles en une seule fois. | Confirmé par Dr Amadou |
| **RG-P03** | Chaque PEC mensuelle mentionne les médicaments autorisés, la base de remboursement globale et le ticket modérateur. | Confirmé par Dr Amadou |
| **RG-P04** | Le pharmacien utilise son logiciel de vente interfacé avec Presta+ pour les calculs de base. | Confirmé par Dr Amadou |
| **RG-P05** | En cas de médicament non enrôlé, le patient choisit entre l'achat à 100% à sa charge ou la substitution par un médecin. | Confirmé par Dr Amadou |
| **RG-P06** | **Validité temporelle :** Une ordonnance n'est valable que pendant **7 jours** maximum après sa date d'émission pour être délivrée. | RP 24-37 / CAT Art. 14 |
| **RG-P07** | **Substitution :** La substitution générique est autorisée si la base de remboursement du substituant est $\le$ à celle du médicament initial. Si le prix est supérieur, l'accord préalable du médecin traitant et du médecin-conseil est obligatoire. | RP 24-32 |
| **RG-P08** | **Code R68 :** Les ordonnances prescrites sous le code diagnostic CIM-10 R68 sont exclues du remboursement en pharmacie. | Note Circulaire R68 |
| **RG-P09** | **Restriction paramédicale :** Blocage automatique du remboursement des molécules de la directive paramédicale 2024 si prescrites par un non-médecin (sans PEC). | Directive Paramédicaux 2024 |
| **RG-P10** | **Traits obliques :** L'ordonnance scannée doit se terminer par les trois traits obliques (`///`). | RP 24-03 |
| **RG-P11** | **Prix le plus bas :** Si le prix public de cession en pharmacie est inférieur au tarif AMU, facturer au prix public le plus bas. | RP 24-34 |
| **RG-P12** | **Limite de durée :** La prescription ambulatoire de plus de **15 jours de traitement** (plusieurs boîtes) d'un médicament exige une PEC. | RP 24-31 |

---

## 7. Modèle de confiance — Spécificités Pharmacie

- **Cohérence tarifaire** : Vérifie l'application du prix le plus bas (RG-P11) et le respect des tarifs Presta+. Comme pour la consultation (PRD-001, R-TG-024), le taux AMU varie acte par acte et le barème CAT varie d'un contrat à l'autre ; les contrats "Frais Réel" ne se comparent à aucun tarif de référence.
- **Cohérence documentaire** : Présence des trois traits obliques `///` sur l'ordonnance. Non-délivrance d'ordonnances expirées (> 7 jours). Diagnostic CIM-10 présent et différent du code R68.
- **Cohérence prescripteur** : Habilitation du prescripteur (médecin/paramédical) croisée avec les restrictions paramédicales (RG-P09).
- **Cohérence de régime** : Limite de délivrance à 15 jours sans PEC (RG-P12). Respect des règles de substitution bioéquivalente (RG-P07).

**Alerte recours / régularisation :** En officine, FHTP doit éviter de bloquer inutilement le patient au comptoir. Les risques régularisables (pièce manquante, ordonnance à clarifier, substitution à justifier, PEC/TPC attendue) déclenchent une alerte au pharmacien et au prestataire concerné. En cas de rejet effectif, FHTP déclenche une alerte recours contextualisée selon le régime (AMU, CAT ou double couverture), le motif et les pièces à produire. En AMU, la voie de recours devant le comité de régulation (PRD-001, R-TG-025) s'applique aussi à la pharmacie.
