# FHTP-ARC-001 — Addendum 7, v0.1
## Matrice de traçabilité (TRC)

**Date :** 9 juillet 2026
**Statut :** brouillon pour validation par Dr Amadou
**À intégrer dans :** FHTP-ARC-001 v0.5, nouvelle section 26.

---

## Note de méthode

Le lien réglementation → règle existe déjà, règle par règle, dans les trois PRD. Le lien règle → pilier existe déjà dans le moteur de règles (section 2.1, champ `pilier`). Ce qui manquait : une matrice unique qui croise les quatre maillons — réglementation, règle, pilier, et maintenant le test associé (Addendum 3, section 21) — plutôt que de devoir recouper plusieurs documents à la main.

## 26.1 Structure de la matrice

Une ligne par règle, quatre colonnes fixes :

| Règle | Source réglementaire | Pilier | Cas de test associé |
|---|---|---|---|
| R-TG-017 | Note Circulaire R68 / RP 24-10 | Cohérence documentaire | `test_r68_rejet_immediat` |
| R-TG-014 | RP 24-37 / CAT Art. 14 | Cohérence documentaire | `test_ordonnance_validite_7j` |
| R-TG-020 | RP 24-24 | Complétude administrative | `test_echo_obstetricale_max3` |
| RG-P07 | RP 24-32 | Cohérence tarifaire | `test_substitution_generique_prix` |
| RG-H06 | INAM Art. 31 | Cohérence tarifaire | `test_calcul_sejour_jour_sortie_exclu` |
| *(...)* | *(...)* | *(...)* | *(...)* |

*(Extrait illustratif — la matrice complète couvre l'ensemble des règles des trois PRD et des RP24, de l'ordre de 100 à 150 lignes, cf. Addendum 3, section 21.5.)*

## 26.2 Ce que cette matrice permet concrètement

- Vérifier qu'aucune règle n'est dépourvue de test avant une mise en production — un vide dans la colonne "cas de test" est un signal, pas un détail.
- Retrouver instantanément, en cas de contestation d'un rejet par un centre, le texte réglementaire exact qui justifie la règle appliquée.
- Mesurer la couverture réelle du modèle de confiance à six piliers : si un pilier a très peu de règles rattachées, c'est soit qu'il est réellement moins chargé (cohérence graphique, backlog), soit qu'une réglementation existante n'a pas encore été traduite en règle.

## 26.3 Ce qui reste à faire

La matrice complète (toutes les règles, pas cet extrait illustratif) reste à construire ligne par ligne à partir des trois PRD — travail mécanique une fois la structure validée, pas une nouvelle conception. Le rattachement au composant technique (quel module du Core évalue quelle règle) pourra s'ajouter comme cinquième colonne une fois le développement engagé, pas avant.

---

## Journal des versions

| Version | Date | Auteur | Changements |
|---|---|---|---|
| 0.1 | 9 juillet 2026 | Claude (sur demande de Dr Amadou) | Première structure de la matrice de traçabilité (règle → source réglementaire → pilier → cas de test), avec extrait illustratif de cinq règles. Construction complète de la matrice laissée comme tâche mécanique de suivi, pas de conception. |
