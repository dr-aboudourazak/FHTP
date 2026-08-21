# FHTP-ARC-001 — Addendum 8, v0.1
## Request for Change (RFC)

**Date :** 9 juillet 2026
**Statut :** brouillon pour validation par Dr Amadou
**À intégrer dans :** FHTP-ARC-001 v0.5, nouvelle section 27.

---

## Note de méthode

De fait, chaque addendum validé par Dr Amadou dans ce fil de travail a fonctionné comme une RFC informelle : une proposition, une discussion, une décision, une trace datée dans un journal des versions. Ce document formalise juste ce déroulé en gabarit réutilisable, dimensionné pour un projet à un seul décideur aujourd'hui — pas un processus lourd pensé pour une grande équipe qui n'existe pas encore.

## 27.1 Gabarit RFC

```
RFC-XXX — [titre court]
Date :
Demandeur :
Contexte : pourquoi ce changement est proposé
Changement proposé : ce qui change concrètement
Alternatives envisagées : au moins une, même écartée rapidement
Impact : quels documents, quelles règles, quels composants sont touchés
Statut : PROPOSE | APPROUVE | REJETE | REPORTE
Décision et date :
```

## 27.2 Statuts et ce qu'ils impliquent

| Statut | Ce qu'il déclenche |
|---|---|
| **PROPOSE** | Aucun changement effectif. Discussion en cours. |
| **APPROUVE** | Le changement est intégré dans le document concerné, avec une entrée dans le journal des versions correspondant. |
| **REJETE** | Conservé dans l'historique des RFC, pour ne pas relancer indéfiniment la même discussion sans nouvelle information. |
| **REPORTE** | Cas déjà rencontré dans ce projet — l'extension régionale ou la recherche réglementaire pour d'autres pays (FHTP-KNO-001, "Décision de séquencement") sont des REPORTE de fait, pas des REJETE : la porte reste ouverte, juste pas maintenant. |

## 27.3 Ce que ce processus n'est pas, à ce stade

Pas de comité de validation, pas de délai formel de traitement — Dr Amadou reste le seul décideur, et le processus doit rester à sa mesure. Ce gabarit prend tout son sens le jour où une équipe se forme autour du projet et où plusieurs personnes peuvent proposer un changement en parallèle ; avant ça, il sert surtout à garder une trace uniforme, pas à ralentir la prise de décision.

## 27.4 Application rétroactive, à titre d'exemple

Pour montrer que le gabarit fonctionne sur ce qui existe déjà, plutôt que de rester théorique :

```
RFC-000 — Dégradation progressive de licence plutôt que coupure sèche
Date : 9 juillet 2026
Demandeur : Dr Amadou
Contexte : un accès expiré ne doit pas couper un centre du jour au lendemain,
           cohérent avec les délais de paiement AMU déjà documentés.
Changement proposé : quatre phases sur 60 jours (alerte, grâce, dégradée, suspendue)
                      plutôt qu'une suspension immédiate à l'échéance.
Alternatives envisagées : suspension immédiate — écartée, contraire à l'esprit
                           d'aide du projet.
Impact : Addendum 1, section 12.6 ; ADR-007.
Statut : APPROUVE
Décision et date : validé par Dr Amadou, 9 juillet 2026.
```

---

## Journal des versions

| Version | Date | Auteur | Changements |
|---|---|---|---|
| 0.1 | 9 juillet 2026 | Claude (sur demande de Dr Amadou) | Première formalisation du processus de changement (RFC) : gabarit, quatre statuts avec leur conséquence, portée volontairement légère tant que le projet reste à un seul décideur, et un exemple rétroactif construit à partir d'une décision déjà prise (ADR-007) pour valider que le gabarit fonctionne sur du réel. |
