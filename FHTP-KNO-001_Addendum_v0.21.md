# FHTP-KNO-001 — Addendum v0.21
## Principe de stabilité et esprit du projet

**Date :** 9 juillet 2026
**À intégrer dans :** FHTP-KNO-001 v0.20, section 3 (Principes fondateurs), comme nouvelles sous-sections 3.7 et 3.8.

---

## 3.7 Principe de stabilité — "ce qui est déposé par terre ne peut plus tomber"

Confié par Dr Amadou, 9 juillet 2026, en référence à un enseignement de son père : une architecture se choisit pour sa solidité éprouvée, pas pour l'attrait du moment. Concrètement pour FHTP : préférer des technologies matures et largement éprouvées, limiter les dépendances fragiles, construire chaque composant pour qu'il tienne seul plutôt que sur un empilement de couches sophistiquées difficile à maintenir dans la durée.

Ce principe rejoint, sans avoir été nommé jusqu'ici, plusieurs choix déjà faits ailleurs dans le projet : l'ancrage externe gratuit et pérenne plutôt qu'une infrastructure dédiée coûteuse (FHTP-ARC-001, section 8.5) ; le jeton de licence vérifiable localement plutôt qu'une dépendance réseau permanente (ARC-001 Addendum 1, section 12.5) ; et surtout le principe déjà posé en section 3.1 — documenter d'abord, concevoir ensuite, coder en dernier — qui revient à ne rien construire avant d'avoir vérifié le sol.

**Conséquence technique, confirmée par Dr Amadou le 9 juillet 2026 : le langage de FHTP Core est Python.** Choix cohérent avec ce principe : écosystème mature, largement éprouvé, avec des bibliothèques stables pour tout ce dont FHTP Core a besoin (moteur de règles, API, traitement Excel/CSV, OCR). Le site web AMADOU FITTER (JS/CSS, édition via CMS) reste un projet distinct, sans lien technique avec FHTP Core — chaque projet garde l'outil qui lui correspond.

## 3.8 L'esprit du projet — sourate Al-Asr (103)

Partagé par Dr Amadou, 9 juillet 2026, comme ce qui doit guider le cœur de FHTP : par le temps, l'humanité court à la perte, sauf ceux qui croient, qui font le bien, qui s'enjoignent mutuellement la vérité, et qui s'enjoignent mutuellement la patience.

Ce document ne cherche pas à interpréter le texte : seulement à noter que ces quatre exigences se retrouvent déjà, sans avoir été nommées ainsi, dans les choix faits pour FHTP :

- **La sincérité d'intention** rejoint la vision déjà posée section 1 : construire la confiance, pas punir.
- **Faire le bien** rejoint l'objectif concret déjà énoncé section 6.4 : réduire les délais de remboursement et la crise de confiance entre prestataires et payeurs, pas seulement détecter la fraude.
- **Dire et encourager la vérité** rejoint la règle en vigueur depuis la v0.6 de ce document : aucune entrée sans source vérifiable — et la même exigence appliquée à la conception technique, par exemple l'honnêteté sur les limites réelles de l'OCR (ARC-001 Addendum 1, section 14.8) plutôt qu'une fiabilité promise qui n'existe pas encore.
- **S'enjoindre mutuellement la patience** rejoint le rythme déjà choisi : un scénario à la fois jusqu'à validation complète (section 3.1), une dégradation progressive de licence plutôt qu'une coupure sèche (ARC-001 Addendum 1, section 12.6), et le choix de calibrer sur un échantillon réel avant d'investir plutôt que de se précipiter.

Rien de tout cela n'est ajouté de toutes pièces : c'est déjà la manière dont ce projet a été conduit depuis le début. Ce principe ne fait que la nommer.

---

## Journal des versions (entrée à ajouter à la section existante)

| Version | Date | Auteur | Changements |
|---|---|---|---|
| 0.21 | 9 juillet 2026 | Claude (à partir du partage de Dr Amadou) | Ajout du principe de stabilité ("ce qui est déposé par terre ne peut plus tomber"), avec confirmation que Python est le langage retenu pour FHTP Core. Ajout de l'esprit du projet inspiré de la sourate Al-Asr (103), relié aux pratiques déjà en place plutôt que présenté comme un ajout séparé. |
