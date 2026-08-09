# FHTP-ARC-001 — Addendum v0.10
## API FHTP Core, internationalisation, soumission groupée, vérification de PEC hors connexion

**Date :** 9 juillet 2026
**Statut :** brouillon pour validation par Dr Amadou
**À intégrer dans :** FHTP-ARC-001 v0.5, comme nouvelles sections 12, 13, 14 et 15, plus l'annexe récapitulative des entités (le Journal des versions actuel, section 12, devient section 16 ; les entrées v0.6 à v0.10 y sont ajoutées en fin de document).
**Documents de référence :** FHTP-ARC-001 v0.5, FHTP-KNO-001 v0.20, FHTP-REF-001 v1.3

---

## Note de méthode

Ce document ajoute trois éléments demandés par Dr Amadou le 7 juillet 2026 : l'exposition d'une API propre à FHTP Core (distincte des connecteurs déjà décrits), le support du multilinguisme, et la prise en charge d'un mode de soumission groupée pour les centres qui facturent avec leur propre logiciel et ne transmettent leurs dossiers qu'en fin de mois. Ce dernier point part d'une observation de terrain confirmée par Dr Amadou : la plupart des centres compilent leurs factures juste avant l'échéance réglementaire (le 5 du mois suivant, R-TG-002), plutôt que de soumettre dossier par dossier au fil de l'eau. FHTP doit traiter ce mode de fonctionnement comme normal, pas comme un cas dégradé.

Aucune de ces trois sections ne modifie la logique du moteur de règles à six piliers ni les règles métier des trois PRD. Elles ajoutent des points d'entrée et une couche de présentation autour d'un cœur qui reste inchangé.

---

## 12. API FHTP Core — exposition directe

### 12.1 Ce que cette section couvre, et ce qu'elle ne couvre pas

La section 3 de FHTP-ARC-001 décrit des connecteurs : la façon dont FHTP Core parle aux payeurs (INAM, CNSS, CAT) et au terrain (SIH, officine). Ce sont des interfaces que FHTP initie ou consomme selon un rôle défini à l'avance.

Cette section décrit l'inverse : comment un système externe — logiciel de facturation d'un cabinet, tableur, portail web du module de saisie minimale — appelle FHTP Core directement pour lui demander une validation. Ce n'est pas un connecteur au sens de la section 3 : c'est la porte d'entrée générale de FHTP Core, celle que tout le monde utilise, y compris un centre qui n'a jamais entendu parler d'un SIH.

### 12.2 Deux modes de consommation

| Mode | Utilisé par | Caractéristique |
|---|---|---|
| **Connecteur Terrain intégré** (section 3.2/5, déjà validé) | SIH, logiciel d'officine, embarqué dans le poste de travail existant | Temps réel, dossier par dossier, transparent pour l'utilisateur final |
| **API Directe FHTP Core** (nouvelle, cette section) | N'importe quel logiciel de facturation, y compris un tableur exporté | Un dossier à la fois, ou un lot entier (section 14) ; le centre décide du rythme |

Le deuxième mode existe précisément parce que tous les centres n'ont pas de SIH, et que ceux qui en ont un n'utilisent pas forcément l'intégration en temps réel — cf. section 14.

### 12.3 Points d'entrée principaux (illustratif, à figer avec Dr Amadou)

```
POST   /api/v1/dossiers            Soumettre un dossier unique. Réponse synchrone.
GET    /api/v1/dossiers/{id}       Consulter le statut d'un dossier.
POST   /api/v1/lots                Soumettre un lot de dossiers. Réponse asynchrone (voir section 14).
GET    /api/v1/lots/{id}           Statut global d'un lot.
GET    /api/v1/lots/{id}/rapport   Rapport détaillé du lot, une entrée par dossier.
GET    /api/v1/referentiels/{type} Lecture seule des référentiels (tarifs, médicaments, actes).
```

**Réponse d'un dossier unique (`POST /api/v1/dossiers`) :**

```json
{
  "dossier_id": "DOS-2026-004521",
  "decision_finale": "CONTROLE_RAPIDE",
  "piliers": {
    "completude_administrative": "CONFORME",
    "coherence_regime": "CONFORME",
    "coherence_tarifaire": "A_VERIFIER",
    "coherence_documentaire": "CONFORME",
    "coherence_prescripteur": "CONFORME",
    "coherence_graphique": "NON_EVALUE"
  },
  "motifs": ["R-TG-005: montant facturé supérieur à la base Presta+"],
  "alerte_recours": null,
  "locale": "fr"
}
```

Le format de sortie est identique quel que soit le mode d'entrée : dossier saisi à la main via le portail, importé depuis un fichier Excel, ou soumis par API JSON depuis un SIH tiers. Le moteur de règles ne voit jamais le format d'origine — seulement le modèle de données consolidé déjà défini en section 6. C'est la même logique que celle déjà retenue pour les connecteurs payeurs : un contrat générique, plusieurs implémentations d'entrée.

### 12.4 Authentification et portée d'accès

Chaque centre dispose d'un jeton propre (OAuth2 client credentials, cf. section 8.3), scope limité à ses propres dossiers, conformément au principe déjà retenu en F5 et F4 (section 8.2). Un centre ne peut jamais interroger ou soumettre au nom d'un autre, même par erreur d'intégration côté client.

---

## 13. Internationalisation et multilinguisme

### 13.1 Ce qui reste inchangé

Le moteur de règles raisonne déjà en codes, pas en texte : conditions, identifiants de règles, statuts de pilier sont des valeurs machine (`R-TG-017`, `ANOMALIE`, `CIM-10`). Cette partie-là n'a besoin d'aucune adaptation pour être multilingue — c'est un acquis de l'architecture actuelle, pas un chantier.

Ce qui doit changer, c'est uniquement la couche de texte destinée à un humain : le message d'un rejet, le libellé d'un acte, le nom d'un statut affiché à l'écran.

### 13.2 Référentiel de libellés (nouvelle entité)

Aujourd'hui, une règle porte directement son message en français dans le champ `message` (voir l'exemple de la section 2.1 de FHTP-ARC-001). Ce champ doit être remplacé par une référence à un identifiant de message, résolu au moment de la réponse selon la langue demandée.

```json
{
  "id": "R-TG-017",
  "condition": "dossier.diagnostic_cim10 == 'R68'",
  "action_si_vrai": "REJET",
  "message_id": "MSG-R-TG-017-REJET"
}
```

```
Referentiel_Libelle
  id_libelle          (ex: MSG-R-TG-017-REJET)
  locale               [fr | en]
  texte
  version
```

```
MSG-R-TG-017-REJET | fr | "Code R68 proscrit par l'INAM. Dossier rejeté d'office."
MSG-R-TG-017-REJET | en | "Code R68 is prohibited by INAM. File automatically rejected."
```

Même logique de versionnage que le Référentiel de Règles (section 2.5) : un changement de formulation se fait par nouvelle version du libellé, pas par écrasement, pour garder une trace de ce qui a été affiché à quelle date.

Les libellés des référentiels médicaments et actes (nomenclature Presta+, lettre-clé CAT) suivent le même principe : le code reste international et non traduit, seul son intitulé affiché change de langue.

### 13.3 Résolution de la langue

Ordre de priorité :
1. Paramètre explicite de la requête API (`Accept-Language` ou équivalent).
2. Langue par défaut du connecteur payeur concerné — un connecteur Togo (INAM/CNSS/CAT) répond en français par défaut ; un futur connecteur Ghana répondrait en anglais par défaut, sans qu'aucune règle métier n'ait besoin d'être dupliquée pour autant.
3. Français, à défaut de tout le reste — langue de référence actuelle du projet.

### 13.4 Portée retenue

Français et anglais restent la base : le français pour le Togo, l'anglais pour le futur connecteur Ghana et pour les lecteurs de rapports côté bailleurs internationaux.

**Ajout du 9 juillet 2026, sur demande de Dr Amadou :** deux langues supplémentaires à anticiper pour la portabilité régionale, plus une troisième pour un cas d'usage différent.

- **Portugais** — pertinent pour une extension vers la Guinée-Bissau ou le Cap-Vert, dans la même logique de portabilité déjà retenue pour le Niger et le Burkina Faso (FHTP-KNO-001 section 3.4).
- **Espagnol** — pertinent pour la Guinée équatoriale, seul pays hispanophone de la sous-région.
- **Arabe** — cas d'usage distinct des deux précédents : il ne s'agit pas d'un pays candidat à un futur connecteur payeur, mais d'un besoin déjà présent au Togo. Confirmé par Dr Amadou : certaines ONG islamiques gérant des orphelinats et des structures de soins associées échangent avec leurs partenaires internationaux en arabe. Ces structures peuvent très bien soumettre leurs dossiers à l'INAM ou la CNSS en français (le circuit payeur ne change pas), tout en ayant besoin que leurs propres rapports de suivi soient lisibles en arabe par leurs partenaires.

**Conséquence de conception pour ce dernier point :** la langue d'un rapport ne peut plus dépendre uniquement du connecteur payeur par défaut (section 13.3, priorité 2). Il faut un attribut de langue préférée rattaché à la formation sanitaire elle-même, indépendant du payeur auquel elle soumet ses dossiers :

```
Formation_Sanitaire
  ...
  locale_rapport_preferee   (nullable — sinon la résolution retombe sur le payeur, puis le français)
```

Un même dossier peut ainsi être soumis en français à l'INAM tout en produisant, à la demande, une copie de rapport en arabe pour l'usage interne de la structure — sans dupliquer la logique de validation, seule la couche de restitution change.

**Point d'attention technique, arabe uniquement :** l'arabe s'écrit de droite à gauche. Ça ne concerne pas le Référentiel de Libellés (le stockage de texte ne change pas), mais le moteur de rendu des rapports (section 14.3) doit savoir produire une mise en page RTL correcte, pas seulement traduire les mots. À vérifier lors du choix de l'outil de génération PDF.

**Ce qui reste hors périmètre pour l'instant :** les langues togolaises locales (éwé, kabyè), pour la même raison que déjà notée — aucun besoin exprimé, personnel de terrain opérant en français. Pas de changement sur ce point.

### 13.5 Ce qui ne se traduit jamais

Le Journal de Conformité (section 2.4) continue d'enregistrer des `rule_id`, pas du texte. C'est déjà une bonne propriété de l'architecture actuelle : un audit reste exploitable indépendamment de la langue d'affichage du moment, et un changement de libellé futur ne réécrit jamais l'historique.

---

## 14. Soumission groupée (batch) — fin de mois, logiciel de facturation tiers

### 14.1 Constat de terrain

Confirmé par Dr Amadou, 7 juillet 2026 : sur le terrain togolais, un centre qui dispose déjà de FHTP mais facture avec son propre logiciel (ou un tableur, cf. l'observation déjà notée au CHR Dapaong, FHTP-KNO-001 section 6.1) ne soumet en général pas ses dossiers un par un au fil des consultations. Il accumule les factures du mois, puis, à l'approche de l'échéance réglementaire du 5 du mois suivant (R-TG-002), les compile et les transmet toutes ensemble.

FHTP doit traiter ce mode comme un chemin normal, au même titre que le flux temps réel déjà décrit en section 10 — pas comme un contournement à tolérer.

### 14.2 Nouvelle entité : Lot_Soumission

```
Lot_Soumission
  id_lot
  id_formation (FK)
  periode_couverte          (ex: 2026-06, mois facturé)
  date_soumission
  format_source             [JSON | CSV | EXCEL | XML | PDF]
  canal                     [API | PORTAIL_UPLOAD]
  nombre_dossiers_detectes
  statut_lot                [RECU | EN_TRAITEMENT | TRAITE_PARTIEL | TRAITE_COMPLET]
```

**Ajout du 9 juillet 2026, sur demande de Dr Amadou : le format PDF.** Deux cas très différents se cachent derrière ce même format, à ne pas confondre :

1. **Export PDF structuré** — un logiciel de facturation produit un PDF qui reste, sous le capot, un tableau (lignes/colonnes identifiables). Extraction directe possible, proche du traitement d'un CSV.
2. **Compilation scannée de feuilles de soins physiques** — le cas le plus courant pour les cabinets sans logiciel : un lot de feuillets papier scannés en un seul PDF. Là, il n'y a pas de tableau à extraire, mais un ensemble de documents à reconnaître un par un, par OCR, avant de pouvoir les faire entrer dans le modèle générique de Dossier.

Le deuxième cas est nettement plus lourd que l'ajout d'un simple parseur de fichier : il demande un sous-module de reconnaissance de document (découpage du PDF en dossiers individuels, OCR par feuillet, extraction des champs obligatoires — code formation, code prescripteur, montants). C'est un chantier à part entière, pas une variante mineure du CSV/Excel déjà prévu. Retenu comme composant à spécifier séparément, pas encore détaillé ici.

Ajout sur `Dossier` (section 6) : un champ `id_lot` (nullable). Un dossier soumis en temps réel n'a pas de lot ; un dossier soumis en fin de mois en a un. Le reste du modèle ne change pas.

### 14.3 Déroulé

1. Le centre exporte ses factures du mois depuis son propre logiciel, ou les compile manuellement dans un tableur — c'est la réalité déjà documentée, FHTP s'y adapte plutôt que d'imposer un format neuf.
2. Soumission via `POST /api/v1/lots` (fichier Excel/CSV en pièce jointe, ou tableau JSON), ou par glisser-déposer sur le portail web pour les centres sans capacité d'intégration technique.
3. FHTP Core accuse réception immédiatement : `id_lot` et nombre de lignes détectées. Le traitement complet est asynchrone — personne ne doit rester devant son écran en attendant que 200 factures soient évaluées une par une.
4. Chaque dossier du lot passe ensuite par le moteur de règles à six piliers exactement comme un dossier temps réel (section 2.1). Aucune règle spécifique au mode batch n'existe dans le Core : seul le point d'entrée diffère, la logique de validation reste unique.
5. Un dossier malformé (champ obligatoire absent, date invalide, code acte inconnu) n'interrompt pas le traitement du lot : il reçoit un statut `REJET_FORMAT` propre à lui-même, avec le motif précis, pendant que les autres dossiers continuent leur évaluation normale.
6. Une fois le lot traité, deux niveaux de restitution :
   - **Rapport de synthèse** : répartition des dossiers par décision (FAST_TRACK / CONTROLE_RAPIDE / AUDIT_APPROFONDI / REJET_FORMAT).
   - **Rapport détaillé** : une ligne par facture, avec son évaluation complète des six piliers — exportable en CSV/Excel/PDF, ou consultable via `GET /api/v1/lots/{id}/rapport`.

### 14.4 Traitement en file, pas en transaction unique

Les dossiers d'un lot sont traités en file d'attente (queue), un par un, plutôt qu'en une seule grosse transaction. L'échec ou le ralentissement d'un dossier ne doit jamais bloquer les autres. Aucune limite arbitraire de taille n'est fixée à ce stade de conception ; le dimensionnement réel se calibrera une fois un premier volume de test observé.

### 14.5 Idempotence

Un centre peut corriger une facture rejetée et la resoumettre dans un lot ultérieur. Pour éviter tout double traitement ou double paiement potentiel, chaque dossier d'un lot porte une clé de dédoublonnage fournie par le centre lui-même (numéro de facture interne + code formation). Une resoumission avec la même clé mais un contenu modifié remplace la version précédente dans l'historique du dossier ; elle ne crée jamais un doublon de paiement. C'est la même préoccupation que celle déjà traitée pour la synchronisation du mode dégradé (section 7.4) — la solution se généralise naturellement au batch.

### 14.6 Articulation avec le mode dégradé et les PEC

- Un dossier créé hors-ligne pendant le mois (section 7) suit sa Sync Queue habituelle dès la reconnexion, puis peut simplement être rattaché au lot mensuel une fois synchronisé : le lot est un regroupement de présentation, pas un chemin de traitement parallèle à celui déjà défini.
- Un numéro de PEC présent dans un dossier de lot est vérifié exactement comme en temps réel, par requête au connecteur payeur concerné — jamais validé sur la seule présence d'un numéro dans le fichier importé. C'est directement la correction retenue pour l'incident du CHR Dapaong (F7, section 8.2) : le batch ne doit pas rouvrir cette faille sous une autre forme.

### 14.7 Format d'import : FHTP s'adapte au centre, pas l'inverse

Confirmé par Dr Amadou, 9 juillet 2026 : plutôt que d'imposer un format unique de fichier Excel/CSV, il vaut mieux que FHTP s'adapte au format que chaque centre utilise déjà. C'est la même logique que celle déjà retenue pour les logiciels terrain (FHTP-KNO-001 section 3.5) : FHTP s'intègre à l'existant, il ne remplace pas les habitudes déjà en place.

**Nouvelle entité : profil d'import propre à chaque centre.**

```
Profil_Import_Centre
  id_profil
  id_formation (FK)
  format_source        [CSV | EXCEL | PDF]
  mapping_colonnes      (association colonne du fichier du centre -> champ du modèle générique de Dossier ;
                         ex: "Colonne C" -> montant_facture, "Colonne F" -> code_prescripteur)
  date_configuration
  configure_par         [EQUIPE_FHTP | CENTRE]
```

**Fonctionnement retenu :** à l'onboarding d'un centre (ou lors de sa première soumission groupée), un exemple de fichier tel qu'il l'utilise déjà est déposé une fois ; l'équipe FHTP — ou le centre lui-même via un assistant de configuration simple — associe chaque colonne détectée à un champ du modèle générique. Ce mapping est enregistré comme profil et réutilisé automatiquement à chaque soumission suivante, sans que le centre ait à reformater son export mensuel habituel. Si le centre change de logiciel ou modifie la structure de son fichier, une nouvelle version du profil est créée — l'ancienne reste consultable pour l'historique, même logique de versionnage que le reste des référentiels.

Ce mapping résout le format d'entrée avant que le moteur de règles n'intervienne : quel que soit le fichier reçu, ce que le Core évalue reste toujours le même modèle de Dossier consolidé (section 6). Le point ouvert précédemment noté ici est donc tranché — plus de format imposé, un profil par centre.

### 14.8 Risque de fiabilité — reconnaissance des PDF issus de scans de factures

Inquiétude soulevée par Dr Amadou, 9 juillet 2026, à propos du deuxième cas de la section 14.2 (compilation scannée de feuillets papier) : la reconnaissance automatique risque de poser problème en pratique. Ce n'est pas une inquiétude à écarter — elle est fondée, et cohérente avec ce que le projet a déjà documenté ailleurs :

- Les feuillets de la convention CAT sont auto-carbonés (FHTP-REF-001, Partie 2.7) : la copie la moins bonne d'une liasse à cinq feuillets est structurellement plus pâle et moins nette que l'originale.
- Les mentions manuscrites (diagnostic, posologie, signature) varient d'un prescripteur à l'autre et se superposent parfois au cachet — exactement le type de document qui met en échec un OCR généraliste, pas seulement un cas limite rare.
- Un scan fait au téléphone par un opérateur pressé n'a pas la qualité d'un scanner à plat.

**Décision de conception : ne pas faire reposer la validation automatique sur la seule confiance en l'OCR.** Concrètement :

1. L'extraction OCR propose des valeurs de champs, chacune avec un score de confiance.
2. Tout champ en dessous d'un seuil de confiance (à calibrer sur de vrais échantillons, pas fixé arbitrairement ici) est signalé comme à vérifier, jamais deviné silencieusement.
3. Un dossier issu de ce chemin ne peut pas atteindre une évaluation à six piliers avant qu'un opérateur humain (au centre ou chez FHTP) ait confirmé ou corrigé les champs signalés. Nouveau statut : `EN_ATTENTE_CONFIRMATION_OCR`.
4. Le scan d'origine reste hashé et archivé (même mécanisme que la section 8.4) indépendamment des corrections apportées, pour que toute correction reste traçable jusqu'au document source.

Ce principe reprend directement celui déjà posé pour le mode dégradé et pour le scan de PEC (section 15) : une source d'entrée moins fiable ne bloque jamais le service, mais elle ne saute jamais non plus l'étape de confirmation humaine avant de nourrir le moteur de règles.

**Recommandation de séquencement, dans le même esprit que celui déjà retenu pour le reste du projet (documenter d'abord, construire ensuite) :** plutôt que d'investir tout de suite dans un pipeline d'extraction automatique complet, il vaut mieux collecter un premier lot réel de factures scannées, les faire relire manuellement, et calibrer sur cet échantillon ce qui est réellement reconnaissable avant d'engager le développement du sous-module OCR. En attendant, le chemin principal recommandé pour la soumission groupée reste le format structuré (CSV/Excel/JSON via le Profil_Import_Centre) ; le PDF scanné est accepté comme pièce justificative jointe au dossier, avec une saisie assistée plutôt qu'une extraction automatique aveugle.

---

## 15. Vérification de PEC en l'absence de connexion payeur — pièce scannée et référentiel des modèles de documents

### 15.1 Rappel du principe déjà acté, et de sa limite

La correction F7 (FHTP-ARC-001 section 8.2) est ferme : la validité d'une PEC est toujours vérifiée par requête au connecteur payeur concerné, jamais par la seule présence d'un numéro au bon format. C'est la correction directe de l'incident du CHR Dapaong (FHTP-KNO-001 section 6.1).

Cette règle suppose que le connecteur payeur est joignable. Le mode dégradé (section 7) couvre déjà la coupure réseau générale, avec un plafond clair : un dossier créé hors ligne ne reçoit jamais FAST_TRACK avant reconnexion et réévaluation en ligne. Mais rien n'était prévu de spécifique pour le cas d'une PEC précisément, au-delà de ce plafond général. Demande de Dr Amadou, 9 juillet 2026 : durcir ce point particulier plutôt que de le laisser dans le seul filet générique du mode dégradé.

### 15.2 Pièce scannée obligatoire

Quand le connecteur du payeur concerné est injoignable et qu'un acte du dossier dépend d'une PEC, FHTP exige le rattachement d'un scan de la PEC accordée avant d'accepter le dossier, même en statut provisoire. Sans ce scan, le dossier reste bloqué en attente de pièce — pas de contournement silencieux.

Ce scan est hashé au moment du dépôt (même mécanisme que la section 8.4, ancrage côté serveur) : ce qui a été fourni à cet instant précis est figé, pour qu'une substitution ultérieure du document soit détectable.

### 15.3 Référentiel des modèles de documents payeurs (nouvelle entité)

Un scan seul ne prouve rien par lui-même — n'importe quel document peut être scanné. Pour donner un minimum de valeur à ce contrôle en attendant la vérification en ligne, FHTP mémorise le format officiel connu de chaque type de document délivré par chaque payeur, et compare le scan reçu à ce modèle de référence.

**Précision de Dr Amadou, 9 juillet 2026 : pour un même payeur, le format varie selon le type d'acte.** Une PEC d'hospitalisation, une entente pour analyse biologique, une pour imagerie, une pour pharmacie (TPC), une pour kinésithérapie et une pour lunetterie n'ont pas la même structure — même si l'en-tête et le cachet du payeur restent en général identiques d'un type d'acte à l'autre. Le référentiel doit donc distinguer les deux niveaux plutôt que de dupliquer l'en-tête et le cachet dans six entrées différentes :

```
Modele_Payeur_Socle
  id_payeur_connecteur (FK, une entrée par payeur)
  mentions_communes      (éléments partagés quel que soit le type d'acte : en-tête, cachet, signature du médecin-conseil)
  date_version

Modele_Document_Payeur
  id_modele
  id_payeur_connecteur (FK)
  type_acte               [HOSPITALISATION | ANALYSE_BIOLOGIQUE | IMAGERIE | PHARMACIE_TPC | KINESITHERAPIE | LUNETTERIE | AUTRE]
  type_document           [PEC_STANDARD | PEC_URGENCE | TPC | AUTRE]
  mentions_specifiques     (propre à ce type d'acte : ex. numéro de séjour pour l'hospitalisation, référence opticien agréé pour la lunetterie)
  date_version
  source                   (ex : exemplaire officiel transmis par le payeur ou par Dr Amadou)
```

Le rapprochement combine les deux niveaux : mentions communes du socle du payeur, plus mentions spécifiques au type d'acte concerné par le dossier. Ça reste un filtre de cohérence structurelle (présence des mentions attendues, mise en page reconnaissable), pas une preuve cryptographique — même nature de vérification que le pilier 4 (cohérence documentaire), appliquée ici à un document spécifique plutôt qu'à l'ordonnance elle-même.

**Reste à clarifier avec Dr Amadou :** au-delà de la variation par type d'acte déjà tranchée ici, existe-t-il aussi des variantes selon le centre ou l'antenne régionale du payeur qui délivre la PEC ? La structure retenue suppose un modèle par payeur et par type d'acte, valable pour tous les centres qui en dépendent — à confirmer avant de figer le schéma définitivement.

**Tranché le 9 juillet 2026, sur confirmation de Dr Amadou :** non, un payeur garde la même identité visuelle quel que soit le centre ou l'antenne régionale qui délivre le document — pas de variante à prévoir dans le cas général. Le modèle par payeur et par type d'acte défini ci-dessus suffit.

Par prudence, une porte de sortie reste néanmoins ouverte plutôt que fermée en dur, au cas où un cas particulier apparaîtrait un jour (ex. une antenne isolée utilisant encore un ancien formulaire) :

```
Modele_Document_Payeur
  ...
  variante_centre (nullable, FK vers Formation_Sanitaire — vide par défaut ; ne sert que si une exception réelle est un jour constatée)
```

Ce champ ne change rien au fonctionnement courant : tant qu'il reste vide, le rapprochement utilise le modèle générique du payeur. Il évite seulement d'avoir à modifier la structure de la table le jour où une exception confirmée se présenterait.

### 15.4 Statuts et issue

`PEC_Entente_Prealable` (section 6) gagne un statut intermédiaire :

```
statut: [EN_ATTENTE | ACCORDE | REFUSE | EXPIRE | SILENCE_VAUT_ACCORD | EN_ATTENTE_VERIFICATION_SCAN]
scan_hash (nullable — renseigné uniquement en EN_ATTENTE_VERIFICATION_SCAN)
```

- **Scan cohérent avec le modèle du payeur** → le dossier peut avancer, mais reste plafonné exactement comme en mode dégradé (section 7.2) : jamais FAST_TRACK avant que le numéro de PEC ait été effectivement reconfirmé en ligne dès la reconnexion. Le rapprochement visuel achète de la continuité de service, pas une validation définitive.
- **Scan incohérent** (mentions manquantes, mise en page qui ne correspond à aucun modèle connu) → statut ANOMALIE sur le pilier documentaire, escalade vers AUDIT_APPROFONDI, avec motif explicite plutôt qu'un rejet muet — le prestataire doit savoir précisément ce qui cloche pour pouvoir régulariser.
- Dès la reconnexion, la vérification en ligne reprend la priorité sur tout le reste : si le payeur infirme la PEC malgré un scan jugé cohérent, le dossier bascule en CONTROLE_RAPIDE, comme déjà prévu pour toute réévaluation post-synchronisation (section 7.2).

---

## Annexe — Récapitulatif des nouvelles entités (pour fusion dans la section 6 de FHTP-ARC-001)

Les entités introduites dans cet addendum sont dispersées entre les sections 13, 14 et 15. Ce tableau les regroupe en un seul endroit, pour faciliter leur intégration dans le modèle de données consolidé de la section 6 du document maître.

| Entité | Introduite en | Rattachement | Rôle |
|---|---|---|---|
| `Referentiel_Libelle` | 13.2 | Référentiel de Règles (section 2.5) | Sépare le texte affiché (par langue) de la logique des règles |
| `Lot_Soumission` | 14.2 | `Formation_Sanitaire` (FK) | Regroupe les dossiers soumis en fin de mois |
| `Profil_Import_Centre` | 14.7 | `Formation_Sanitaire` (FK) | Mémorise le mapping de colonnes propre au fichier habituel d'un centre |
| `Modele_Payeur_Socle` | 15.3 | `Contrat_Payeur` / connecteur payeur (FK) | En-tête et cachet communs à tous les types d'actes d'un même payeur |
| `Modele_Document_Payeur` | 15.3 | `Modele_Payeur_Socle` (FK) + type d'acte | Mentions spécifiques par type d'acte, avec `variante_centre` optionnel |

Champs ajoutés sur des entités déjà existantes en section 6 :

| Entité existante | Champ ajouté | Rôle |
|---|---|---|
| `Dossier` | `id_lot` (nullable) | Rattache un dossier à un lot s'il a été soumis en groupé |
| `Formation_Sanitaire` | `locale_rapport_preferee` (nullable) | Langue des rapports, indépendante du payeur |
| `PEC_Entente_Prealable` | `scan_hash` (nullable) | Trace le document scanné fourni en l'absence de connexion payeur |
| `PEC_Entente_Prealable` | statut : ajout de `EN_ATTENTE_VERIFICATION_SCAN` | Plafonne l'usage d'un scan non encore reconfirmé en ligne |

Un nouveau statut de dossier a aussi été introduit hors de ce tableau (section 14.8) : `EN_ATTENTE_CONFIRMATION_OCR`, pour les dossiers issus d'une reconnaissance de PDF scanné en attente de confirmation humaine.

---

## 16. Journal des versions (entrée à ajouter à la section existante)

| Version | Date | Auteur | Changements |
|---|---|---|---|
| 0.6 | 8 juillet 2026 | Claude (sur demande de Dr Amadou) | Ajout de l'API FHTP Core en exposition directe (distincte des connecteurs), séparée en soumission unitaire synchrone et soumission groupée asynchrone. Ajout du support multilingue (référentiel de libellés séparé de la logique des règles, résolution de langue par requête/connecteur/défaut français, portée limitée à français/anglais pour l'instant). Ajout du mode de soumission groupée (batch) pour les centres facturant avec un logiciel tiers ou un tableur en fin de mois, avec nouvelle entité Lot_Soumission, traitement en file indépendant par dossier, idempotence par clé fournie par le centre, et articulation avec le mode dégradé et la vérification systématique des PEC déjà actée. |
| 0.7 | 9 juillet 2026 | Claude (sur demande de Dr Amadou) | Extension de la portée linguistique : portugais et espagnol (portabilité régionale, Guinée-Bissau/Cap-Vert et Guinée équatoriale), et arabe (besoin déjà présent au Togo : ONG islamiques gérant orphelinats et structures de soins associées, échangeant avec leurs partenaires en arabe) ; ajout d'un attribut de langue de rapport préférée par formation sanitaire, indépendant du payeur, et note sur le rendu RTL. Ajout du format PDF en soumission groupée, avec distinction entre export structuré et compilation scannée de feuillets (ce second cas renvoyé à un sous-module de reconnaissance de document à spécifier séparément). Ajout d'une section dédiée à la vérification de PEC en l'absence de connexion payeur : pièce scannée obligatoire, hachage à l'ancrage, nouveau référentiel des modèles de documents payeurs pour un contrôle de cohérence structurelle, statut intermédiaire EN_ATTENTE_VERIFICATION_SCAN plafonné comme le mode dégradé, sans jamais remplacer la vérification en ligne définitive. |
| 0.8 | 9 juillet 2026 | Claude (sur demande de Dr Amadou) | Référentiel des modèles de documents payeurs éclaté en deux niveaux (Modele_Payeur_Socle pour l'en-tête et le cachet communs, Modele_Document_Payeur par type d'acte) pour refléter le fait qu'un même payeur utilise un format différent selon le type d'acte (hospitalisation, analyse biologique, imagerie, pharmacie/TPC, kinésithérapie, lunetterie). Point ouvert sur le format des factures groupées tranché : plutôt qu'un format imposé, nouvelle entité Profil_Import_Centre qui mémorise le mapping de colonnes propre à chaque centre, configuré une fois puis réutilisé automatiquement à chaque soumission mensuelle. |
| 0.9 | 9 juillet 2026 | Claude (sur demande de Dr Amadou) | Confirmation qu'un payeur garde la même identité documentaire quel que soit le centre ou l'antenne régionale ; ajout d'un champ optionnel variante_centre par prudence, vide par défaut, sans complexifier le cas courant. Ajout de la section 14.8 sur le risque de fiabilité de la reconnaissance des PDF scannés : décision de ne jamais faire reposer la validation automatique sur la seule confiance en l'OCR, nouveau statut EN_ATTENTE_CONFIRMATION_OCR exigeant confirmation humaine des champs à faible confiance avant évaluation par le moteur de règles, et recommandation de séquencement (calibrer sur un échantillon réel avant d'investir dans un pipeline d'extraction complet, le format structuré via Profil_Import_Centre restant le chemin principal recommandé). |
| 0.10 | 9 juillet 2026 | Claude | Ajout d'une annexe récapitulative regroupant toutes les nouvelles entités et tous les champs ajoutés introduits dans cet addendum (dispersés entre les sections 13, 14 et 15), pour faciliter leur fusion en un seul passage dans la section 6 du document maître. |
