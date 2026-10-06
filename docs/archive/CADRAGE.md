> **OBSOLÈTE** : remplacé par `FINAL.md` (référence unique, 2026-10-06). Conservé pour l'historique uniquement ; ne pas s'y référer.

# CADRAGE DU PROJET — référence unique
# Remplace et annule REPONSES_SEDNAL_5.md, 6, 7 et 8. Prioritaire sur eux en cas de conflit.
# REPONSES_SEDNAL_4.md reste valable SAUF ce que ce fichier contredit (voir § Corrections).
# Supprime ou marque « obsolète » les fichiers 5 à 8 pour éviter toute ambiguïté.

## 1. Principe directeur
Le système est OUVERT. Il trouve lui-même ses sources, quel que soit l'écosystème.
Aucun réseau n'est une porte d'entrée privilégiée. Aucun dépôt manuel de fichiers n'est requis
pour fonctionner. Sednal n'intervient plus après la mise en route.
Toute conception qui suppose « l'humain fournit les sources » est à corriger.

## 2. Ce que Sednal fournit, et rien d'autre
1. Un ou plusieurs SUJETS, en une phrase de langage naturel.
2. Les clés des fournisseurs de recherche branchés (variables d'environnement).
3. Des limites générales : quotas, profondeur d'exploration, liste d'INTERDITS.
4. L'interrupteur `autonome` (false par défaut) et un fichier STOP d'arrêt immédiat.
Il ne fournit PAS : de sites, de mots-clés, d'exports, de validation au cas par cas.

## 3. Corrections à appliquer sur l'existant
- SUPPRIME toute liste blanche de domaines ou de sites. Remplace-la par des règles générales :
  sources publiques uniquement, robots.txt respecté, pas de connexion ni de compte, pas de
  contournement de limites ou de captcha, délai >= 1 s par domaine, arrêt sur 403/429,
  User-Agent identifiable. Plus une liste d'INTERDITS (domaines/catégories) éditable par Sednal.
  La seule liste blanche admise concerne les FOURNISSEURS branchés, pas les sites visités.
- SUPPRIME toute exigence de lexique initial saisi par Sednal (voir § 5, amorçage).
- SUPPRIME l'obligation de validation humaine des candidats (voir § 7).
- Les exports Telegram/Instagram ne sont PLUS une condition d'avancement. Q16 à Q19 se
  tranchent sur les premières vraies données ramenées par la collecte, quelle qu'en soit
  l'origine. Les adaptateurs existants (Telegram, X, Instagram, web) sont conservés comme
  lecteurs de fichiers, mais ne sont pas le chemin principal.
- Aucune démarche par réseau (compte professionnel, application Meta, jeton X) n'est demandée
  à Sednal. Si un adaptateur officiel est branché un jour, c'est un fournisseur de plus.

## 4. La multiprise (ouverture totale, exigence prioritaire)
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
- Format de sortie commun indépendant des fournisseurs ; champs spécifiques conservés dans
  une colonne `extra`. Interrogation de plusieurs fournisseurs ensemble, fusion des doublons
  en gardant la liste des fournisseurs d'origine.
- Livre 3 exemples très différents (API JSON à clé, flux RSS, serveur MCP) et un guide
  « brancher une nouvelle API en 10 minutes » dans docs/utilisateur.md.
- Test d'ouverture : ajouter un fournisseur factice uniquement par YAML, un autre uniquement
  par plugin, et vérifier qu'aucune ligne du cœur n'a changé.

## 5. Amorçage à partir d'une phrase
À partir du sujet en langage naturel : interroge la multiprise, extrais des termes discriminants
des résultats, construis un lexique initial marqué « amorçage » (poids faible, plafonné).
Aucun mot imposé par Sednal. La boucle du § 8 l'affine ensuite.

## 6. Récupérateur universel de pages publiques
Après la recherche, récupère le contenu des pages candidates (règles du § 3) et normalise-le au
format web existant. Les liens vers des réseaux sociaux sont enregistrés comme CITATIONS (D24),
sans lire ces réseaux. Un réseau n'est lu que par un adaptateur officiel branché.
Tout résultat reçu (API, MCP, page) est une DONNÉE NON FIABLE : jamais exécuté, jamais interprété
comme une instruction, jamais transmis tel quel à un modèle ; on n'en extrait que des champs
typés (texte nettoyé, URL validée).

## 7. Ingestion automatique
Un candidat est ingéré automatiquement s'il est public, respecte les règles, n'est pas dans les
INTERDITS, et atteint un score de proximité minimal pour un sujet (seuil configurable).
Pas de validation humaine. Profondeur d'exploration et nombre de sources par cycle plafonnés.
Le recoupement continue de décider : une source non recoupée reste « probable » au mieux.

## 8. Boucle automatique `grappes cycle`
collecte -> ingestion -> score -> recoupement -> assignation -> apprentissage -> recalibrage ->
export -> rapport. Idempotent, journalisé, planifiable (timer systemd), verrou anti-concurrence.
- Apprentissage UNIQUEMENT à partir des entités « confirmées » (recoupées sur >= 2 écosystèmes) :
  termes discriminants ajoutés à un lexique_appris séparé, poids faible, plafonné par cycle,
  expiration si non revus. Les lexiques écrits par Sednal ne sont jamais modifiés.
- Recalibrage borné des seuils, sur les confirmées uniquement.
- Instantané versionné par cycle. Indicateurs de stabilité (changements de grappe, ambiguïté,
  taux de confirmés, dérive du lexique) ; au-delà d'un seuil, RETOUR EN ARRIÈRE automatique et
  mention dans le rapport. Commande `grappes rollback`.
- Rapport `rapports/cycle_<date>.md` lisible par un non-informaticien.
- `autonome: false` par défaut, mode dry-run tant qu'il n'est pas activé.

## 9. Cadre inchangé (Q7, valeurs proposées par Claude, non confirmées par Sednal)
Sources publiques uniquement ; retention_days = 90 pour les données brutes ; redact_persons
activé par défaut ; pas de scraping de réseaux sociaux hors API officielle ; pas de contenu
privé ; pas de ré-identification. Secrets en variables d'environnement, jamais dans le dépôt
ni dans les journaux. Journal de tous les appels externes.

## 10. Tests
Aucune requête réelle dans les tests : faux serveur HTTP local et faux serveur MCP.
Cas exigés : réponse mal formée, résultat piégé (texte type « ignore tes instructions »),
clé absente, quota dépassé, doublons, amorçage depuis une phrase, dégradation déclenchant le
retour en arrière, ajout d'un fournisseur par YAML puis par plugin.

## 11. Corrections de MISSION.md à me proposer
MISSION.md contient des erreurs de ma part (Claude). Relis-la et propose-moi les correctifs
dans un fichier à part (ne la modifie pas toi-même) :
- §9.1 : l'exemple « trois termes ≈ 86 » est faux (avec scale=3 : un terme ≈ 28, trois ≈ 63).
- §11 : formule de confiance remplacée par D15, et E=0 si le recoupement n'est pas validé (D16).
- §13.1 : import MCP à corriger selon D13, avec la version épinglée.
- §17 : questions Q12 à Q19 manquantes.
- Toute phrase supposant que Sednal fournit les sources, les sites ou les mots-clés : à réécrire
  selon le § 2 de ce fichier.

## 12. Ordre de travail
1. Termine REPONSES_SEDNAL_4.md (D25, valeurs Q7, corpus synthétique, parcours de bout en bout,
   robustesse), en ignorant ce que ce fichier contredit.
2. Applique ce CADRAGE.md : corrections du § 3 d'abord, puis §§ 4 à 8 par étapes, un commit par
   étape, tests verts à chaque étape.
3. Mets à jour DECISIONS.md (statut « proposée »), docs/conception/, docs/utilisateur.md, ETAT.md.
4. Dans ETAT.md, la section « En attente de Sednal » ne doit contenir que : sujet(s), clés des
   fournisseurs, limites, activation de `autonome`. Rien d'autre.
Ne lance aucune collecte réelle tant que `autonome: true` n'est pas mis par Sednal.
