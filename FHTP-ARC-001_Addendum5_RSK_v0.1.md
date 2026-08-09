# FHTP-ARC-001 — Addendum 5, v0.1
## Registre des risques (RSK) — au-delà de la sécurité technique

**Date :** 9 juillet 2026
**Statut :** brouillon pour validation par Dr Amadou
**À intégrer dans :** FHTP-ARC-001 v0.5, nouvelle section 24 (ou FHTP-KNO-001, à trancher avec Dr Amadou selon que le registre reste technique ou devient un document de pilotage à part).

---

## Note de méthode

La table de failles F1-F9 (section 8.2 et Addendum 4) couvre le risque de sécurité technique. Ce document couvre ce qui reste : le risque métier et le risque projet, qui touchent directement la viabilité de FHTP, pas seulement son intégrité technique.

## 24.1 Registre

| # | Risque | Impact si non traité | Mitigation retenue |
|---|---|---|---|
| R1 | **Dépendance à un seul payeur dominant.** L'essentiel du volume togolais passe par l'AMU (INAM/CNSS). Un changement réglementaire unilatéral (nouvelle nomenclature, rupture de l'accès Presta+) affecterait FHTP en bloc. | Interruption de service pour la majorité des centres. | Déjà atténué par le principe de connecteurs interchangeables (FHTP-KNO-001 section 3.4) — le risque technique est traité, le risque contractuel (accès maintenu par l'INAM) reste hors du contrôle de FHTP et doit être suivi comme un risque, pas seulement une hypothèse d'architecture. |
| R2 | **Changement réglementaire non anticipé.** Les règles RP24 ou une nouvelle convention CAT peuvent changer sans préavis long. | Règles obsolètes appliquées, rejets injustifiés en masse. | Le cycle de mise à jour des règles (Addendum 2, section 18.3) et le mécanisme de rollback (Addendum 3, section 21.4) réduisent le délai de correction, mais ne préviennent pas le changement lui-même — veille réglementaire à formaliser comme activité récurrente, pas ponctuelle. |
| R3 | **Résistance à l'adoption terrain.** Un centre habitué à surfacturer par anticipation (FHTP-KNO-001, "crise de confiance") pourrait percevoir FHTP comme un outil de contrôle plutôt que d'aide. | Adoption lente, contournement du système. | Directement la raison d'être du positionnement déjà choisi : FHTP comme outil de confiance et de paiement plus rapide, pas comme police de la facturation — à rappeler dans toute communication commerciale. |
| R4 | **Non-paiement ou résiliation en série.** Si le modèle de licence (Addendum 1, section 12) est perçu comme trop rigide malgré la dégradation progressive, plusieurs centres pourraient ne pas renouveler simultanément. | Perte de revenu concentrée, mauvais signal pour la suite de la commercialisation. | Suivi humain des échéances déjà prévu (Addendum 2, section 18.4) — à instrumenter avec un tableau de bord agrégé, pas seulement centre par centre, pour détecter un décrochage groupé tôt. |
| R5 | **Dépendance à une seule personne (Dr Amadou) pour la validation des règles et la relation terrain.** Le projet repose aujourd'hui sur une expertise et un réseau personnels. | Point de défaillance unique si indisponibilité prolongée. | Aucune mitigation technique possible ; c'est un risque organisationnel à traiter le jour où l'équipe grandit — à noter comme tel plutôt que d'y répondre par une fausse solution logicielle. |
| R6 | **OCR moins performant qu'espéré** (déjà anticipé Addendum 1, section 14.8) — repris ici car c'est un risque projet, pas seulement une limite technique : un centre qui compte sur la reconnaissance automatique pourrait être déçu si le calibrage révèle un taux de reconnaissance faible. | Attentes commerciales déçues, retard perçu sur une fonctionnalité annoncée. | Communication déjà prudente retenue en 14.8 (saisie assistée, jamais promesse d'automatisation complète) — à maintenir strictement dans tout discours commercial, ne jamais sur-vendre cette fonctionnalité avant calibrage réel. |
| R7 | **Extension régionale prématurée.** La tentation d'anticiper un connecteur Ghana, Niger ou Burkina Faso avant qu'un marché concret ne se présente (déjà déconseillé, FHTP-KNO-001 section "Décision de séquencement"). | Effort de conception dépensé sur une hypothèse plutôt que sur le marché réel. | Déjà tranché par Dr Amadou : recherche réglementaire régionale reportée jusqu'à opportunité concrète — ce risque est donc déjà maîtrisé par une décision prise, pas seulement identifié. |

## 24.2 Ce qui reste à faire

Ce registre est un point de départ, pas un inventaire exhaustif figé — il doit être revu à chaque jalon important (premier centre pilote, première extension régionale envisagée), pas rédigé une fois pour toutes.

---

## Journal des versions

| Version | Date | Auteur | Changements |
|---|---|---|---|
| 0.1 | 9 juillet 2026 | Claude (sur demande de Dr Amadou) | Première rédaction du registre des risques métier et projet (sept risques : dépendance payeur, changement réglementaire, résistance à l'adoption, résiliation en série, dépendance à une seule personne, déception sur l'OCR, extension régionale prématurée), en complément de la table de failles de sécurité déjà existante (F1-F9). |
