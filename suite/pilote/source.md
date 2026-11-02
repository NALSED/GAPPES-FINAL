# source.md — Sources officielles Aleph (OCCRP) et Maltego, pour l'agent de codage

> **Écrit par Sednal, fourni directement à momo et conservé ici pour mémoire et traçabilité.**
> **Statut : notes de travail. Rien n'est acté sans validation de Sednal.**
> Ce document synthétise de la documentation **officielle et publique**. Il ne contient aucune information issue de rétro-ingénierie.

---

## 0. Comment lire ce document

- Objectif de Sednal : **s'inspirer** des mécanismes d'Aleph et de Maltego pour son logiciel OSINT. **Pas de copie** de code ni d'interface.
- Niveaux de confiance utilisés ci-dessous :
  - **[OFFICIEL]** : lu dans la documentation officielle de l'éditeur.
  - **[OFFICIEL-INDIRECT]** : documentation officielle d'une brique voisine (FollowTheMoney, OpenAleph, SDK Maltego).
  - **[À CONFIRMER]** : détail non vérifié sur une source primaire. Ne pas coder dessus sans vérifier sur une instance réelle (`/api/openapi.json` pour Aleph) ou dans le dépôt.
- Si une information manque ici, **ne pas l'inventer** : demander à Sednal ou aller à la source listée en §7.

### Règles de travail pour toi, agent

1. Tu t'inspires des **concepts** : modèle de données, séparation des rôles, patron d'appel. Tu ne recopies ni code ni textes.
2. Avant d'utiliser du code Aleph/FtM/OpenAleph, **vérifie la licence** (§2.9).
3. Tu ne tentes **aucune** opération de rétro-ingénierie sur Maltego (§3.8). Tout ce qu'il faut savoir sur son protocole est déjà publié par l'éditeur.
4. Chaque décision d'architecture issue de ce document est une **proposition** à soumettre à Sednal, pas une décision.

---

## 1. Vue d'ensemble : deux logiciels, deux philosophies

| Axe | Aleph (OCCRP) | Maltego |
|---|---|---|
| Rôle | Plateforme de **recherche documentaire + graphe de données** (fuites, registres, documents) | Outil d'**enquête interactive par graphe**, piloté par des « Transforms » |
| Approche | Tu **ingères** des données, elles sont indexées, croisées, consultées | Tu **pars d'une entité** et tu lances des requêtes à la demande qui la font grandir |
| Modèle | FollowTheMoney (schémas typés, propriétés multi-valuées) | Entités typées (standard + personnalisées) reliées par des liens |
| Extensibilité | Ingestion (alephclient, mappings, Memorious), API REST | Transforms (serveurs HTTP ou commandes locales), SDK, Hub |
| Mode | Serveur web multi-utilisateurs | Application bureau Java + serveurs de Transforms |
| Licence | Open source (voir §2.9) | Propriétaire (voir §3.8) |

Idée centrale à retenir : **Aleph = « pull-then-search »** (je collecte, j'indexe, je recherche). **Maltego = « seed-then-expand »** (je pars d'un point, j'élargis par appels). Un logiciel OSINT complet a souvent besoin des deux.

---

## 2. ALEPH

### 2.1 Architecture [OFFICIEL]

Composants décrits par la documentation d'Aleph :

- **API** : application Flask (Python), expose l'API REST.
- **UI** : application React (front).
- **Workers** : traitements asynchrones (ingestion, analyse, indexation, xref).
- **ingest-file** : service qui reçoit les documents et en extrait texte, métadonnées, entités (OCR, conversion, détection de langue, etc.).
- **Store FtM** : stockage des entités FollowTheMoney (PostgreSQL).
- **Base applicative** : utilisateurs, collections, rôles, permissions.
- **Elasticsearch** : index de recherche (entités, documents, résultats xref).
- **Redis** : files de tâches et état.
- **Archive de fichiers** : stockage des fichiers bruts (disque local, S3, GCS).
- **alephclient** : client CLI/Python pour pousser des données.
- **Memorious** : framework de crawlers qui alimente Aleph.

Flux logique à retenir :

````text
Source (fichier, crawler, mapping CSV/SQL)
        │
        ▼
  ingest / mapping ──► entités FtM ──► store (PostgreSQL)
                                          │
                                          ▼
                              worker : analyse + indexation
                                          │
                                          ▼
                                   Elasticsearch
                                          │
                                  API REST ◄── UI React
````

**À retenir pour le projet** : séparer **collecte**, **normalisation**, **stockage de vérité**, **index de recherche**. L'index est une vue reconstructible. La vérité est dans le store.

### 2.2 FollowTheMoney (FtM) : le modèle de données [OFFICIEL-INDIRECT]

FtM est la bibliothèque/modèle d'Aleph (MIT). C'est **la partie la plus réutilisable en idée**.

Principes :

- Une **entité** = `id` + `schema` + `properties`.
- `schema` : type de l'entité (hiérarchie avec héritage). Exemples courants : `Thing`, `Person`, `Company`, `Organization`, `LegalEntity`, `Document`, `Address`, `Email`, `Event`.
- `properties` : dictionnaire où **chaque valeur est une liste** (multi-valué par défaut). Exemple : une personne peut avoir plusieurs `name`, plusieurs `nationality`.
- **Références entre entités** : une propriété de type « entity » contient l'`id` d'une autre entité.
- **Entités interstitielles** : une relation n'est **pas** une simple arête. C'est une entité à part entière, avec ses propres propriétés (dates, montant, source). Exemples : `Ownership` (owner → asset), `Directorship` (director → organization), `Family`, `Membership`, `Payment`, `Associate`.

Exemple d'entité (forme JSON de flux) :

````json
{
  "id": "ex-person-001",
  "schema": "Person",
  "properties": {
    "name": ["Jean Dupont", "J. Dupont"],
    "nationality": ["fr"],
    "birthDate": ["1980-04-12"]
  }
}
````

Exemple de relation interstitielle :

````json
{
  "id": "ex-own-001",
  "schema": "Ownership",
  "properties": {
    "owner": ["ex-person-001"],
    "asset": ["ex-company-042"],
    "percentage": ["60"],
    "startDate": ["2019-01-01"]
  }
}
````

Pourquoi c'est intéressant pour de l'OSINT :

- Une même personne trouvée dans 5 sources n'est pas un conflit : c'est **la même entité avec 5 valeurs de `name`**, chacune traçable.
- La relation porte l'information (date, source, pourcentage). Une simple arête ne le permet pas.
- Les schémas héritent : un traitement écrit pour `LegalEntity` marche pour `Person` et `Company`.

Formats d'échange FtM [OFFICIEL-INDIRECT] :

- **Flux NDJSON** (une entité par ligne), extension `.ftm`.
- Variante `.ijson` (« JSON itératif »).
- **Mappings YAML** : décrivent comment transformer un CSV ou une table SQL en entités FtM (quelle colonne → quelle propriété, comment fabriquer l'`id`).

Outil `ftm` (CLI) [OFFICIEL-INDIRECT] : commandes `map` (appliquer un mapping), `aggregate` (fusionner des fragments d'une même entité), `sign` (calculer des identifiants stables), `validate`, `export` (vers CSV, graphe, etc.).

Notion à copier **en concept** : l'**agrégation de fragments**. Chaque source produit un fragment d'entité avec le même `id`. Un pas d'agrégation les fusionne. Cela rend l'ingestion idempotente et parallélisable.

### 2.3 Pipeline d'ingestion [OFFICIEL]

Étapes conceptuelles :

1. Réception d'un fichier (via UI, alephclient, crawler).
2. Création d'une entité `Document` dans une **collection**.
3. Worker `ingest-file` : détection du type, conversion, extraction de texte, OCR si besoin, extraction de métadonnées, création d'entités enfants (pièces jointes d'un mail, pages d'un PDF).
4. Analyse : extraction de noms, lieux, e-mails, téléphones, etc., et création d'entités « mentionnées ».
5. Indexation dans Elasticsearch.
6. Optionnel : recoupement (xref) avec les autres collections.

À retenir : tout est **asynchrone**, avec des files de tâches. L'utilisateur voit un état de progression. Une défaillance d'un étage ne bloque pas les autres.

### 2.4 API REST [OFFICIEL + À CONFIRMER]

Points confirmés par la doc :

- Préfixe `/api/2/`.
- Authentification par clé d'API : en-tête `Authorization: ApiKey <clé>`.
- Recherche avec filtres de la forme `filter:<champ>=<valeur>`, facettes `facet=<champ>`, pagination `limit` / `offset`.
- Opérations de type « développer » (`expand`) et « similaires » (`similar`) sur une entité.

**[À CONFIRMER]** : les chemins exacts de chaque endpoint, les noms précis de paramètres et les codes d'erreur. Sur une instance Aleph/OpenAleph, la spécification OpenAPI fait foi. Ne pas deviner.

Patron à retenir : l'API distingue **recherche** (texte + filtres + facettes) et **navigation de graphe** (`expand` = voisins d'une entité).

### 2.5 Recoupement entre collections (xref) [OFFICIEL]

- Aleph compare les entités des collections entre elles pour trouver des correspondances probables.
- Méthode : génération de **candidats** par **empreintes** (fingerprints de noms normalisés) dans l'index, puis **score** (modèle ML) pour classer.
- Résultats stockés dans un **index séparé**. L'utilisateur confirme ou rejette (« décision »).
- Les décisions humaines alimentent la qualité ensuite.

À retenir : **deux étages** (rappel large par index, précision par score) + **boucle de validation humaine**. Très transposable.

### 2.6 Permissions [OFFICIEL]

- Les données sont regroupées en **collections**.
- Permissions **par collection** : lecture, écriture. Attribuables à des utilisateurs ou groupes.
- Rôles : utilisateurs, groupes, administrateurs.

À retenir : une enquête (ou un dossier) = une collection = une frontière d'accès. Simple et robuste.

### 2.7 Outils d'alimentation [OFFICIEL]

- **alephclient** : `alephclient crawldir`, envoi de dossiers, flux d'entités, création de collections. Configuration par variables d'environnement (hôte, clé d'API).
- **Mappings** : YAML qui transforme des tables en entités (voir §2.2).
- **Memorious** : crawlers déclaratifs (étapes enchaînées : fetch, parse, store).

### 2.8 OpenAleph (fork) [OFFICIEL-INDIRECT]

Fork maintenu activement. Différences repérées dans sa documentation :

- File de tâches **Procrastinate** (PostgreSQL) en remplacement d'une partie de la plomberie d'origine.
- Service d'analyse `ftm-analyze` séparé.
- Bibliothèque Python `openaleph` et variables `OPAL_HOST` / `OPAL_API_KEY`.
- Grammaire de requête documentée (parser de requêtes de recherche).

Utile comme **référence de ce qui est maintenu aujourd'hui**. Vérifier la version avant de s'y fier.

### 2.9 Licences [OFFICIEL, à revérifier au moment d'utiliser du code]

- `aleph` d'origine : MIT.
- `followthemoney` : MIT.
- `ingest-file` : AGPLv3+ à partir de la version 3.18.4. **Attention** : la licence AGPL impose des obligations si tu intègres/exposes ce code en service réseau.
- `openaleph-search` : AGPLv3.

Règle : **s'inspirer de l'architecture est libre. Intégrer du code AGPL dans le projet demande une décision explicite de Sednal.**

### 2.10 Ce qu'on peut en tirer pour le projet OSINT

Propositions (à valider par Sednal) :

1. **Modèle d'entité inspiré de FtM** : `id`, `schema` typé hérité, `properties` multi-valuées, relations comme entités. Chaque valeur porte sa **source** et sa **date de collecte**.
2. **Pipeline asynchrone** : collecte → normalisation → stockage → analyse → index. Chaque étape sur une file.
3. **Idempotence par fragments + agrégation** (voir §2.2).
4. **Recoupement en deux étages** avec validation humaine (§2.5).
5. **Collections comme frontière d'accès** (§2.6).
6. **Séparation vérité / index** : l'index est reconstructible.
7. **Format d'échange NDJSON** pour importer/exporter facilement.

---

## 3. MALTEGO

### 3.1 Architecture [OFFICIEL]

Trois rôles :

- **Maltego Desktop** : application Java (client graphique). Versions de Java supportées indiquées par l'éditeur : 8, 11, 17 selon les versions. Interface graphique obligatoire, y compris sous Linux (X11).
- **TDS (Transform Distribution Server)** : serveur de l'éditeur qui distribue les Transforms du Hub et sert d'intermédiaire.
- **Serveurs de Transforms** : serveurs HTTP (de l'éditeur, de tiers ou **les tiens**) qui reçoivent une entité et renvoient d'autres entités.

Variante : **Local Transforms**, des commandes exécutées sur la machine de l'utilisateur, sans serveur.

````text
  Utilisateur ─► Maltego Desktop ─► TDS ─► Serveur de Transforms ─► sources de données
                       │                          (HTTP)
                       └─► Local Transform (commande locale, sortie XML)
````

Les hôtes et ports que le client doit pouvoir joindre sont **listés dans la documentation officielle** (page « System Architecture » / exigences réseau). Il n'y a donc pas besoin de les découvrir autrement.

### 3.2 Qu'est-ce qu'une Transform [OFFICIEL]

Une Transform est une fonction :

````text
entité d'entrée  ──►  Transform  ──►  0..N entités de sortie (+ liens + messages UI)
````

Éléments :

- **Type d'entrée** : un type d'entité précis (ex. `maltego.Domain`).
- **Sortie** : des entités avec valeur, propriétés, poids, liens (étiquette, style), éventuellement des messages affichés à l'utilisateur.
- **Réglages** (settings) : paramètres demandés à l'utilisateur (clé d'API, limite).
- **Limites** : l'utilisateur fixe un nombre maximum de résultats ; la Transform doit les respecter.

C'est l'application directe du patron **« seed-then-expand »**.

### 3.3 Protocole de Transform (XML) [OFFICIEL, forme historique]

La documentation publique décrit un échange de messages XML. Forme simplifiée (**illustrative**, la doc de la version courante fait foi) :

Requête :

````xml
<MaltegoMessage>
  <MaltegoTransformRequestMessage>
    <Entities>
      <Entity Type="maltego.Domain">
        <Value>example.org</Value>
        <Weight>100</Weight>
        <AdditionalFields>...</AdditionalFields>
      </Entity>
    </Entities>
    <Limits SoftLimit="12" HardLimit="12"/>
    <TransformFields>...</TransformFields>
  </MaltegoTransformRequestMessage>
</MaltegoMessage>
````

Réponse :

````xml
<MaltegoMessage>
  <MaltegoTransformResponseMessage>
    <Entities>
      <Entity Type="maltego.IPv4Address">
        <Value>192.0.2.10</Value>
        <Weight>100</Weight>
      </Entity>
    </Entities>
    <UIMessages>
      <UIMessage MessageType="Inform">Terminé</UIMessage>
    </UIMessages>
  </MaltegoTransformResponseMessage>
</MaltegoMessage>
````

**[À CONFIRMER]** : la version courante du SDK Python (§3.4) masque ces détails. Elle fournit des classes Python, et la documentation de l'éditeur est la référence du format exact. Ne pas coder un parseur XML « maison » sans l'avoir confronté à la doc actuelle.

Local Transform (principe) : Maltego lance une commande, lui passe la valeur de l'entité et ses champs en arguments, et lit la réponse XML sur la sortie standard. C'est le moyen le plus simple de brancher un script.

### 3.4 SDK Python officiel (v1.0.0) [OFFICIEL]

Paquets : `maltego-transforms` et `maltego-transforms-std-entities`. Concepts :

- `@register_transform` : déclare une fonction comme Transform (nom, type d'entrée, description, réglages).
- `@register_entity` : déclare une entité personnalisée (propriétés typées).
- Objets : `MaltegoGraph`, `Entity`, `Link`, `Context` (contexte de requête : limites, réglages, identité).
- `TransformSetting` : paramètre déclaré, saisi par l'utilisateur.
- **Middlewares** : code exécuté avant/après chaque Transform (journalisation, quotas, authentification).
- `MaltegoServerSettings` / `ServerHTTPSettings` : configuration du serveur.
- Serveur basé sur **FastAPI**.
- **Runners** : exécution des Transforms en threads ou en asynchrone.
- **Authentification** : JWT, OIDC, SAML.
- Bibliothèque d'**entités standard** (domaines, IP, personnes, e-mails, etc.).

Squelette de principe (pseudo-code, **pas** du code garanti) :

````python
# Pseudo-code d'illustration du patron
@register_transform(name="DomainToIPs", input_entity="Domain")
def domain_to_ips(ctx, graph, entity):
    for ip in resolve(entity.value)[: ctx.limit]:
        node = graph.add_entity("IPv4Address", ip)
        graph.add_link(entity, node, label="resolves to")
````

Pour les signatures réelles, lire la **référence d'API** du SDK. Ne pas se fier à ce pseudo-code.

Ancienne bibliothèque : `maltego-trx` (open source), à connaître car beaucoup d'exemples publics l'utilisent. La documentation actuelle pousse vers le nouveau SDK.

### 3.5 Entités standard, Machines, Hub [OFFICIEL]

- **Entités standard** : catalogue officiel (personne, e-mail, domaine, DNS, IP, réseau, organisation, document, etc.). Utile comme **liste de départ de types OSINT**, avec les propriétés usuelles.
- **Machines** : scénarios automatisés qui enchaînent des Transforms (macros). Idée : un **playbook** déclaratif.
- **Hub** : catalogue/marketplace de Transforms (« Hub items »). Un **Transform Seed** (`/seed`) permet à un serveur de Transforms d'être découvert et installé côté client.

### 3.6 Idées à retenir (concept) pour le projet

Propositions (à valider par Sednal) :

1. **Contrat de Transform** : `entrée typée → liste d'entités + liens + messages`, avec limites, réglages, et nom/description. Chaque « connecteur OSINT » suit ce contrat.
2. **Deux modes de branchement** : connecteurs **in-process** (plugin Python) et connecteurs **distants** (HTTP) pour isoler les sources instables ou sous licence.
3. **Middleware** autour de chaque appel : journal, limite de débit, quota, cache, respect des conditions d'usage de la source.
4. **Réglages déclarés** (clé d'API, limites) séparés du code.
5. **Playbooks** (équivalent des Machines) : séquences déclaratives de connecteurs.
6. **Catalogue de types** : s'appuyer sur la liste d'entités standard comme inspiration de l'ontologie initiale, puis mapper vers le modèle FtM-like (§2.10).
7. **Provenance sur chaque résultat** : quelle Transform, quelle source, quand. (Maltego ne l'impose pas strictement ; Aleph via FtM s'y prête bien.)

### 3.7 Combiner les deux : proposition d'architecture

````text
 Connecteurs (contrat « Transform »)           Ingestion (pipeline « Aleph »)
   entité ─► connecteur ─► entités+liens          fichiers / crawlers / tables
                  │                                          │
                  └──────────► normalisation en entités typées ◄─────────┘
                                         │
                              Store (vérité) + provenance
                                         │
                       Index de recherche  +  recoupement (2 étages)
                                         │
                      API  ◄──  UI (recherche, graphe, validation humaine)
````

Les connecteurs alimentent le même store que l'ingestion de documents. La **recherche** et le **graphe** lisent le même modèle.

### 3.8 Licence et limites juridiques de Maltego (IMPORTANT)

Le contrat de licence (EULA / conditions générales de Maltego) interdit notamment :

- le désassemblage, la décompilation et la rétro-ingénierie du logiciel (sauf dans la mesure permise par la loi applicable) ;
- le contournement des mécanismes de licence, de sécurité ou de chiffrement ;
- la **rétro-ingénierie de tout protocole de communication**.

Conséquences pour toi, agent :

- **Ne propose, ne génère et ne lance aucune** décompilation de JAR, interception TLS, contournement de licence ou analyse du protocole propriétaire.
- Les mécanismes d'appel (Transforms, TDS, hôtes/ports) étant **documentés publiquement** par l'éditeur, tu n'as **pas besoin** de les découvrir autrement. Utilise uniquement §7.
- Si un détail manque dans la doc publique, **dis-le à Sednal** au lieu de le déduire d'une analyse du binaire.

---

## 4. Tableau de correspondance (inspiration → projet)

| Besoin du projet | Inspiration Aleph | Inspiration Maltego | Proposition |
|---|---|---|---|
| Modèle de données | FtM : schémas, propriétés multi-valuées, relations-entités | Types d'entités standard | Modèle FtM-like + catalogue de types inspiré des entités standard |
| Alimenter le système | alephclient, mappings, crawlers | Transforms à la demande | Deux voies : ingestion en lot + connecteurs interactifs |
| Extensibilité | Mappings YAML, crawlers | SDK, serveurs distants, Hub | Contrat de connecteur + plugins in-process + connecteurs HTTP |
| Dédoublonnage / recoupement | xref 2 étages + décision humaine | Fusion manuelle dans le graphe | xref 2 étages + file de validation |
| Accès | Permissions par collection | Licences/éditions | Dossier = frontière d'accès |
| Automatisation | Workers asynchrones | Machines | Playbooks déclaratifs sur la file de tâches |
| Traçabilité | Entités sources, collections | (limitée) | Provenance obligatoire sur chaque valeur |

---

## 5. Points ouverts à soumettre à Sednal

1. Base de stockage : PostgreSQL seul, ou PostgreSQL + moteur de recherche ?
2. Tolérance à la licence AGPL (intégrer du code) ou inspiration uniquement ?
3. Connecteurs : tous in-process au départ, ou dès le début un mode HTTP distant ?
4. Périmètre de provenance : par entité, par propriété, ou par valeur ?
5. Interface : web (comme Aleph) ou application bureau (comme Maltego) ?

---

## 6. Ce que ce document NE contient pas

- Aucun détail issu d'une analyse du binaire de Maltego.
- Aucun chemin d'endpoint Aleph garanti (à lire sur l'OpenAPI de l'instance).
- Aucune signature de fonction du SDK Maltego garantie (à lire dans la référence d'API).

---

## 7. Sources

**Aleph / OCCRP**
- Documentation Aleph : https://docs.aleph.occrp.org/
- Code Aleph : https://github.com/alephdata/aleph
- alephclient : https://github.com/alephdata/alephclient
- Memorious : https://github.com/alephdata/memorious

**FollowTheMoney**
- Documentation : https://followthemoney.readthedocs.io/
- Code : https://github.com/alephdata/followthemoney

**OpenAleph**
- Documentation : https://openaleph.org/docs/

**Maltego**
- Documentation : https://docs.maltego.com/
- Conditions d'utilisation (EULA) : https://www.maltego.com/eula.html
- SDK Python `maltego-transforms` : voir la section SDK de https://docs.maltego.com/
- Ancien SDK `maltego-trx` : https://github.com/paterva/maltego-trx

> Vérifie chaque URL avant de t'appuyer dessus : les structures de sites documentaires changent.

---

*Fin de source.md. Rédigé par Sednal, conservé ici tel que reçu — Claude n'en a pas changé le contenu technique.*
