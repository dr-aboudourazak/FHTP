# FHTP-KNO-001 — Knowledge Book
## FITTER Health Trust Platform
**Version 0.20 — Décision de séquencement : backlog assumé pour 4 scénarios et recherche régionale**
**Dernière mise à jour :** 6 juillet 2026 (v0.13)
**Statut :** version de référence

**Changement de nom (6 juillet 2026) :** le projet, jusqu'ici EQUIMED Trust Platform (ETP), s'appelle désormais **FITTER Health Trust Platform (FHTP)**. Ce nom fait le lien avec AMADOU FITTER, le nouveau projet de Dr Amadou dont le pôle Healthcare Marketplace recoupe directement cette plateforme. Le sigle FHTP a été choisi plutôt que FTP pour éviter la collision avec File Transfer Protocol, un sigle informatique déjà universellement utilisé. Le slogan et tout le reste du contenu métier restent inchangés.

---

## Note sur cette version

Cette version remplace intégralement les versions 0.1 à 0.5. Elle retire tout contenu qui avait été généré par supposition (biographie inventée, cas de fraude fictifs, sigles et nomenclatures non vérifiés) et le remplace par des informations soit confirmées directement par Dr Amadou, soit tirées de documents sources qu'il a fournis.

**Règle permanente à partir de cette version :** toute entrée de ce document porte une source. Une information sans source ne rentre pas dans le Knowledge Book, elle reste une hypothèse à vérifier.

---

## 1. Vision

**FITTER Health Trust Platform (FHTP)**
**Signature : Building Trust in Healthcare**

FHTP vise à construire un cadre de confiance pour la validation des prestations de santé, couvrant les professionnels, les établissements, les actes, les dossiers médicaux et les remboursements. [Source : Dr Amadou]

FHTP est un projet personnel du Dr Amadou. Il n'est pas, à ce stade, un actif d'EQUIMED GROUP SARL. L'objectif est de garder cette flexibilité jusqu'à ce que le projet soit mature, moment où un contrat de commercialisation pourra être signé avec EQUIMED GROUP pour le Togo et un ensemble de pays à définir, tout en gardant la liberté de signer un contrat distinct avec une entité locale différente si un marché particulier l'exige. (Précision de Dr Amadou, 5 juillet 2026)

---

## 2. Historique des décisions

| Date | Décision | Statut |
|---|---|---|
| — | Nom du produit : FITTER Health Trust Platform (FHTP), signature "Building Trust in Healthcare" | Validée |
| — | Approche : documenter d'abord la réalité du terrain, concevoir ensuite, coder en dernier | Validée |
| — | Création du Knowledge Book comme mémoire du projet | Validée |
| — | Portée géographique : Togo uniquement pour le moment (pas le Sénégal, contrairement à une hypothèse initiale erronée) | Validée |
| — | Un seul scénario métier travaillé jusqu'au bout avant de passer au suivant, en commençant par la consultation en cabinet libéral | Validée |
| — | Toute entrée du Knowledge Book doit porter une source vérifiable | Validée |
| — | Architecture de confidentialité médicale (Privacy by Design, compartimentation, preuve cryptographique plutôt que stockage du contenu médical) | Validée en principe, détails techniques à approfondir |

---

## 3. Principes fondateurs

### 3.1 Principes méthodologiques
- Documentation d'abord, conception ensuite, code en dernier.
- Un seul pays, un seul scénario à la fois, jusqu'à validation complète.
- Toute référence réglementaire, tarifaire ou légale doit être vérifiée auprès de Dr Amadou ou d'un document source, jamais supposée.
- Calendrier réaliste, sans sprint imposé, au rythme de disponibilité de Dr Amadou.

### 3.2 Principes métier
- La confiance se construit à cinq niveaux : professionnels, établissements, actes, dossiers médicaux, remboursements.
- Le système doit refléter la coexistence de deux logiques tarifaires distinctes au Togo (voir section 6) : celle de l'INAM pour le secteur public, celle du CAT pour les assureurs privés.
- La qualification du prescripteur doit être cohérente avec la nature de l'acte facturé.

### 3.3 Principe de confidentialité médicale (Privacy by Design)
Validé en principe par Dr Amadou, avec ces éléments :
- FHTP ne stocke jamais le contenu médical (rapports, diagnostics détaillés). Il vérifie l'intégrité des documents par hash et signature, sans en connaître le contenu.
- Le contenu médical original reste dans le système d'information de l'établissement.
- Lors des contrôles, l'accès au document médical original passe par l'établissement, pas par FHTP. FHTP conserve la trace de la demande de contrôle et de sa réponse, avec délai.
- Un septième principe reste à ajouter par rapport aux versions précédentes : la portabilité, pour qu'un patient changeant d'assureur ou d'établissement récupère son historique sans blocage.
- Le consentement patient est envisagé en deux temps : un consentement large signé une fois lors de l'affiliation, et une notification simple à chaque acte. Ce point reste à approfondir avec Dr Amadou.

---

### 3.4 Principe d'architecture : FHTP Core indépendant du payeur

*Validé par Dr Amadou le 5 juillet 2026, à partir d'une intuition confirmée par la lecture des documents INAM.*

FHTP ne doit jamais dépendre structurellement d'un organisme payeur particulier. L'INAM, la CNSS, un assureur privé (CAT ou autre) sont des **connecteurs** (adaptateurs), pas le cœur du système. Le cœur d'FHTP (FHTP Core) ne raisonne qu'en termes génériques : vérifier l'éligibilité d'un bénéficiaire, obtenir la base de remboursement d'un acte ou d'un médicament, soumettre une facture. Chaque payeur fournit une implémentation de ces interfaces génériques, propre à ses règles (codes R/E/TPC et Presta+ pour l'INAM/CNSS, lettre-clé/coefficient pour le CAT).

Conséquences concrètes :
- Les trois niveaux d'intégration déjà identifiés pour l'INAM (import des référentiels Excel, vérification via la plateforme en ligne, API future) ne sont pas trois solutions concurrentes : ce sont trois implémentations possibles d'un même connecteur INAM, interchangeables sans modifier FHTP Core.
- Ce principe ne remet rien en cause de ce qui est déjà validé (AMU/CAT, six piliers de confiance, règles métier du PRD-001) : ces éléments restent la logique métier d'FHTP Core. Ce qui change, c'est où vit la connaissance propre à chaque payeur, isolée derrière un connecteur plutôt que mélangée à la logique métier générale.
- Ce principe ouvre naturellement la voie à d'autres pays : un futur "connecteur Ghana" ou "connecteur Côte d'Ivoire" s'ajouterait sans toucher au cœur du système.
- Ce principe sera formalisé en détail dans FHTP-ARC-001, une fois les PRD des trois scénarios (consultation, hospitalisation, pharmacie) validés, conformément à la séquence déjà convenue.

**Pays candidats à la portabilité (identifiés par Dr Amadou, 5 juillet 2026) :** Niger et Burkina Faso. Aucun détail sur leurs régimes d'assurance maladie n'est encore vérifié ; ce sont des candidats à documenter via recherche dédiée avant toute conception de connecteur spécifique, pas des hypothèses à construire de mémoire.

### 3.5 Extension du principe : FHTP s'intègre au terrain, il ne le remplace pas

*Validé par Dr Amadou le 6 juillet 2026.*

Le principe d'indépendance vis-à-vis du payeur (section 3.4) a un miroir côté terrain : FHTP ne doit dépendre d'aucun logiciel de centre en particulier, et surtout, **FHTP vient s'intégrer aux logiciels déjà utilisés par les prestataires (vente et gestion de stock en pharmacie, SIH en centre de soins), il ne cherche pas à les remplacer.**

Raisons retenues :
- Le cœur de valeur de FHTP est la validation et la confiance dans le dossier de facturation, pas la gestion opérationnelle du stock ou de la caisse. Ce sont deux métiers distincts.
- Le terrain a déjà en partie résolu ce problème : les logiciels de pharmacie utilisent une base de données locale reprenant le contenu de Presta+ (nuance importante ci-dessous). Une posture de remplacement mettrait FHTP en concurrence inutile avec des éditeurs déjà en place.
- Remplacer un système de gestion de stock ferait porter à FHTP une responsabilité opérationnelle bien plus lourde (continuité des soins) que son rôle de couche de validation.
- Ce choix prolonge directement le principe de connecteurs déjà retenu pour les payeurs (section 3.4) : un connecteur par système de centre existant, plutôt qu'un système concurrent.

**Nuance retenue pour les centres sans logiciel :** certains cabinets facturent encore sur Excel ou à la main (KB section 6, confirmé pour la consultation). Pour ceux-là, FHTP peut proposer un module de saisie minimale, limité à ce qu'il faut pour produire un dossier de facturation valide, sans devenir un véritable logiciel de gestion de stock ou de caisse. Ce n'est pas remplacer un système existant, puisqu'il n'y en a pas, mais combler un vide réel sans sortir du rôle de FHTP.

**Conséquence d'architecture :** FHTP se pense en trois blocs plutôt que deux — connecteurs payeurs d'un côté (section 3.4), FHTP Core au centre, et côté terrain soit un connecteur vers un logiciel de centre existant (pharmacie, SIH), soit un module de saisie minimale quand rien n'existe. Ce principe sera détaillé dans FHTP-ARC-001, comme celui des connecteurs payeurs.

### 3.6 Anticipation régionale : deux logiques tarifaires, pas une seule

*Confirmé par Dr Amadou le 6 juillet 2026, à partir de sa propre lecture des systèmes de la sous-région.*

Il existe une dichotomie réelle en Afrique de l'Ouest : les pays francophones (Togo, Sénégal, Burkina Faso) ont adapté le système français à l'acte (nomenclature, lettre-clé/coefficient), tandis que les pays anglophones (Ghana notamment) utilisent des forfaits liés au diagnostic, sans lettre-clé (logique proche du DRG). Cette observation confirme, sur la base de l'expérience directe de Dr Amadou, ce qui n'était jusqu'ici qu'une piste de lecture non vérifiée dans FHTP-REF-001 (Partie 7.3).

**Anticipation retenue :** rien ne garantit que les pays francophones garderont indéfiniment la logique à l'acte. Dr Amadou anticipe qu'un basculement vers une logique de forfait lié au diagnostic pourrait aussi survenir en zone francophone. **Conséquence d'architecture :** l'interface générique du connecteur payeur (`obtenir_base_remboursement`, section 3.4) doit pouvoir fonctionner selon deux modes dès sa conception, pas seulement le mode à l'acte :
- **Mode à l'acte** (nomenclature, lettre-clé/coefficient) : le tarif se calcule acte par acte, comme au Togo aujourd'hui.
- **Mode forfait au diagnostic** (type DRG) : le tarif se calcule une fois par séjour ou par épisode, à partir du diagnostic CIM-10, indépendamment du nombre d'actes réalisés.

Un connecteur payeur déclare le mode qu'il utilise ; FHTP Core adapte son évaluation du pilier "cohérence tarifaire" en conséquence, sans qu'aucune logique propre à un mode ne s'infiltre dans le Core.

**Piste technique retenue pour FHTP-ARC-001 : la ressource FHIR Claim (standard HL7 international réel) comme couche d'abstraction possible.** Elle peut porter à la fois des lignes d'actes façon NGAP (`item.sequence`) et un diagnostic CIM-10 rattaché, ce qui recoupe naturellement le besoin des deux modes ci-dessus (MODE_ACTE / MODE_FORFAIT_DIAGNOSTIC déjà posés dans FHTP-ARC-001). **Cette piste est retenue uniquement pour la solidité du standard lui-même** ; elle n'est appuyée par aucune preuve empirique de déploiement réussi en Afrique de l'Ouest, contrairement à ce qu'affirmait un document soumis le 6 juillet 2026 (pilote "OpenHIE Sénégal" et "WAHO InterOp" avec un chiffre de réduction de rejets de 31%) : ces deux affirmations n'ont pu être vérifiées et un des liens fournis dans ce même document pointait en réalité vers un rapport sur le Togo alors qu'il était cité comme portant sur le Burkina Faso. FHIR Claim est donc gardé comme référence de conception, pas comme cas d'usage prouvé.

## 4. Connaissances métier

### 4.1 Parcours professionnel de Dr Amadou (source des connaissances terrain)

*Toutes les informations ci-dessous sont confirmées par Dr Amadou.*

- Médecin, Medical Science Liaison (MSL), chercheur, consultant en healthcare marketplace, biostatisticien.
- Senior Physician au Ministère de la Santé du Togo, en poste à l'Hôpital Régional de Dapaong.
- Enseigne la méthodologie de recherche à l'IGEB Lomé et à l'École Nationale des Auxiliaires Médicaux (ENAM) de Dapaong.
- Co-fondateur d'EQUIMED GROUP SARL, depuis 2018.
- Directeur exécutif de l'Hôpital Braun Cinkassé, de 2021 à 2023.
- Médecin-conseil chez Gras Savoye Togo (Willis Towers Watson), de 2017 à 2021. C'est de cette période que proviennent la plupart des schémas de fraude identifiés à ce stade.
- A exercé dans des cliniques à Lomé et chez Al Fikrah Management Consulting à Abu Dhabi (Émirats Arabes Unis).
- Impliqué dans la recherche clinique, avec plusieurs études et travaux de thèse à l'Université de Lomé.
- Auteur du livre *Social integration through education, school or family?*

### 4.2 Schémas de fraude confirmés

*Chaque schéma ci-dessous est confirmé par Dr Amadou et rattaché à un mécanisme de vérification identifié dans les conventions INAM et CAT.*

**1. Surfacturation par gonflement du prix**
Un acte ou un médicament est facturé au-dessus du tarif conventionné.
Vérification : le prix base de remboursement INAM est fixé par arrêté ministériel et ne peut être ni majoré ni minoré par la formation sanitaire (Convention INAM-Médecins, art. 29 ; Convention INAM-Pharmaciens, art. 22). Côté CAT, la nomenclature à lettre-clé et coefficient (article 6) sert de référence de calcul.
Règle FHTP envisagée : rapprochement automatique entre le montant facturé et le tarif de référence en vigueur à la date de l'acte, avec alerte sur tout écart.

**2. Facturation d'actes ou de médicaments non réalisés ou non délivrés**
Vérification : le rapport médical d'hospitalisation (Convention INAM-Médecins, art. 19) et le rapport de visite du praticien-conseil (art. 37-38) servent de pièces de recoupement.
Règle FHTP envisagée : réduction du score de confiance quand un acte facturé n'a pas de contrepartie documentée.

**3. Acte réalisé par une personne non qualifiée pour ce niveau de soin**
Vérification : seuls les actes effectués personnellement par un médecin, un chirurgien-dentiste, ou un auxiliaire avec prescription écrite qualifiée sont remboursables (Convention CAT, art. 11 ; Convention INAM-Médecins, art. 12-13).
Règle FHTP envisagée : croisement du code du prescripteur avec la nature de l'acte facturé.

**4. Discordance entre la signature de la fiche tiers-payant et le prescripteur réel**
Une personne signe et cachette la fiche tiers-payant à la place du prescripteur réel. Le signal est une variation d'écriture manuscrite sous une signature identique.
Vérification actuelle : aucun mécanisme administratif direct dans les conventions consultées ne couvre ce cas précisément ; c'est une observation de terrain de Dr Amadou.
Règle FHTP envisagée : ce cas nécessite une capacité de vérification graphométrique qui n'est pas encore spécifiée. Il est placé au backlog (section 7) plutôt que dans les règles immédiates.

**5. Utilisation abusive des majorations (nuit, dimanche, jour férié, spécialité)**
Confirmé par la Convention CAT (art. 15.1), qui cite explicitement l'"application fantaisiste de la nomenclature" et l'"utilisation abusive des majorations de nuit, de dimanche et de spécialité" comme manquements graves sanctionnables.
Point important : ces majorations existent côté assurance privée (CAT) mais pas côté AMU (INAM/CNSS), qui ne les prend pas en compte. Toute règle de validation doit distinguer le régime du patient avant d'appliquer ou non une majoration.

**6. Facture entièrement fabriquée de toutes pièces**
Confirmé par Dr Amadou : au-delà de la surfacturation ou de la facturation d'actes non réalisés, certains dossiers sont de purs faux, sans aucun acte réel sous-jacent.
Vérification : ce cas rejoint les motifs de rejet réels que Dr Amadou a listés (voir 6.4) et les contrôles déjà pratiqués par les assureurs : convocation du patient, visite du centre pendant l'hospitalisation pour vérifier l'effectivité des actes.

**7. Facturation de consultations de suivi répétées**
Facturation d'un nouveau frais de consultation pour un même motif, dans un délai où la règle l'interdit.
Source : règle RP 24-11, confirmée par Dr Amadou comme provenant de documents officiels INAM (FHTP-REF-001, Partie 4.2) : délai de 30 jours en secteur public, 15 jours en secteur privé.
*Ce schéma est une conséquence directe d'une règle officielle confirmée, pas un cas vécu rapporté un par un par Dr Amadou.*

**8. Facturation erronée de la journée de sortie d'hospitalisation**
Facturation de la journée de sortie comme une nuitée complète, alors que le calcul doit exclure cette journée.
Source : Convention INAM-Médecins, article 31.

**9. Délivrance et facturation d'ordonnances expirées**
Délivrance en pharmacie d'une ordonnance datée de plus de 7 jours, sans renouvellement médical.
Source : règle RP 24-37, confirmée par Dr Amadou.

**10. Facturation de médicaments oraux en clinique privée sous régime AMU**
Facturation de médicaments par voie orale en clinique privée alors que seuls les médicaments injectables (parentéraux) y sont remboursables par l'AMU.
Source : règle RP 24-33, confirmée par Dr Amadou.

### 6.4 Motifs de rejet réels (confirmés par Dr Amadou)

- Centre sans autorisation d'exploitation délivrée par le Ministère de la Santé.
- Absence de cachet ou de signature (du prestataire et/ou du patient/accompagnant).
- Absence de date.
- Absence de prise en charge ou d'entente préalable quand elle est requise.
- Facture transmise hors délai (au-delà du 5 du mois suivant).
- Absence du reçu de paiement de la part patient (sauf exemption pour double couverture).

Tout rejet doit être motivé par écrit, et ouvre un droit de recours pour le centre ou le patient. Le délai théorique de remboursement est de 30 jours, mais peut dépasser 3 mois en pratique, notamment à cause des rejets à régulariser.

**Ce que Dr Amadou identifie comme le vrai problème à résoudre : la crise de confiance.** Le manque de confiance entre prestataires et assureurs pousse une partie des prestataires à surfacturer ou frauder par anticipation, pour compenser des délais de remboursement longs et incertains. L'ambition d'FHTP est de réduire ces délais d'environ deux tiers en restaurant cette confiance, plutôt que de se positionner uniquement comme un outil de détection punitif.

---

## 5. Cas réels rencontrés

*Cette section ne contient que des cas confirmés explicitement par Dr Amadou, avec la source et la période. Aucun contenu généré par supposition.*

Sources validées pour cette section :
- Médecin-conseil, Gras Savoye Togo (Willis Towers Watson), 2017-2021
- Directeur exécutif, Hôpital Braun Cinkassé, 2021-2023
- Co-fondateur, EQUIMED GROUP SARL, depuis 2018

*(en attente des premiers cas détaillés)*

---

## 6. Cadre réglementaire togolais (basé sur documents sources et confirmations de Dr Amadou)

### 6.1 L'AMU (Assurance Maladie Universelle) — le régime obligatoire

*Source : explication détaillée de Dr Amadou, confirmée dès la première discussion du projet.*

L'AMU est un régime obligatoire imposé par l'État togolais. Elle se décline en deux branches, gérées par deux institutions distinctes mais partageant la même base de remboursement :
- **INAM** (Institut National d'Assurance Maladie) : gère l'AMU des fonctionnaires, des élèves, et d'une partie des retraités.
- **CNSS** (Caisse Nationale de Sécurité Sociale) : gère l'AMU des salariés du secteur privé. Toute entreprise privée est légalement tenue de cotiser pour ses employés.

Avant l'AMU, les entreprises privées passaient par les assurances privées classiques et les fonctionnaires par l'INAM. Depuis la réforme, toutes les entreprises privées sont enrôlées de force dans l'AMU-CNSS ; certaines conservent une assurance privée en complément.

Mécanismes communs aux deux branches de l'AMU :
- Un **code formation sanitaire** est attribué à chaque centre, et un **code prescripteur** à chaque agent de santé habilité (pas seulement les médecins : aussi les infirmiers, sages-femmes, assistants médicaux), après étude de dossier. Le code semble valide à vie, sans renouvellement identifié à ce jour.
- La base de remboursement des actes reprend les tarifs des centres publics, faute d'une nomenclature propre à l'AMU à ce stade.
- La base de remboursement des médicaments est publiée dans **Presta+**, l'application officielle de référence (disponible sur Play Store / App Store, version web : prestaplus.inam.tg). Seuls les médicaments enrôlés dans Presta+ sont remboursables par l'AMU, même s'ils disposent d'une AMM au Togo. Presta+ indique pour chaque médicament enrôlé : le prix public, la base de remboursement AMU, et la part patient.

**Observation de terrain (Dr Amadou, CHR Dapaong, 6 juillet 2026) :** ce qu'on appelait "intégration Presta+" dans les logiciels de caisse/vente est en réalité une **copie locale de la base de données**, pas une interaction automatique via API. Concrètement :
- Les caissiers disposant d'internet ouvrent une fenêtre séparée pour vérifier manuellement les identités et confirmer certains montants.
- Le gestionnaire du centre sollicite de temps en temps le développeur du logiciel de caisse pour une mise à jour de la base locale, afin qu'elle reflète le contenu réel de Presta+.
- Le CHR Dapaong est le centre de référence étatique de toute la région ; s'il existait un système plus avancé, ce centre serait normalement parmi les premiers à en disposer. Cette observation doit donc être traitée comme une base réaliste pour la majorité des centres, pas comme un cas particulier en retard.

**Incident réel observé par Dr Amadou au CHR Dapaong, illustrant un besoin concret pour FHTP :** un surveillant de caisse a réprimandé un caissier pour avoir délivré un médicament soumis à entente préalable sans vérifier l'existence de cette entente. L'INAM a refusé le remboursement en conséquence. Après vérification, il s'est avéré que la demande d'entente préalable avait bien été faite et accordée, mais le patient avait laissé le document chez lui et s'était présenté avec uniquement la prescription. **FHTP doit pouvoir résoudre ce type de situation** : permettre de vérifier le statut réel d'une entente préalable (par exemple par le numéro de prescription ou l'identifiant du patient) plutôt que de dépendre uniquement de la présentation physique du document par le patient.
- Le patient présente une carte physique (INAM ou CNSS) ou, à défaut, une attestation papier transitoire le temps que la carte soit délivrée.
- Le tiers payant est le mode de règlement dominant ; le paiement direct reste minoritaire mais existe.
- Un reçu de paiement de la part patient (ticket modérateur) est obligatoire pour la validité du dossier, sauf case d'exemption cochée en cas de double couverture (voir 6.3).

**Mise à jour digitalisation (vérifiée par recherche web, juillet 2026) :**
- L'INAM a engagé depuis 2025 une refonte complète de son système d'information, avec déploiement d'une nouvelle carte à puce AMU sécurisée, présentée comme conçue aux mêmes standards que celle de la CNSS et interopérable avec les autres organismes de protection sociale. (Source : Togo First, juin 2025)
- Le portail **e-conventionnement** (conventionnement.inam.tg, accessible aussi depuis www.inam.tg → "Services en ligne") permet aux prestataires (centres de soins, pharmacies, établissements de lunetterie) de faire leur demande de conventionnement en ligne. Une seule demande vaut pour les deux guichets AMU-INAM et AMU-CNSS. Toujours actif en janvier 2026 (communiqué sur les établissements de lunetterie).
- **Distinction importante :** ce portail concerne le conventionnement des *prestataires* (centres, pharmacies). L'*immatriculation des assurés* (délivrance de la carte au patient) n'est pas encore dématérialisée à ce jour ; elle reste au guichet physique de l'INAM.
- Aucune API publique documentée n'a été identifiée à ce stade pour interroger Presta+ ou vérifier les droits en temps réel depuis un logiciel tiers. Un retour reçu par Dr Amadou sur ce sujet contenait surtout des éléments spéculatifs (schémas techniques non confirmés) : la seule voie fiable reste le contact direct avec la Direction des Systèmes d'Information de l'INAM.

### 6.2 Conventions signées avec l'INAM (documents sources consultés)

- Convention INAM / Ordre National des Médecins du Togo (ONMT), février 2012
- Convention INAM / Ordre National des Pharmaciens du Togo, février 2012
- Convention INAM / Formations sanitaires publiques du Togo, février 2012
- Convention INAM / Ordre National des Chirurgiens-Dentistes du Togo (ONCDT), février 2012

Mécanismes propres à ces conventions :
- Les actes et médicaments y sont codés **R** (remboursable), **E** (entente préalable nécessaire), ou **TPC** (carte de traitement pour affection de longue durée / chronique).
- Le contrôle médical est assuré par des praticiens-conseils, avec possibilité de visites inopinées (Convention Médecins, art. 37-38).

*Point à clarifier : ces conventions de 2012 semblent antérieures à la réforme AMU/CNSS. Leur articulation exacte avec le système Presta+ actuel reste à confirmer avec Dr Amadou.*

### 6.3 Les assureurs privés (CAT) — complémentaires de l'AMU, jamais en premier

Convention entre le Comité des Assureurs du Togo (CAT), l'Ordre National des Médecins du Togo (ONMT) et l'Ordre National des Chirurgiens-Dentistes du Togo (ONCDT), édition révisée de septembre 2019.

**Point confirmé par Dr Amadou, essentiel pour la logique de calcul FHTP : l'AMU rembourse toujours en premier, l'assureur privé n'intervient qu'en complémentaire**, sur la base de ce que l'AMU n'a pas couvert. Il n'existe pas encore de formulaire de coordination formalisé entre les deux (projet en cours). Quand un patient a une double couverture AMU + privé, la fiche AMU prévoit une case à cocher qui l'exempte de présenter le reçu de paiement de sa part, puisque l'assureur complémentaire s'en charge selon son contrat.

Pour les médicaments, les assureurs privés utilisent directement le prix public officiel comme base de remboursement (contrairement à l'AMU, qui passe par Presta+ et retient souvent le médicament le plus ancien ou l'équivalent le moins cher).

**Exception de terrain confirmée par Dr Amadou :** la règle "AMU en premier" n'est pas universelle en pratique. Il persiste des entreprises qui n'ont que l'assurance privée (non enrôlées, ou n'ayant pas basculé vers l'AMU-CNSS). Et même quand une entreprise a les deux couvertures, il arrive que le patient utilise directement son assurance privée sans passer par l'AMU. FHTP doit donc traiter le choix du circuit de remboursement comme une donnée à vérifier au cas par cas, plutôt que comme une règle automatique déductible du seul statut de l'entreprise.

Mécanismes clés, différents de l'INAM :
- Tarification par lettre-clé et coefficient (système à la française) : C (consultation généraliste), CS (consultation spécialiste), CSPSY (psychiatre), K (chirurgie et spécialités), Z (radiologie), B (biologie), SC (soins conservateurs dentaires), DC (chirurgie dentaire), et autres.
- Article 15.1 : sanctions en cas de non-respect du tarif, d'application fantaisiste de la nomenclature, ou d'utilisation abusive des majorations de nuit, dimanche et spécialité. Peut aller jusqu'à la suspension des relations, voire la radiation par l'ordre professionnel.
- Article 11 : seuls les actes effectués personnellement par un médecin, un chirurgien-dentiste, ou un auxiliaire dûment habilité et prescrit sont remboursables.
- Une commission de suivi et d'arbitrage (article 14) tranche les litiges, composée de représentants du CAT, de l'ONMT et de l'ONCDT.
- Article 13 : mécanisme d'évacuation sanitaire, avec priorité aux centres de la sous-région avant l'Europe.

**Point de conception majeur pour FHTP :** les logiques tarifaires INAM et CAT sont structurellement différentes (codes R/E/TPC contre lettre-clé/coefficient). Un moteur de règles unique ne peut pas les traiter de façon identique ; il faut au minimum deux modules de calcul tarifaire distincts, sélectionnés selon le régime du patient.

**Correction importante confirmée par Dr Amadou (6 juillet 2026) : il n'existe pas de taux fixe unique côté AMU ni côté CAT.** Les bases Excel Presta+ que Dr Amadou a lui-même téléchargées montrent des taux qui varient acte par acte, hospitalisation par hospitalisation, médicament par médicament : il n'y a pas de "80% INAM / 20% patient" universel. Côté CAT, la variation est encore plus marquée : le barème change d'un contrat à l'autre. Certains contrats sont même en **"Frais Réel"** : la base de remboursement est directement ce que le prestataire facture, sans tarif de référence à comparer. Dans ce cas précis, la notion même de surfacturation ne s'applique pas.

**Conséquence directe pour le modèle de confiance (section 11) :** le pilier "cohérence tarifaire" ne peut pas appliquer une seule logique de comparaison partout. FHTP doit d'abord identifier le type de contrat (taux fixe par acte, barème CAT spécifique, ou Frais Réel) avant de décider comment évaluer ce pilier. Pour un contrat Frais Réel, ce pilier se limite à vérifier la cohérence interne du dossier (actes déclarés cohérents avec le diagnostic, absence de doublons), sans comparaison à un tarif externe.

*Note : le mécanisme de contrôle CAT (Annexe n°6) a depuis été obtenu et intégré dans FHTP-REF-001 section 2.8.*

### 6.5 Réglementation AMU récente et chiffres officiels (ajout du 6 juillet 2026)

**Documents officiels fournis par Dr Amadou** (règles RP24, note R68, restrictions de prescription paramédicale, référentiels cliniques 2015, tarifs AMU Scolaire) : intégrés en détail dans FHTP-REF-001, Partie 4. Le recueil de 37 règles (RP 24-01 à RP 24-37) donne des seuils précis (24h, 3 jours, 7 jours, 15 jours, 30 jours) directement transposables en règles métier pour les trois PRD déjà rédigés.

**Décret n°2023-100/PR, obtenu et intégré le 7 juillet 2026 :** fixe les modalités du contrôle médical en AMU (INAM et CNSS). Texte intégral et comparaison avec le mécanisme CAT disponibles dans FHTP-REF-001, section 6.1. Points clés retenus pour FHTP : contrôle exercé par des médecins-conseils et pharmaciens-conseils soumis à une interdiction stricte de conflit d'intérêts ; contrôle portant explicitement sur le respect du parcours de soins coordonné ; sanction symétrique de suspension en cas de refus de contrôle (prestataire ou assuré) ; voie de recours formalisée devant le **comité de régulation de l'assurance maladie universelle**, avec contre-expertise indépendante et frais à la charge de la partie perdante.

**Chiffres officiels vérifiés, fin 2024 :** 509 902 assurés INAM au total depuis 2011, environ 174 000 assurés CNSS-AMU depuis janvier 2024, réseau de 270 pharmacies et 1 263 formations sanitaires conventionnées côté INAM. Taux de couverture assurance maladie estimé à environ 10% de la population togolaise en 2023.

**Pistes régionales Afrique de l'Ouest (soumises par Dr Amadou) :** synthèse de sources par pays (Sénégal, Burkina Faso, Côte d'Ivoire, Bénin, Mali, Niger, Guinée, Ghana, Nigeria, Liberia, cadre CEDEAO), intégrée dans FHTP-REF-001 Partie 7. Deux affirmations vérifiées et confirmées ; le reste à traiter comme pistes de recherche, pas comme faits acquis. Point conceptuel retenu : la distinction NGAP (tarification à l'acte, Togo/Sénégal/Burkina Faso) contre G-DRG (tarification au cas, Ghana) est cohérente avec l'architecture en connecteurs déjà validée (section 3.4), chaque connecteur pays traduisant sa propre logique vers le modèle générique de FHTP Core.

---

## 7. Idées en attente

| Idée | Statut |
|---|---|
| Module de vérification graphométrique (signatures sur fiches tiers-payant) | Identifié, non spécifié |
| Module de consentement patient (deux temps : affiliation + notification par acte) | À approfondir avec Dr Amadou |
| Double moteur tarifaire INAM / CAT | Nécessaire, à concevoir avec le PRD |
| Obtenir le décret n°2023-100/PR (contrôle médical AMU) | **Obtenu et intégré le 7 juillet 2026** (FHTP-REF-001 section 6.1) |
| Formaliser le circuit "comité de régulation AMU" dans les PRD (recours, contre-expertise) | Nouveau, identifié le 7 juillet 2026, à intégrer dans les trois PRD |
| Vérifier individuellement le tableau régional Afrique de l'Ouest (FHTP-REF-001 Partie 7) | Deux points vérifiés, le reste en attente |

---

## 8. Glossaire

| Terme | Définition |
|---|---|
| AMU | Assurance Maladie Universelle, régime obligatoire togolais, géré conjointement par l'INAM et la CNSS |
| INAM | Institut National d'Assurance Maladie du Togo — gère l'AMU des fonctionnaires, élèves, et une partie des retraités |
| CNSS | Caisse Nationale de Sécurité Sociale — gère l'AMU des salariés du secteur privé |
| Presta+ | Application officielle de référence pour la base de remboursement des médicaments AMU (web : prestaplus.inam.tg) |
| CAT | Comité des Assureurs du Togo — assurances privées, complémentaires de l'AMU |
| ONMT | Ordre National des Médecins du Togo |
| ONCDT | Ordre National des Chirurgiens-Dentistes du Togo |
| ONP | Ordre National des Pharmaciens du Togo |
| R / E / TPC | Codes des conventions INAM 2012 : Remboursable / Entente préalable / Traitement pour affection de longue durée-chronique |
| Lettre-clé / coefficient | Système de tarification CAT : chaque acte a une lettre (C, CS, K, Z, B...) et un coefficient qui, multipliés, donnent le tarif |
| Tiers payant | Mode de règlement où l'assureur (AMU ou privé) paie directement le prestataire, le patient ne réglant que sa part restante |
| Ticket modérateur | Part du montant restant à la charge du patient après remboursement AMU |
| Code formation sanitaire | Identifiant attribué par l'AMU à chaque centre de soins |
| Code prescripteur | Identifiant attribué par l'AMU à chaque agent de santé habilité (médecin, infirmier, sage-femme, assistant médical) |

---

## 9. Journal des versions

| Version | Changements |
|---|---|
| 0.1 à 0.5 | Versions initiales, contenant des informations biographiques et des cas de fraude fabriqués par supposition, ainsi que des sigles non vérifiés (CNAM au lieu d'INAM, nomenclatures inventées). Retirées. |
| 0.6 | Purge complète. Reconstruction sur la seule base des informations confirmées par Dr Amadou et des cinq conventions sources (INAM-Médecins, INAM-Pharmaciens, INAM-Formations publiques, INAM-Chirurgiens-Dentistes, CAT 2019). Ajout de la distinction structurelle INAM/CAT. |
| 0.7 | Correction majeure : restauration du modèle AMU (INAM + CNSS) omis par erreur en v0.6, ajout de Presta+, repositionnement du CAT comme complémentaire de l'AMU, ajout du 6e schéma de fraude (facture fabriquée), ajout des motifs de rejet réels, ajout du brouillon de Scénario 1 basé sur la description détaillée de Dr Amadou. |
| 0.8 | Clarification : l'AMU est un régime unique à deux guichets (INAM et CNSS), pas deux scénarios distincts. Ajout de l'exception "assurance privée utilisée seule ou en priorité". Validation du modèle de confiance à 6 piliers, rattachés chacun à un schéma de fraude confirmé. |
| 0.9 | Vérification par recherche web d'un retour reçu sur l'interopérabilité API INAM : la plupart des éléments techniques (schémas JSON, endpoints) se sont révélés spéculatifs, non confirmés par une source fiable. Ajout des éléments réellement vérifiés : refonte SI INAM 2025, carte à puce, portail e-conventionnement, distinction conventionnement prestataire / immatriculation assuré (celle-ci encore non dématérialisée). |
| 0.10 | Ajout du principe d'architecture "FHTP Core indépendant du payeur" (connecteurs INAM/CNSS/CAT/autres pays), proposé par Dr Amadou et validé. Ce principe guidera FHTP-ARC-001 sans remettre en cause le travail métier déjà validé. |
| 0.11 | Ajout de Niger et Burkina Faso comme pays candidats à la portabilité, sans détails inventés sur leurs régimes d'assurance maladie (à documenter par recherche dédiée si besoin). |
| 0.12 | Renommage du projet : EQUIMED Trust Platform (ETP) devient FITTER Health Trust Platform (FHTP), en lien avec le lancement d'AMADOU FITTER. Clarification du statut de propriété : projet personnel de Dr Amadou, pas un actif d'EQUIMED GROUP SARL à ce stade, en vue d'une flexibilité de commercialisation future par pays. |
| 0.13 | Ajout du principe "FHTP s'intègre au terrain, il ne le remplace pas" : connecteurs vers les logiciels existants (pharmacie, SIH) plutôt que remplacement, avec module de saisie minimale pour les centres sans logiciel. |
| 0.14 | Correction terrain (observation directe de Dr Amadou au CHR Dapaong) : "l'intégration Presta+" des logiciels de caisse est une copie locale mise à jour périodiquement, pas une API en temps réel. Ajout d'un incident réel (entente préalable accordée mais document laissé à la maison, rejet à tort) comme cas d'usage concret à résoudre par FHTP. |
| 0.15 | Ajout de la réglementation AMU récente (règles RP24, note R68, confirmées par Dr Amadou comme provenant de documents officiels INAM), de chiffres officiels vérifiés par recherche web (dont le décret 2023-100/PR sur le contrôle médical, découverte importante), et des pistes régionales Afrique de l'Ouest pour la portabilité (deux points vérifiés, le reste en attente). |
| 0.16 | Fusion avec un travail parallèle mené par Dr Amadou via Codex/Antigravity (architecture technique, intégration RP24 dans les PRD). Correction d'une incohérence tarifaire CAT et d'un taux fixe non sourcé détectés dans ce travail. Ajout de la nuance taux variable par acte et contrats "Frais Réel" CAT (où la notion de surfacturation ne s'applique pas), confirmée par Dr Amadou à partir de ses propres fichiers Presta+ et de son expérience CAT. Ajout de l'anticipation régionale NGAP (francophone) contre forfait au diagnostic type DRG (anglophone), avec conséquence directe sur l'interface générique du connecteur payeur. |
| 0.17 | Ajout de la piste technique FHIR Claim comme couche d'abstraction possible pour FHTP-ARC-001, retenue uniquement pour la solidité du standard HL7 lui-même. Un document soumis le même jour affirmait des preuves empiriques (pilotes "OpenHIE Sénégal" et "WAHO InterOp", réduction de 31% des rejets transfrontaliers) qui n'ont pu être vérifiées ; l'un des liens fournis pointait même vers un rapport sur le Togo cité comme portant sur le Burkina Faso. Ces affirmations non vérifiées ne sont pas retenues. |
| 0.18 | Localisation confirmée du décret n°2023-100/PR : adopté le 11 octobre 2023, cité en pratique dans deux décisions INAM/CNSS (article 10, alinéa 2), PDF officiel repéré sur cnss.tg mais non accessible par les outils actuels (domaine non autorisé, scan sans texte). En attente que Dr Amadou le télécharge et le transmette pour traitement OCR. |
| 0.19 | Décret n°2023-100/PR obtenu (OCR local de Dr Amadou) et intégré intégralement dans FHTP-REF-001 section 6.1. Ajout du comité de régulation AMU, de la voie de recours avec contre-expertise, de la sanction de suspension en cas de refus de contrôle, et de l'interdiction de conflit d'intérêts pour les contrôleurs. |
| 0.20 | Décision assumée de séquencement : les scénarios urgences, dentaire, téléconsultation et évacuation sanitaire restent en backlog volontaire plutôt que rédigés par anticipation. La recherche réglementaire pour d'autres pays d'Afrique de l'Ouest est également reportée jusqu'à opportunité concrète. Passage à FHTP-ARC-001 comme prochaine étape. |

---

## 10. Questions ouvertes

- Le mécanisme de contrôle annexé à la convention CAT est-il disponible ?
- Comment structurer précisément le consentement patient en deux temps ?
- Quel est le seuil ou processus pour la vérification graphométrique des signatures, si cette piste est retenue ?

---

## 11. Scénario 1 — Consultation en cabinet libéral (brouillon à valider)

*Ce brouillon reprend et met en forme la description détaillée que Dr Amadou a donnée dès la première discussion du projet. Il n'a pas encore été revalidé phrase par phrase dans cette conversation-ci : à confirmer avant de le figer dans un PRD séparé.*

### Cas nominal : patient couvert par l'AMU (INAM ou CNSS, logique identique)

**Précision importante de Dr Amadou : l'AMU est un régime unique, géré simultanément par deux institutions (INAM et CNSS).** Ce n'est pas un choix entre deux cas nominaux différents. Le parcours ci-dessous est le même que le patient présente une carte INAM ou une carte CNSS ; seule l'institution réceptrice de la facture change, pas la logique de remboursement, ni les tarifs, ni Presta+. Le Scénario 1 doit donc traiter l'AMU comme un seul circuit à deux guichets, pas comme deux scénarios distincts.

**Phase 1 — Accueil et vérification**
Le patient se présente avec sa carte AMU (INAM ou CNSS selon son statut : fonctionnaire/élève/retraité pour l'INAM, salarié du privé pour la CNSS). Le cabinet vérifie la carte, identifie l'institution réceptrice (INAM ou CNSS) et valide les droits. La logique de vérification est identique dans les deux cas.

**Phase 2 — Consultation médicale**
Le médecin reçoit le patient et réalise la consultation (examen clinique, prise de constantes, examens complémentaires éventuels au cabinet). Il rédige l'ordonnance sur la fiche tiers-payant AMU correspondant au guichet (INAM ou CNSS), qui comporte plusieurs feuillets couleur : bleu pour la consultation et les actes médicaux, vert pour le laboratoire et l'imagerie, jaune pour la pharmacie.

**Phase 3 — Facturation**
Le cabinet établit la facture (Excel, logiciel local, ou saisie directe) avec le code acte selon la nomenclature des tarifs des centres publics, le montant facturé égal au tarif de référence AMU, la part patient (ticket modérateur) et la part AMU. Le médecin appose signature manuscrite et cachet avec numéro d'Ordre.

**Phase 4 — Prescription médicamenteuse**
Pour chaque médicament prescrit, vérification dans Presta+ : si enrôlé, la base de remboursement AMU est connue ; sinon, le médicament est marqué non remboursable et le médecin est alerté.

**Phase 5 — Soumission du dossier**
Le dossier complet comprend : la facture, les fiches tiers-payant remplies (feuillets scannés), la copie de la carte AMU (INAM ou CNSS selon le guichet), le reçu de paiement de la part patient (obligatoire sauf exemption), et la prise en charge ou entente préalable si l'acte est programmé.

**Phase 6 — Décision**
Un rejet doit être motivé par écrit et ouvre un droit de recours. Les motifs réels de rejet et les délais sont détaillés en section 6.4.

### Scénarios alternatifs identifiés

- **Double couverture (AMU + assurance privée complémentaire) :** le patient présente les deux cartes. L'AMU rembourse en premier ; la case d'exemption de reçu est cochée puisque le complémentaire prend le relais selon son contrat.
- **Assurance privée utilisée seule, sans passer par l'AMU :** soit l'entreprise n'est pas enrôlée en AMU-CNSS, soit elle a les deux couvertures mais le patient choisit d'utiliser directement l'assurance privée. Dans ce cas, c'est la logique CAT (lettre-clé/coefficient, prix public direct pour les médicaments) qui s'applique intégralement, sans intervention de l'AMU.
- **Paiement direct :** ordonnance rédigée sur l'ordonnancier du cabinet (pas de fiche tiers-payant), paiement immédiat et intégral, reçu émis pour archivage. Si le patient veut être remboursé, c'est lui qui soumet la facture à son assureur.
- **Attestation papier transitoire :** le patient n'a pas encore sa carte physique. Le numéro d'attestation est saisi manuellement ; ce cas mérite une vigilance renforcée dans le contrôle du dossier.
- **Ordonnance transmise par WhatsApp (paiement direct) :** le patient envoie une photo d'ordonnance avant de se présenter ; le médecin valide ou modifie la prescription à distance ; le patient vient ensuite uniquement pour le paiement et la délivrance.

### Modèle de confiance par dossier (validé le 5 juillet 2026)

Plutôt qu'un score à pourcentages arbitraires, chaque dossier est évalué par six piliers, chacun rattaché à un schéma de fraude confirmé (section 6.3) :

| Pilier | Ce qu'il vérifie | Schéma de fraude rattaché |
|---|---|---|
| Cohérence tarifaire | Montant facturé conforme au tarif de référence (Presta+/tarifs publics pour l'AMU, lettre-clé/coefficient pour le CAT, selon le circuit) | 1 — Surfacturation |
| Cohérence documentaire | Présence d'une contrepartie (rapport médical, feuillet correspondant) pour chaque acte facturé | 2 — Actes non réalisés |
| Cohérence prescripteur/acte | Le code prescripteur correspond à une qualification compatible avec l'acte facturé | 3 — Acte hors qualification |
| Cohérence graphique | Signature et écriture cohérentes sur l'ensemble d'une même fiche | 4 — Discordance signature/prescripteur |
| Cohérence de régime | Majorations appliquées seulement si le circuit est privé (CAT), jamais en AMU pur | 5 — Majoration abusive |
| Complétude administrative | Cachet, signature, date, prise en charge, reçu patient : tous les motifs de rejet réels (section 6.4) | 6 — Facture fabriquée |

Chaque pilier remonte un statut (conforme / à vérifier / anomalie) plutôt qu'un pourcentage. C'est la combinaison des statuts qui détermine si le dossier est payé automatiquement, part en contrôle rapide, ou en contrôle approfondi. Le calibrage précis (seuils, combinaisons qui déclenchent quoi) reste à faire lors de la rédaction du PRD.

### Points encore à valider avec Dr Amadou

- Le calibrage précis des seuils et combinaisons de statuts du modèle de confiance ci-dessus.
- L'articulation exacte entre les conventions INAM de 2012 et le système Presta+ actuel.
- Le circuit de recours en cas de rejet : délai précis, autorité de recours.
- Le futur formulaire de coordination AMU/complémentaire, actuellement en projet côté togolais.

## Décision de séquencement (7 juillet 2026)

Les trois PRD couvrant consultation, hospitalisation et pharmacie sont validés et stabilisés (FHTP-PRD-001 v1.5, FHTP-PRD-002 v1.5, FHTP-PRD-003 v1.4), avec le socle réglementaire togolais désormais considéré comme suffisant (conventions INAM/CAT, règles RP24, décret n°2023-100/PR sur le contrôle médical).

**Quatre scénarios restent en backlog, volontairement, pas par oubli :** urgences, soins dentaires, téléconsultation, évacuation sanitaire. Décision assumée avec Dr Amadou : ne pas les rédiger maintenant, parce que ce sont pour l'essentiel des variations de mécanismes déjà couverts (l'urgence est déjà partiellement traitée dans FHTP-PRD-002, l'évacuation sanitaire a son tarif documenté dans FHTP-REF-001 section 2.10, le dentaire dispose déjà de sa nomenclature complète, la téléconsultation est surtout une variante de canal de la consultation), et parce qu'il vaut mieux les écrire une fois qu'un premier déploiement réel aura donné des retours de terrain, plutôt que par anticipation pure.

**De même, la recherche réglementaire approfondie pour d'autres pays d'Afrique de l'Ouest (Niger, Burkina Faso) n'est pas engagée maintenant.** L'architecture en connecteurs est conçue pour absorber un futur pays sans connaître son détail réglementaire à l'avance ; cette recherche sera faite le jour où un marché précis devient une opportunité concrète.

## Prochaine étape

Avancer sur FHTP-ARC-001 (architecture technique), déjà à sa version 0.3, en s'appuyant sur les trois PRD stabilisés.
