# FHTP-PRD-002
## Product Requirements Document — Scénario 2 : Hospitalisation en clinique privée (Togo)

**Version 1.5 — Renvoi vers le décret 2023-100/PR (comité de régulation)**
**Date :** 6 juillet 2026
**Statut :** version de référence
**Documents de référence :** FHTP-KNO-001 Knowledge Book v0.19, FHTP-PRD-001 v1.5, FHTP-REF-001 v1.3

---

## 1. Objet

Ce document spécifie le comportement attendu de la FITTER Health Trust Platform (FHTP) pour le scénario d'une hospitalisation en clinique privée ou établissement public au Togo (médecine, chirurgie, maternité). Il réutilise le socle commun de FHTP-PRD-001 et détaille les règles spécifiques à l'hospitalisation.

---

## 2. Contexte

L'hospitalisation présente des risques de facturation plus élevés en raison des montants en jeu, des séjours prolongés et de la difficulté de contrôle. FHTP doit appliquer les règles réglementaires de calcul de séjour, de limitation de délivrance des médicaments injectables à l'hôpital, et d'autorisation préalable.

---

## 3. Acteurs
Identiques à FHTP-PRD-001 (les intervenants sont le médecin traitant, le chirurgien et l'anesthésiste, chacun identifié par son numéro d'Ordre et son code prescripteur AMU).

---

## 4. Périmètre

### Dans le périmètre
- Hospitalisation en médecine, chirurgie, ou maternité au Togo.
- Les actes chirurgicaux, anesthésiques et soins infirmiers associés au séjour.
- La délivrance de produits pharmaceutiques pendant l'hospitalisation.

### Hors périmètre
- Consultation externe (PRD-001) et pharmacie d'officine externe (PRD-003).

---

## 5. Parcours utilisateur

### 5.1 Parcours d'admission (Programmé vs. Urgence)

**US-01 — Admission programmée**
- Le patient se présente avec une demande d'entente préalable (PEC/EP) approuvée par le médecin-conseil.
- Le système FHTP vérifie le numéro de PEC et bloque l'admission en tiers-payant si la PEC est manquante ou invalide.

**US-02 — Admission en urgence (Délai de grâce)**
- Le patient est admis d'urgence sans PEC préalable.
- Le cabinet dispose d'un **délai de grâce de 24 heures** (ou jusqu'au premier jour ouvré si week-end/jour férié) pour soumettre l'avis d'hospitalisation et régulariser le dossier (RG-H07 / RP 24-17).
- Le système FHTP n'émet pas de rejet automatique pour PEC manquante durant cette période de grâce.

### 5.2 Parcours de soins et de séjour

**US-03 — Facturation de la chambre et durée de séjour**
- À la sortie, le système calcule automatiquement le nombre de jours d'hospitalisation : `stay_days = date_sortie - date_entree`.
- Le système applique la règle de l'INAM excluant le jour de la sortie du calcul des nuitées (RG-H06).
- Si l'hospitalisation est une mise en observation / hôpital de jour, la durée est limitée à **3 jours maximum** (RG-H09).
- Pour une hospitalisation de maternité, le séjour type est de 2 à 5 jours. Au-delà de 5 jours, le dossier doit être reclassé en chirurgie (si césarienne) ou médecine, avec une justification médicale obligatoire (RG-H02).

**US-04 — Prescription et administration de médicaments à l'hôpital**
- Le médecin prescrit les injectables sur la feuille spécifique d'hospitalisation (RP 24-35).
- La délivrance en une seule fois de médicaments injectables (voie parentérale) est limitée à **3 jours de traitement** maximum (RG-H08).
- Dans le cadre de l'AMU, les médicaments oraux ne sont pas remboursables s'ils sont facturés directement par la clinique privée (RG-H11).

**US-05 — Clôture et soumission du dossier**
- Le médecin rédige le rapport médical de sortie obligatoire contenant les 6 éléments requis (dates, motif, bilans, traitements avec noms commerciaux, évolution, ordonnance de sortie).
- Le médecin appose sa signature et clôture l'ordonnance de sortie par trois traits obliques (`///`).
- La clinique soumet le dossier complet sous 30 jours.

---

## 6. Règles métier (Hospitalisation)

| Code | Règle Métier | Source |
|---|---|---|
| **RG-H01** | Un acte soumis à PEC réalisé sans PEC initiale ou complémentaire n'est pas remboursé (hors urgence régularisée). | Confirmé par Dr Amadou |
| **RG-H02** | Une maternité dépassant 5 jours doit être reclassée (médecine/chirurgie) avec justification dans le rapport. | Confirmé par Dr Amadou |
| **RG-H03** | Le rapport médical de sortie est obligatoire. L'absence de rapport est tolérée en secteur public, mais bloque le remboursement en secteur privé. | Confirmé par Dr Amadou / Convention |
| **RG-H04** | Format de facturation : facture globale pour le CAT, fiches paysage multiples pour l'AMU (pas de forfait global). | Confirmé par Dr Amadou |
| **RG-H05** | Le dépassement du délai de transmission (30 jours) déclenche une alerte administrative, mais pas un rejet automatique. | Confirmé par Dr Amadou |
| **RG-H06** | **Calcul du séjour :** Le séjour facturé est égal à `date_sortie - date_entree`. Le jour de sortie est exclu de la facturation des nuitées. | INAM Art. 31 |
| **RG-H07** | **Urgence :** Pour les actes chirurgicaux, anesthésiques et hospitalisations d'urgence, la régularisation PEC est autorisée a posteriori dans les **24 heures** (ou le 1er jour ouvré). | RP 24-17 / INAM Art. 19 |
| **RG-H08** | **Injectables :** La délivrance de médicaments parentéraux (injectables) en cours de séjour ne doit pas dépasser **3 jours de traitement** en une seule fois. | RP 24-30 |
| **RG-H09** | **Hôpital de jour :** L'hôpital de jour doit être facturé en "mise en observation" (code MEO), limitée à **3 jours maximum**. | RP 24-16 |
| **RG-H10** | **Diagnostic d'entrée :** Le diagnostic de séjour doit être encodé en CIM-10. L'usage du code R68 est interdit au remboursement. | Note Circulaire R68 |
| **RG-H11** | **Molécules orales :** Les cliniques privées ne sont remboursées que pour les médicaments injectables. Les médicaments oraux sont exclus du tiers-payant clinique (sauf dérogation). | RP 24-33 |

---

## 7. Modèle de confiance — Spécificités Hospitalisation

Le dossier d'hospitalisation est évalué selon les six piliers avec les contrôles élargis suivants :

- **Cohérence tarifaire** : Vérifie le calcul exact du séjour `date_sortie - date_entree` (RG-H06) et la facturation MEO pour l'hôpital de jour (RG-H09). Comme pour la consultation (PRD-001, R-TG-024), le taux n'est pas fixe et les contrats CAT "Frais Réel" ne se prêtent pas à une comparaison tarifaire externe.
- **Cohérence documentaire** : Présence du rapport médical avec les 6 éléments. Présence du symbole `///` sur l'ordonnance de sortie. Croisement des médicaments facturés avec les injectables mentionnés au rapport.
- **Cohérence prescripteur** : Codes prescripteurs valides pour tous les intervenants (chirurgien, anesthésiste). Vérification que le chirurgien/anesthésiste n'a pas prescrit pour ses ayants droit.
- **Cohérence de régime** : Exclusion des médicaments oraux en clinique privée AMU (RG-H11). Limite de délivrance d'injectables à 3 jours (RG-H08).
- **Complétude administrative** : Présence des numéros de PEC initiale et complémentaires pour chaque acte programmé lourd.

**Alerte recours / régularisation :** L'hospitalisation concentre les rejets les plus sensibles, notamment autour de la PEC, de l'urgence, de la prolongation et du rapport de sortie. FHTP doit donc alerter en amont lorsqu'une pièce manque ou qu'un délai risque d'être dépassé. Si un rejet survient malgré les contrôles préventifs, le système déclenche une alerte recours contextualisée selon le régime (AMU, CAT ou double couverture), le motif et les pièces régularisables. En AMU, la voie de recours devant le comité de régulation (PRD-001, R-TG-025) s'applique aussi à l'hospitalisation.
