# 17 — Les sources à brancher, par ordre d'implémentation

## Ce que ce document corrige

`sources-candidates-21.10.2026.md` (racine du dépôt) liste les sources envisagées, avec un verdict
**à ajouter** / **à surveiller** / **écarté**. Ce verdict n'avait jamais été traduit en consigne de
branchement pour momo — ce document fait ce travail : pour chaque source « à ajouter », son état de clé,
sa priorité, et son rôle probable dans le modèle de grappes (CHERCHER/VÉRIFIER/ENRICHIR/CATALOGUE/OUTIL/
RAPPROCHER).

Croise deux documents déjà écrits, sans rien y changer :
- `sources-candidates-21.10.2026.md` — le choix de chaque source, avec sa justification.
- `cles-api-26.10.2026.md` — l'état réel des clés et comptes au 26/10/2026.

## Avant de commencer : rien ne contrevient à la règle n° 8

Vérifié ligne par ligne : aucune source « à ajouter » ci-dessous n'est un outil de recherche par nom de
personne physique. Les outils qui le sont (Maigret, Xquik, Clearfront, AnySite, les modules personnes de
SpiderFoot) sont déjà dans les listes « Écarté » ou « Non retenu » de `sources-candidates-21.10.2026.md`,
décision du 20/10/2026, antérieure et cohérente avec la règle n° 8 de `00-MAIN.md`. Rien à retirer ici.

Une source enrichit parfois une fiche d'entreprise avec un nom de dirigeant (CompanyScope MCP, via SEC
EDGAR). Ça reste conforme : la règle interdit d'utiliser ce nom comme **clé de rapprochement**, pas de
l'afficher comme propriété d'une fiche d'entreprise. Ne branche pas CompanyScope pour chercher une
personne — seulement pour enrichir une fiche d'entreprise déjà trouvée.

## Priorité

- **P1 — branche maintenant.** Clé déjà obtenue ou aucune clé requise.
- **P2 — branche dès que la clé arrive.** Démarche lancée ou à lancer, voir `cles-api-26.10.2026.md`.
- **P3 — à confirmer sur place avant de brancher.** Un point précis (licence, CGU, chemin d'accès) doit
  être vérifié d'abord — ne code pas le branchement avant.
- **Pas maintenant.** Reporté par une décision déjà prise ; n'y touche pas sans remonter la question.

Le rôle indiqué est une **proposition**, pas une décision : quatre sources (data.europa.eu, org-id.guide,
Wikidata via SPARQL, radio-browser) portent un rôle CATALOGUE ou RAPPROCHER alors que ce rôle était pensé
pour les outils — c'est la question ouverte n° 1 de `14-questions-ouvertes.md`, **toujours pas tranchée**.
Les rôles de ce document suivent l'usage déjà décrit dans `sources-candidates-21.10.2026.md` ; ne les
fige pas dans le code tant que la question n° 1 n'a pas de réponse.

---

## 1. Web

| Source | Clé | Priorité | Rôle proposé |
| :-- | :-- | :-- | :-- |
| Parallel Search MCP | aucune | **P1** | CHERCHER |
| Fetch (MCP officiel) | aucune | **P1** | OUTIL — récupère une page, ne cherche rien |
| Memento TimeTravel | aucune | **P1** | ENRICHIR — versions archivées d'une page déjà trouvée |
| Linkup | obtenue | **P1** | CHERCHER |
| Firecrawl | obtenue | **P1** | CHERCHER + OUTIL (couvre aussi la récupération de page) |
| Serper | obtenue | **P1** | CHERCHER |
| Exa | obtenue | **P1** | CHERCHER |

## 2. Organisations officielles

| Source | Clé | Priorité | Rôle proposé |
| :-- | :-- | :-- | :-- |
| OCDS Data Registry | aucune | **P1** | CHERCHER — marchés publics |
| TED — Search API | aucune | **P1** | CHERCHER — marchés publics UE |
| data.europa.eu (SPARQL) | aucune | **P1** | CATALOGUE *(question n° 1 ouverte)* |
| org-id.guide | aucune | **P1** | CATALOGUE *(question n° 1 ouverte)* |
| Govdirectory | aucune, passe par le SPARQL Wikidata déjà prévu | **P1** | CATALOGUE — rien de neuf à brancher |

## 3. Associations

| Source | Clé | Priorité | Rôle proposé |
| :-- | :-- | :-- | :-- |
| DILA — JOAFE (+ API comptes annuels) | aucune | **P1** | CHERCHER (FR) |
| IRS — BMF / 990 | aucune | **P1** | CHERCHER (US) |
| ProPublica Nonprofit Explorer | aucune | **P1** | CHERCHER + ENRICHIR — finances par année (US) |
| Charities Register NZ (OData) | aucune | **P1** | CHERCHER (NZ) |
| ACNC Charity Register | aucune | **P1** | CHERCHER (AU) |
| CRA — organismes de bienfaisance | aucune | **P1** | CHERCHER (CA) |
| Charities Regulator | aucune | **P1** | CHERCHER (IE) |
| 360Giving GrantNav | aucune | **P1** | ENRICHIR — relie une association à l'argent qu'elle reçoit (UK) |

## 4. Entreprises

| Source | Clé | Priorité | Rôle proposé |
| :-- | :-- | :-- | :-- |
| BODACC | aucune | **P1** | VÉRIFIER — événements (création, radiation, liquidation) sur une entreprise déjà trouvée (FR) |
| info-financière (AMF) | aucune, 10 000 appels/jour par IP | **P1** | ENRICHIR — sociétés cotées (FR) |
| CompanyScope MCP | aucune | **P1** | ENRICHIR uniquement — jamais pour chercher, voir l'avertissement légal ci-dessus |
| Finlande — PRH | aucune | **P1** | CHERCHER (FI) |
| Suisse — Zefix | aucune, **licence à confirmer** | **P3** | CHERCHER (CH) |
| The Gazette (UK) | aucune, **conditions d'API non confirmées** | **P3** | VÉRIFIER — liquidations, faillites (UK) |

## 5. Réseaux sociaux

Tout ce bloc est gratuit, sans clé, première main — les API officielles des plateformes, à utiliser
exactement comme documenté dans `sources-candidates-21.10.2026.md` §5 (recherche d'événements, de
hashtags, de communautés — jamais de compte nommé).

| Source | Clé | Priorité | Rôle proposé |
| :-- | :-- | :-- | :-- |
| Mobilizon | aucune | **P1** | CHERCHER — événements |
| Mastodon — flux RSS | aucune | **P1** | CHERCHER — compte ou hashtag |
| Mastodon — API timelines | aucune | **P1** | CHERCHER — un 401 est un échec de source normal, pas un bug |
| Bluesky — recherche | aucune | **P1** | CHERCHER |
| Bluesky — Jetstream | aucune | **P1** | OUTIL — flux temps réel, filtrage par mot-clé à notre charge |
| Lemmy — `/search` | aucune | **P1** | CHERCHER — communautés |
| PeerTube | aucune | **P1** | CHERCHER |
| MatrixRooms.info | aucune, s'intègre comme moteur SearXNG | **P1** | CHERCHER |

## 6. Lieux

| Source | Clé | Priorité | Rôle proposé |
| :-- | :-- | :-- | :-- |
| OpenAddresses | aucune | **P1** | ENRICHIR — adresses, complète OSM |
| geoBoundaries | aucune | **P1** | CATALOGUE — limites administratives, alimente les champs pays/région |
| Photon | aucune, **politique d'usage de l'instance publique à vérifier avant volume** | **P1** (usage léger) / **P3** (volume) | OUTIL — géocodage |
| university-domains-list | aucune | **P1** | ENRICHIR — nom d'université → domaine web |
| GeoNames | obtenue (nom d'utilisateur, pas une clé) | **P1** | ENRICHIR — variantes de noms |

## 7. Presse

| Source | Clé | Priorité | Rôle proposé |
| :-- | :-- | :-- | :-- |
| radio-browser.info | aucune | **P1** | CATALOGUE *(question n° 1 ouverte)* — annuaire des radios par pays |
| Media Cloud | obtenue | **P1** | CHERCHER + CATALOGUE — articles et annuaire de sources par pays |
| The Guardian Open Platform | obtenue | **P1** | CHERCHER |
| New York Times APIs | obtenue | **P1** | CHERCHER |
| API Radio France | **en attente** de validation manuelle de Radio France | **P3** — et même une fois la clé arrivée, les CGU de stockage ne sont pas confirmées, voir `cles-api-26.10.2026.md` et `14-questions-ouvertes.md` §6 | CHERCHER |

## 8. Personnalisé / outillage

| Source | Clé | Priorité | Rôle proposé |
| :-- | :-- | :-- | :-- |
| Serveurs MCP officiels (Fetch, Filesystem, Git, Time) | aucune | **P1** | OUTIL |
| trafilatura | aucune | **P1** | OUTIL — extraction de texte et métadonnées |
| news-please | aucune | **P1** | OUTIL — crawler + extracteur presse |
| RSSHub / RSS-Bridge | aucune | **P1** | OUTIL — fabrique un flux RSS pour un site qui n'en a pas |
| changedetection.io | aucune | **P1** | OUTIL — surveille une page, en sort du RSS |

---

## Pas maintenant — n'y touche pas sans remonter la question

- **yente** (OpenSanctions auto-hébergé) et **Aleph** (OCCRP) : la question du disque (81 Go restants
  pour deux candidats qui en demandent plus à eux deux) n'est pas arbitrée — `14-questions-ouvertes.md`
  §5.
- **Wikimedia Enterprise, DATAtourisme, Geoapify, LocationIQ, OpenCage** : retenus en secours seulement,
  comptes à ne créer que si on tranche dans ce sens — voir `cles-api-26.10.2026.md` §4.
- **Danemark (CVR / Virk)** : chemin d'accès Datafordeler pas clair, vérification de 10 min à faire avant
  toute décision.
- **OpenRegistry / Registry Lookup (Veridion)** : relais tiers, à n'utiliser que quand aucun registre
  direct n'existe pour un pays, et toujours marqués seconde main (fiabilité D ou E, jamais mieux).
- **SpiderFoot, Fylings MCP** : reportés le 21/10, pour des raisons propres à chacun — voir
  `sources-candidates-21.10.2026.md` §8.

## Où regarder

- `sources-candidates-21.10.2026.md` — le choix et sa justification, source par source.
- `cles-api-26.10.2026.md` — l'état réel des clés, mis à jour au fil de l'eau.
- `05-reglages-sources.md` — comment une source s'inscrit dans la fiche (catégorie, rôle, fiabilité,
  langue, quota).
- `14-questions-ouvertes.md` §1 — la question du rôle CATALOGUE/RAPPROCHER sur une source, qui conditionne
  le rôle final de 4 sources de ce document.
