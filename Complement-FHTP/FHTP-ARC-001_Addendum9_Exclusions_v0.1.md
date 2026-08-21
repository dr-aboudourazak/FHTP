# FHTP-ARC-001 — Addendum 9, v0.1
## Exclusions de contrat — AMU et CAT, y compris par catégorie de bénéficiaire

**Date :** 9 juillet 2026
**Statut :** brouillon pour validation par Dr Amadou
**À intégrer dans :** FHTP-ARC-001 v0.5, section 6 (modèle de données) et section 10 (flux de validation, précision du pilier concerné).

---

## Note de méthode

Signalé par Dr Amadou, 9 juillet 2026, comme un angle mort réel : les exclusions d'actes cliniques, paracliniques ou de pharmacie varient beaucoup d'un contrat à l'autre — et, pour une même entreprise, entre cadres et exécutants au sein du même contrat. C'est explicitement désigné comme une source majeure de conflit et de perte en gestion tiers-payant. Ce que l'architecture avait déjà, avant ce document :

- Côté AMU : un acte ou médicament absent de Presta+ est exclu de fait (INAM Art. 7) — mécanisme global, correct mais grossier.
- Côté CAT : les flux 10.4-10.6 mentionnent "vérifier les exclusions de la police" — mais sans entité de données dédiée, et surtout sans granularité par catégorie de bénéficiaire au sein d'un même contrat.

Ce document corrige les deux manques.

## 1. Nouvelle entité : Exclusion_Contrat

```
Exclusion_Contrat
  id_exclusion
  id_contrat_payeur (FK, cf. section 6 — Contrat_Payeur existe déjà)
  categorie_beneficiaire   (nullable — CADRE | EXECUTANT | AUTRE ;
                            vide = s'applique à toute la police, renseigné = ne s'applique qu'à cette catégorie)
  type_exclusion           [ACTE | MEDICAMENT | CATEGORIE_ACTE | PATHOLOGIE_PREEXISTANTE]
  code_ou_categorie        (code acte/DCI précis, ou catégorie large — ex: "actes esthétiques", "produits de confort")
  motif                    (texte libre, ex: "non couvert au niveau exécutant selon police X")
  date_version
```

**Pourquoi une entité séparée plutôt qu'un champ sur `Contrat_Payeur` :** un contrat peut porter plusieurs dizaines d'exclusions, à des niveaux différents (police entière ou catégorie précise) — même logique que celle déjà retenue pour ne pas dupliquer l'en-tête d'un payeur dans chaque type d'acte (Addendum 1, section 15.3, `Modele_Payeur_Socle` / `Modele_Document_Payeur`). Ici : une exclusion sans `categorie_beneficiaire` s'applique à tout le monde ; une exclusion avec `categorie_beneficiaire` = `EXECUTANT` ne s'applique qu'à ce niveau, sans toucher aux cadres du même contrat.

## 2. Champ ajouté sur Beneficiaire

```
Beneficiaire
  ...
  categorie_contrat (nullable)   [CADRE | EXECUTANT | AUTRE]
```

Renseigné uniquement quand le contrat du bénéficiaire distingue des niveaux de couverture — pas pertinent pour l'AMU dans son état actuel (la distinction y est INAM/CNSS/Scolaire, pas cadre/exécutant), mais l'entité reste la même pour les deux régimes plutôt que d'en créer une seconde : si l'AMU introduisait un jour une distinction de ce type, aucune nouvelle structure ne serait nécessaire.

## 3. Correction de placement : pilier 2, pas pilier 4

Les flux 10.4-10.6 plaçaient la vérification des exclusions sous le pilier 4 (cohérence documentaire). **Ce n'est pas le bon pilier.** Une exclusion de police est une question de couverture contractuelle — donc pilier 2 (cohérence de régime), au même titre que les restrictions déjà classées là (majorations interdites en AMU, molécules orales exclues en clinique privée). Une exclusion mal classée sous "documentaire" risquerait d'être traitée comme un problème de pièce manquante plutôt que comme un motif de non-couverture — deux natures de rejet différentes, avec des voies de recours différentes.

**Vérification mise à jour, pilier 2 :** pour chaque acte ou médicament du dossier, croiser `Exclusion_Contrat` sur le `Contrat_Payeur` du bénéficiaire **et** sur sa `categorie_beneficiaire` si elle est renseignée. Une exclusion trouvée au niveau police s'applique à tous ; une exclusion trouvée seulement au niveau catégorie ne s'applique qu'aux bénéficiaires de cette catégorie précise.

## 4. Origine et fraîcheur des exclusions

Même logique que le reste des référentiels (section 2.5) : les exclusions sont importées et versionnées par contrat, pas codées en dur. Une police qui change ses exclusions à son renouvellement annuel produit une nouvelle version, sans toucher au moteur de règles lui-même — cohérent avec R-TG-024 déjà retenu pour la variabilité tarifaire CAT.

## 5. Ajout au registre des risques (FHTP-KNO-001, section 12)

**R8 — Exclusion mal appliquée par manque de granularité.** Une exclusion réelle non modélisée (notamment la distinction cadre/exécutant) entraîne soit un remboursement indu, soit un rejet injustifié perçu comme arbitraire par le bénéficiaire — exactement la source de conflit signalée par Dr Amadou. Mitigation : `Exclusion_Contrat` avec granularité par catégorie, comme ci-dessus.

---

## Journal des versions

| Version | Date | Auteur | Changements |
|---|---|---|---|
| 0.1 | 9 juillet 2026 | Claude (sur demande de Dr Amadou) | Correction d'un angle mort identifié par Dr Amadou : les exclusions de contrat n'étaient traitées que génériquement (mention dans les flux CAT, absence de Presta+ côté AMU), sans entité dédiée ni granularité par catégorie de bénéficiaire. Ajout de Exclusion_Contrat (avec categorie_beneficiaire optionnel), du champ categorie_contrat sur Beneficiaire, correction du pilier concerné (2, cohérence de régime, plutôt que 4), et ajout du risque R8 au registre. |
