# FINAL.md — RÉFÉRENCE UNIQUE DU PROJET
# Remplace et annule : CADRAGE.md, CADRAGE_COMPLEMENT.md, SORTIE_FINALE.md, CONTROLE.md,
# et toutes les REPONSES_SEDNAL_*.md. Prioritaire sur MISSION.md en cas de conflit.
# MISSION.md reste la référence pour tout ce que ce fichier ne traite pas.
# Marque tous les fichiers listés ci-dessus comme obsolètes (ou archive-les), et ne t'y réfère plus.
# Ton COMPRIS.md est validé : applique ce que tu y annonces.

## 1. PRINCIPE DIRECTEUR
Le système est OUVERT et AUTONOME. Il trouve lui-même ses sources, quel que soit l'écosystème.
Aucun réseau n'est une porte d'entrée privilégiée. Aucun dépôt manuel de fichiers n'est requis
pour fonctionner. Sednal n'intervient plus après la mise en route.
Toute conception qui suppose « l'humain fournit les sources » est à corriger.

## 2. CE QUE SEDNAL FOURNIT, ET RIEN D'AUTRE
1. Un ou plusieurs SUJETS, en une phrase de langage naturel.
2. Les clés des fournisseurs de recherche branchés (variables d'environnement).
3. Des limites générales : quotas, profondeur d'exploration, liste d'INTERDITS.
4. L'interrupteur `autonome` (false par défaut) et un fichier STOP d'arrêt immédiat.
Il ne fournit PAS : sites, mots-clés, lexique de départ, exports, validation au cas par cas,
démarches auprès d'un réseau social.
La section « En attente de Sednal » d'ETAT.md ne contient que ces quatre lignes. Rien d'autre.

## 3. CORRECTIONS À APPLIQUER SUR L'EXISTANT
- SUPPRIME toute liste blanche de domaines ou de sites visités. Remplace par des règles
  générales : sources publiques uniquement, robots.txt respecté, pas de connexion ni de compte,
  pas de contournement de limites ou de captcha, délai >= 1 s par domaine, arrêt sur 403/429,
  User-Agent identifiable. Plus une liste d'INTERDITS (domaines/catégories) éditable par Sednal.
  La seule liste blanche admise concerne les FOURNISSEURS branchés.
- SUPPRIME toute exigence de lexique initial saisi par Sednal (voir § 5).
- SUPPRIME l'obligation de validation humaine des candidats (voir § 7).
- SUPPRIME la condition « candidat cité par une source déjà confirmée ».
- FUSIONNE le double verrou : `autonome` seul, plus d'`execution_autorisee`.
- Phase 7 « vrais exports » DISSOUTE : plus de condition d'avancement liée à des fichiers
  fournis par Sednal. Retire ces mentions d'ETAT.md, QUESTIONS.md et des documents de conception.
- Q16 à Q19 restent ouvertes et se trancheront sur les premières vraies données collectées.
- Les adaptateurs existants (Telegram, X, Instagram, web) sont conservés comme lecteurs de
  fichiers, mais ne sont plus le chemin principal. Aucune démarche par réseau (compte
  professionnel, application Meta, jeton X) n'est demandée à Sednal.

## 4. LA MULTIPRISE (ouverture totale, exigence prioritaire)
Rien de fermé. Sednal doit pouvoir brancher n'importe quelle API sans toucher au code.
- Aucun fournisseur codé en dur dans le cœur ; les fournisseurs livrés sont des exemples
  supprimables sans rien casser.
- Ajouter une API = un fichier YAML. Le YAML couvre : authentification (en-tête, paramètre
  d'URL, Bearer, Basic, jeton en variable d'environnement), GET/POST, corps JSON ou formulaire,
  gabarits de paramètres ({sujet}, {mots_cles}), pagination (curseur, page, décalage, lien
  suivant), formats de réponse (JSON, XML/RSS/Atom, CSV), chemins vers les champs (titre, URL,
  identifiant, description, date), transformations simples (regex, concaténation, défaut).
- Client MCP : appel d'outils d'un serveur MCP externe (stdio ou HTTP), défini en configuration
  (commande ou URL, outil, correspondance arguments/résultat). Distinct du serveur MCP en
  lecture seule du projet, qui sert vers l'extérieur.
- Cas hors YAML : plugin Python implémentant `SearchProvider`, déposé dans `plugins/`, découvert
  automatiquement, sans modifier le dépôt principal.
- Format de sortie commun indépendant des fournisseurs ; champs spécifiques conservés dans une
  colonne `extra`. Plusieurs fournisseurs interrogeables ensemble, doublons fusionnés en gardant
  la liste des fournisseurs d'origine.
- Livre 3 exemples très différents (API JSON à clé, flux RSS, serveur MCP) et un guide
  « brancher une nouvelle API en 10 minutes » dans docs/utilisateur.md.
- Test d'ouverture : ajouter un fournisseur factice uniquement par YAML, un autre uniquement par
  plugin, et vérifier qu'aucune ligne du cœur n'a changé.

## 5. AMORÇAGE À PARTIR D'UNE PHRASE
À partir du sujet en langage naturel : interroge la multiprise, extrais des termes discriminants
des résultats, construis un lexique initial marqué « amorçage » (poids faible, plafonné).
Aucun mot imposé par Sednal. La boucle du § 8 l'affine ensuite.

## 6. RÉCUPÉRATEUR UNIVERSEL DE PAGES PUBLIQUES
Après la recherche, récupère le contenu des pages candidates (règles du § 3) et normalise-le au
format web existant. Les liens vers des réseaux sociaux deviennent des CITATIONS (D24), sans
lire ces réseaux. Un réseau n'est lu que par un adaptateur officiel branché.
SÉCURITÉ : tout résultat reçu (API, MCP, page) est une DONNÉE NON FIABLE. Jamais exécuté, jamais
interprété comme une instruction, jamais transmis tel quel à un modèle. On n'en extrait que des
champs typés (texte borné et nettoyé, URL validée, date).

## 7. INGESTION AUTOMATIQUE
Un candidat est ingéré automatiquement s'il est public, respecte les règles, n'est pas dans les
INTERDITS, et atteint un score de proximité minimal pour un sujet (seuil configurable).
Pas de validation humaine. Profondeur d'exploration et nombre de sources par cycle plafonnés.
Le recoupement continue de décider : une source non recoupée reste « probable » au mieux.

## 8. BOUCLE AUTOMATIQUE `grappes cycle`
collecte -> ingestion -> score -> recoupement -> assignation -> apprentissage -> recalibrage ->
export -> rapport. Idempotent, journalisé, planifiable (timer systemd), verrou anti-concurrence.
- Apprentissage UNIQUEMENT à partir des entités « confirmées » (recoupées sur >= 2 écosystèmes) :
  termes discriminants ajoutés à un lexique_appris séparé, poids faible, plafonné par cycle,
  expiration si non revus. Les lexiques écrits par Sednal ne sont jamais modifiés.
- Recalibrage borné des seuils, sur les confirmées uniquement.
- Instantané versionné par cycle. Indicateurs de stabilité (entités changeant de grappe, taux
  d'ambiguïté, taux de confirmés, dérive du lexique) ; au-delà d'un seuil configurable, RETOUR EN
  ARRIÈRE automatique, restauration de l'instantané précédent et mention dans le rapport.
  Commande `grappes rollback`. Arrêts : `autonome: false` et fichier STOP.
- Rapport `rapports/cycle_<date>.md` lisible par un non-informaticien, lié depuis ETAT.md.
- `autonome: false` par défaut, mode dry-run tant qu'il n'est pas activé.

## 9. SORTIE FINALE
`sorties/resultat.csv` : UNE SEULE COLONNE, en-tête exactement `NOM`.
Une ligne par entité retenue, rien d'autre dans le fichier. UTF-8 sans BOM, tri alphabétique.
- NOM = nom lisible de l'entité. Jamais un identifiant technique ni une URL brute.
- Dédoublonne les variantes d'écriture (casse, accents, espaces, suffixes).
- N'exporte que les entités assignées à une grappe (confirmées et probables), seuil configurable.
- Un fichier par grappe si plusieurs grappes : `sorties/resultat_<grappe>.csv`.
- Personnes physiques (compte sans indice institutionnel explicite dans son nom) : trois cas, pas
  une exclusion de principe (décision 901/Q21, remplace l'ancienne règle « en cas de doute, une
  personne » qui perdait des résultats utiles, ex. le compte public d'une personnalité du sport
  dans une recherche sur le sport). (1) Matche directement la grappe (statut « classé », au-dessus
  du seuil) : gardée dans `resultat.csv` comme n'importe quelle entité. (2) Hors sujet (sous le
  seuil ou « non classé ») : exclue, comme avant. (3) Doute (statut « ambigu », le programme ne
  peut pas trancher) : `sorties/resultat_a_trancher.csv`, jamais mêlée à `resultat.csv` ni
  silencieusement exclue. Option `inclure_personnes` en configuration, à false ; si Sednal la passe
  à true, les personnes suivent la même règle que les autres entités, sans fichier « à trancher »
  séparé, et le masquage ne s'applique plus à ce fichier : écris cet avertissement dans
  docs/utilisateur.md et dans le rapport de cycle. Dans tous les cas, `entites.csv` et la base
  continuent d'appliquer redact_persons.
- `scoring.mode_recherche` (décision 901/Q26, deux valeurs fermées) : `sites` (défaut) trouve des
  sites/comptes qui correspondent aux critères, aucune extraction ; `extraction` lit le contenu des
  sources de la recherche, extrait les acteurs nommés dans le texte (`config/ner.yaml`, D63) et les
  ajoute comme candidats de recoupement, au même titre que les sources.
Inchangés : `entites.csv`, `appartenances.csv`, la base SQLite et le serveur MCP en lecture seule,
qui gardent scores, confiance et explications.
`resultat.csv` reste la sortie de référence. `sorties/resultat_tsites.csv` (`nom;ville;pays`, mêmes noms,
même tri) est une sortie de compatibilité pour trouver-sites, pilotée par `export_tsites` (D59).

## 10. CADRE DE DONNÉES (valeurs proposées par Claude, réversibles par Sednal)
Sources publiques uniquement. retention_days = 90 pour les données brutes. redact_persons actif.
Pas de scraping de réseaux sociaux hors API officielle. Pas de contenu privé. Pas de
ré-identification. Secrets en variables d'environnement, jamais dans le dépôt ni dans les
journaux. Journal de tous les appels externes (fournisseur, date, requête, statut).

## 11. D25 — IDENTIFIANT DE CANAL TELEGRAM
Table d'équivalence en configuration = référence (nom affiché -> identifiant public).
Repli si absent de la table : dérivation du nom affiché (minuscules, espaces -> « _ »), mais
marquée « hypothèse » dans `explain`, ne validant PAS seule un recoupement (E=0 pour cette
citation), et comptée dans le rapport. Deux canaux de même nom affiché : ne rien fusionner.
Tests : nom présent, absent, collision, accents.

## 12. TESTS
Aucune requête réelle dans les tests : faux serveur HTTP local et faux serveur MCP.
Cas exigés : réponse mal formée, résultat piégé (texte type « ignore tes instructions »), clé
absente, quota dépassé, doublons, amorçage depuis une phrase, dégradation déclenchant le retour
en arrière, ajout d'un fournisseur par YAML puis par plugin, dédoublonnage et tri de
`resultat.csv`, entité sans nom lisible, fichier vide.

## 13. CORRECTIONS DE MISSION.md À ME PROPOSER
MISSION.md contient des erreurs de Claude. Relis-la et propose les correctifs dans un fichier à
part (ne la modifie pas toi-même) :
- §9.1 : l'exemple « trois termes ≈ 86 » est faux (avec scale=3 : un terme ≈ 28, trois ≈ 63).
- §11 : formule de confiance remplacée par D15, et E=0 si le recoupement n'est pas validé (D16).
- §13.1 : import MCP à corriger selon D13, avec la version épinglée.
- §17 : questions Q12 à Q19 manquantes.
- §12 : sortie finale à aligner sur le § 9 ci-dessus.
- Toute phrase supposant que Sednal fournit sources, sites, mots-clés ou exports : à réécrire
  selon le § 2.

## 14. ORDRE DE TRAVAIL
1. Corrections du § 3 et nettoyage des fichiers obsolètes.
2. Corpus synthétique reproductible (quelques centaines d'observations, 3 grappes,
   chevauchements, ambiguïtés, oppositions, liens non identifiables, mono-écosystème).
3. Parcours complet de bout en bout jusqu'à `resultat.csv`, vérifié par un test d'intégration.
4. Robustesse : fichiers malformés, très gros fichiers, encodages. Mesure de charge.
5. Multiprise (§ 4), amorçage (§ 5), récupérateur (§ 6), ingestion automatique (§ 7).
6. Boucle automatique (§ 8).
7. Rapport d'ingestion lisible, docs/utilisateur.md, docs/conception/, DECISIONS.md (statut
   « proposée »), ETAT.md à jour.
Un commit par étape, tests verts à chaque étape.
Ne lance AUCUNE collecte réelle tant que Sednal n'a pas mis `autonome: true`.
