# 15 — Mécanismes existants à reprendre

Recherche du 26/10/2026. Complète `source.md` (Aleph, FtM, Maltego) sur ce qu'il ne couvre pas : le
rapprochement d'entités proprement dit, la méthode d'évaluation des sources, la traçabilité, le cadre
légal français, et ce qui éviterait de recoder des briques existantes.

Principe appliqué : **ne rien réinventer**. Chaque ligne ci-dessous nomme un outil, une norme ou une
méthode documentés, avec ce qu'ils apportent et leurs limites.

---

## 1. Le rapprochement d'entités — le trou du projet

La tuile « Fusion / doublons » a aujourd'hui pour règle « même entité si nom et ville identiques ».
C'est une correspondance exacte, et elle ne marchera pas : `Club de judo de Grenoble`,
`CLUB JUDO GRENOBLE` et `Judo Club Grenoblois` sont la même association et ne se ressemblent pas pour
une machine.

Le domaine s'appelle **record linkage** et il est travaillé depuis 1969 (modèle Fellegi-Sunter). Il ne
faut rien inventer ici.

### Splink — la recommandation

Développé par le ministère de la Justice britannique. **Licence MIT**, Python.

| Pourquoi lui | Détail |
| :-- | :-- |
| Modèle probabiliste Fellegi-Sunter | Méthode de référence du domaine, pas une heuristique maison |
| **Pas de données d'entraînement étiquetées** | Le modèle s'entraîne sans supervision — décisif pour un projet solo |
| Tourne en local sur DuckDB | Pas d'infrastructure lourde ; Spark seulement au-delà de ~100 millions d'enregistrements |
| Diagnostics lisibles | On voit *pourquoi* deux fiches ont été rapprochées, et avec quel score |

Ce dernier point compte plus que tout le reste pour grappes : un rapprochement non explicable est un
rapprochement non vérifiable, donc inutilisable selon la règle n° 1 du projet.

### Les autres, et pourquoi pas eux

**dedupe** (Python) — apprentissage actif : un humain étiquette des paires, le modèle apprend. Bon
principe, mais demande ce travail d'étiquetage au départ, et ne tient que des volumes petits à moyens.

**Zingg** — demande Spark 3.5. Trop lourd pour la VM.

**Python Record Linkage Toolkit** — boîte à outils pédagogique, pas un moteur de production.

### yente / OpenSanctions — à bien cadrer

Déjà prévu sur la VM (60 Go). **Attention à ce qu'il est** : un moteur de correspondance spécialisé
**sanctions et personnes politiquement exposées**, pas un moteur de rapprochement généraliste. On lui
envoie une entité modèle (schéma + propriétés), il renvoie des candidats classés.

Trois choses à savoir :

- Leur propre documentation dit de traiter une correspondance comme **une piste, pas une alerte**, et de
  prévoir une revue humaine. C'est exactement le patron à deux étages d'Aleph.
- Les données PEP contiennent beaucoup de noms courants : **les fausses correspondances sont fréquentes**.
  Filtrer les sources et ajuster les seuils est obligatoire, pas optionnel.
- **L'usage libre est réservé au non-commercial.** Un usage professionnel demande une licence de données.
  À vérifier selon ce que devient grappes.

**Conclusion** : Splink pour le rapprochement général entre sources, yente en plus si et seulement si le
recoupement sanctions/PEP fait partie du besoin. Ce ne sont pas des concurrents.

### Le patron à reprendre, quel que soit l'outil

Celui d'Aleph (§2.5 de `source.md`), confirmé par OpenSanctions :

1. **Rappel large** — générer des candidats par empreintes de noms normalisés. On accepte du bruit.
2. **Précision par score** — classer les candidats. On garde un score, pas un oui/non.
3. **Validation humaine** — l'utilisateur confirme ou rejette. Les décisions sont conservées.

Dans grappes, l'étage 3 n'existe pas encore dans la maquette. **Il manque un écran de validation des
rapprochements.** C'est probablement l'onglet *Tri*, qui n'a pas de spécification — à soumettre à Sednal.

---

## 2. Coter les sources : le code Admiralty

grappes a aujourd'hui un champ « Origine de l'information : première main / seconde main ». C'est une
intuition juste, mais informelle. Il existe une norme pour ça, utilisée par l'OTAN et les services de
renseignement : le **code Admiralty**, aussi appelé système OTAN 6×6.

Il **sépare deux choses que grappes confond** :

**La fiabilité de la source**, de A à F — une propriété de la source, stable dans le temps :

| | |
| :-- | :-- |
| **A** | Totalement fiable. Aucun doute, historique de fiabilité complète |
| **B** | Habituellement fiable. Doutes mineurs |
| **C** | Assez fiable. Des doutes, mais a déjà fourni de l'information valide |
| **D** | Habituellement non fiable |
| **E** | Non fiable |
| **F** | Non évaluable — aucune base pour juger |

**La crédibilité de l'information**, de 1 à 6 — une propriété de *chaque fiche*, pas de la source :

| | |
| :-- | :-- |
| **1** | Confirmée par d'autres sources indépendantes |
| **2** | Probablement vraie. Non confirmée mais cohérente |
| **3** | Possiblement vraie. Concorde avec une partie du reste |
| **4** | Douteuse. Pas d'élément de confirmation |
| **5** | Improbable. Contredite par le reste |
| **6** | Non évaluable |

Noté en deux caractères : `B2` = source habituellement fiable, information probablement vraie.

**Ce que ça change pour grappes** : les deux axes s'évaluent **séparément**. Une source excellente peut
renvoyer une information douteuse, et une source médiocre une information confirmée par ailleurs. Le
champ actuel, à un seul axe, ne permet pas de dire ça.

Proposition : remplacer « Origine de l'information » par une **cote de fiabilité A–F sur la fiche
source**, et calculer une **cote de crédibilité 1–6 sur chaque fiche de grappe**, où le chiffre vient du
nombre de sources indépendantes qui concordent. Le rôle VÉRIFIER devient alors mesurable au lieu d'être
une intention.

**Piège à éviter, documenté** : deux sources qui concordent ne sont indépendantes que si elles ne se
recopient pas l'une l'autre. En open data, c'est fréquent — plusieurs annuaires reprennent le même
registre. Une cote `1` ne doit pas être attribuée à deux sources qui dérivent du même original.

---

## 3. La méthode : le Protocole de Berkeley

Le **Berkeley Protocol on Digital Open Source Investigations**, publié par le Haut-Commissariat des
Nations unies aux droits de l'homme, est le document de référence sur la conduite d'enquêtes en sources
ouvertes destinées à servir de preuve.

Ce n'est pas un outil, c'est une méthode : comment collecter, vérifier, conserver et documenter une
information de source ouverte pour qu'elle tienne devant un tiers.

À lire par Sednal plus que par l'agent. Il donne le cadre que grappes cherche à outiller, et il est
gratuit.

---

## 4. La traçabilité : PROV-O

grappes a pour règle n° 1 de garder l'original et de savoir d'où vient chaque information. Le W3C a
normalisé ce modèle : **PROV-O**, recommandation depuis 2013.

Trois concepts : une **entité** (la donnée), une **activité** (ce qui l'a produite), un **agent** (qui
en est responsable). Et les relations entre eux : *a été généré par*, *a utilisé*, *a été attribué à*,
*dérive de*.

Appliqué à grappes : une fiche *a été générée par* l'appel à DILA—JOAFE du 26/10 à 14 h 52, qui *a
utilisé* la requête traduite, qui *dérive de* la saisie de l'utilisateur. La marque « IA » devient un cas
particulier de ce modèle, pas un bricolage à part.

Même sans adopter le format RDF, **reprendre le vocabulaire** évite d'inventer des noms de champs qui
voudront dire autre chose dans six mois.

---

## 5. Ne pas recoder le canevas

Le plan de travail libre (`08`) est la pièce la plus lourde de la spécification. **Il existe en
bibliothèque.**

**React Flow** (paquet `@xyflow/react`), licence MIT. C'est la bibliothèque qui fait tourner le canevas
de nombreux outils du genre : nœuds déplaçables, ports, liens en courbes, sélection, zoom, mise en page
automatique. Variante **Svelte Flow** (`@xyflow/svelte`) si le front n'est pas en React.

Tout ce que décrit `08-plan-de-travail.md` — glisser une tuile, tirer un lien depuis un port, cliquer un
lien pour le sélectionner, ranger automatiquement — est fourni. Ce qui reste à écrire est le contenu des
tuiles et les règles métier, c'est-à-dire la partie qui appartient à grappes.

**Estimation honnête** : recoder ça à la main représente des semaines, pour un résultat moins robuste.

---

## 6. Les briques pour la tuile Traduction

**Ne pas traduire les noms propres** (`09`) demande de les reconnaître d'abord. C'est de la
reconnaissance d'entités nommées.

**GLiNER** — modèle généraliste, multilingue, qui reconnaît des types d'entités donnés en langage
naturel, sans réentraînement. Léger, publié avec son article de recherche. C'est l'option à essayer en
premier : on lui demande « personnes, organisations, lieux », il les marque, on les protège avant de
traduire.

**spaCy** reste la valeur sûre si GLiNER déçoit : modèles français disponibles, plus ancien, plus prévisible.

**La translittération** (question ouverte n° 2) : ne pas écrire de table maison. `iuliia` pour le
cyrillique implémente une vingtaine de normes officielles distinctes — et c'est bien le problème : il
existe plusieurs romanisations valides du même nom. Pour une recherche, il faut souvent **chercher
plusieurs variantes à la fois**, exactement comme pour les langues multiples de la tuile Traduction.

---

## 7. Sources françaises à brancher en priorité

**API Recherche d'entreprises** — `https://recherche-entreprises.api.gouv.fr`

| | |
| :-- | :-- |
| Clé | **aucune**, accès totalement ouvert |
| Débit | 7 requêtes par seconde |
| Contenu | Entreprises, SIREN/SIRET, codes NAF, **dirigeants et élus** |
| Licence | Licence Ouverte 2.0 |

C'est la meilleure source française gratuite pour le rôle CHERCHER sur les entreprises, et elle demande
zéro démarche. À brancher avant les sources payantes.

**À ne pas confondre avec API Entreprise** (`entreprise.api.gouv.fr`), qui est réservée aux
administrations et organismes habilités, sur demande motivée. Le catalogue DJEPVA des données
associatives passe par celle-là — donc **pas accessible librement**. Pour les associations, rester sur
le Journal officiel des associations (DILA — JOAFE), déjà dans la configuration.

---

## 8. Le cadre légal — à lire avant d'écrire du code

**C'est la partie la plus importante de ce document.**

La CNIL a publié en juin 2024 des recommandations sur la réutilisation de données publiées sur Internet.
Plusieurs points touchent grappes directement.

### Ce qui va bien

- Réutiliser de l'open data pour une finalité licite relève en général de l'**intérêt légitime**.
- La CNIL dit de **préférer les API au moissonnage** — c'est déjà l'architecture de grappes.

### Ce qui pose problème

> **« Compiler des informations en ligne pour constituer des profils de personnes nommément désignées
> ne relève pas de l'intérêt légitime. Le consentement est nécessaire. »**

C'est, formulé autrement, une partie de ce que fait grappes. La CNIL cite explicitement comme exemple
les sites qui agrègent photos, publications et CV de plusieurs réseaux et blogs pour en faire un profil.

**La distinction qui sauve le projet** : le RGPD protège les **personnes physiques**, pas les personnes
morales. Chercher une **association** ou une **entreprise** — ce que grappes fait aujourd'hui — est hors
du champ. Chercher **une personne nommée** y entre de plein fouet.

Mais la frontière est poreuse : un dirigeant d'entreprise, un président d'association sont des personnes
physiques, et l'API Recherche d'entreprises renvoie justement les dirigeants.

### La décision à prendre, explicitement

**Proposition à soumettre à Sednal** : écrire noir sur blanc que grappes a pour objet les **personnes
morales** — associations, entreprises, organisations — et pas les personnes physiques. Puis l'appliquer
dans le code : les données de dirigeants sont affichées quand la source les renvoie, mais **ne servent
jamais de clé de rapprochement**, et on ne construit pas de fiche par personne.

Sans cette limite écrite, grappes est juridiquement un outil de profilage de personnes, et le reste des
précautions ne compense pas.

### Les autres obligations, si des personnes physiques entrent dans le périmètre

- **Information des personnes** (article 14 du RGPD) : identité du responsable, finalité, base légale,
  catégories de données, destinataires, durée de conservation, **sources**, et les droits. Des exceptions
  existent (effort disproportionné) mais doivent être **documentées**, et une information générale
  publique reste due.
- **Analyse d'impact (AIPD)** attendue dès que l'agrégation est en jeu.
- **Données sensibles** : interdites par principe. L'exception « données manifestement rendues publiques
  par la personne » est interprétée strictement par la Cour de justice de l'Union européenne, et ne
  couvre jamais les données concernant des tiers.
- **Exactitude et durée de conservation** : la CNIL insiste sur le fait qu'une donnée périmée cause un
  préjudice réel. Grappes doit dater chaque collecte et savoir purger.

---

## 9. Récapitulatif : quoi reprendre, pour quoi

| Besoin de grappes | Mécanisme existant | Statut |
| :-- | :-- | :-- |
| Rapprocher des fiches de sources différentes | **Splink** (MIT) | à adopter |
| Recoupement sanctions / PEP | yente | optionnel, non commercial |
| Patron de rapprochement | Rappel large → score → validation humaine | à adopter |
| Coter une source et une information | **Code Admiralty** A–F × 1–6 | remplace « origine de l'information » |
| Méthode d'enquête et de vérification | Protocole de Berkeley (ONU) | à lire |
| Tracer l'origine de chaque donnée | Vocabulaire **PROV-O** (W3C) | à reprendre |
| Canevas de tuiles et de liens | **React Flow** (MIT) | évite des semaines |
| Protéger les noms propres en traduction | GLiNER, ou spaCy | à essayer |
| Translittération | `iuliia` et normes ICU | quand ce sera d'actualité |
| Entreprises françaises | API Recherche d'entreprises, sans clé | à brancher en priorité |
| Cadre légal | Recommandations CNIL de juin 2024 | **décision requise, voir §8** |

---

## 10. Les trois points à trancher par Sednal

1. **Le périmètre légal** (§8) — grappes vise-t-il les personnes morales uniquement ? À écrire dans
   `00-MAIN.md` comme huitième règle non négociable si oui.
2. **Le code Admiralty** (§2) — remplace-t-il le champ « Origine de l'information » ?
3. **L'écran de validation des rapprochements** (§1) — est-ce l'onglet *Tri* ?

---

## 11. Liens

**Rapprochement d'entités**
- Splink : https://moj-analytical-services.github.io/splink/
- dedupe : https://github.com/dedupeio/dedupe
- OpenSanctions, API de correspondance : https://www.opensanctions.org/docs/api/matching/
- OpenSanctions, réglage du score : https://www.opensanctions.org/docs/api/tuning/

**Méthode et normes**
- Protocole de Berkeley (PDF, ONU) : https://unipd-centrodirittiumani.it/public/docs/OHCHR_BerkeleyProtocol.pdf
- Code Admiralty : https://en.wikipedia.org/wiki/Admiralty_code
- PROV-O (W3C) : https://www.w3.org/TR/prov-o/

**Briques techniques**
- React Flow : https://www.reactflow.dev
- Svelte Flow : https://svelteflow.dev
- GLiNER : https://pypi.org/project/gliner/
- iuliia (translittération) : https://pypi.org/project/iuliia/

**Sources françaises**
- API Recherche d'entreprises : https://www.data.gouv.fr/dataservices/api-recherche-dentreprises
- API Entreprise (accès restreint) : https://entreprise.api.gouv.fr/catalogue

**Cadre légal**
- CNIL, recommandations réutilisateurs (PDF, juin 2024) : https://www.cnil.fr/sites/default/files/2024-06/recommandations_reutilisateurs_donnees_publiees_sur_internet.pdf
