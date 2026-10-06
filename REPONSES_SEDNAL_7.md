# Réponses de Sednal n°7 : phase 9, boucle automatique d'auto-amélioration (proposition, à confirmer par Sednal)

## Objectif
Sednal ne veut plus intervenir après la mise en place. Le système tourne seul par cycles et
s'améliore, dans des limites fixées UNE FOIS en configuration (c'est l'autorisation de Sednal).
Remplace la règle « les candidats ne sont jamais ingérés automatiquement » par : ingestion
automatique autorisée seulement pour les candidats qui respectent la configuration d'autonomie
ci-dessous. Tout le reste de Q7 s'applique toujours (sources publiques uniquement, redact_persons,
retention_days, pas de scraping de réseaux sociaux, pas de contenu privé).

## Commande `grappes cycle`
Un cycle = collecte (fournisseurs de recherche AUTORISÉS) -> ingestion -> score -> recoupement ->
assignation -> apprentissage -> recalibrage -> export CSV -> rapport. Idempotent, journalisé,
déclenchable par une planification (timer systemd ou cron sur momo, hebdomadaire par défaut,
fréquence configurable). Verrou pour empêcher deux cycles simultanés. Sans configuration
d'autonomie explicite : mode dry-run, rien n'est écrit.

## Configuration d'autonomie (fichier unique, valeurs par défaut prudentes)
- autonome: false par défaut ; Sednal l'active lui-même.
- fournisseurs et domaines autorisés, quota de requêtes et d'éléments ingérés par cycle,
  nombre maximal de nouvelles sources par cycle ;
- candidat ingérable seulement si : source publique, domaine/fournisseur autorisé, citée par
  au moins une source déjà confirmée, pas de login requis.

## Apprentissage (avec garde-fous)
- Mots appris : termes discriminants (TF-IDF ou équivalent) fréquents chez les entités
  « confirmées » (validées par recoupement d'au moins 2 écosystèmes) et rares ailleurs.
  Ajoutés à un fichier SÉPARÉ « lexique_appris » par grappe, poids faible, maximum N termes par
  cycle et par grappe, expiration si non revus. Les lexiques et ancres écrits par Sednal ne sont
  jamais modifiés ni supprimés.
- Seuils : recalibrage borné (variation maximale par cycle, bornes min/max), calculé sur les
  entités confirmées uniquement.
- Aucun apprentissage à partir d'entités « probables » seules ou d'une source mono-écosystème.

## Retour en arrière automatique
- Chaque cycle crée un instantané versionné de la configuration apprise et des résultats.
- Indicateurs de stabilité : part des entités qui changent de grappe, taux d'ambiguïté, taux de
  confirmés, dérive du lexique. Si un indicateur dépasse un seuil configurable, annule le cycle,
  restaure l'instantané précédent, et signale-le dans le rapport.
- Commande `grappes rollback` et interrupteur d'arrêt (`autonome: false` ou fichier STOP).

## Rapport
`rapports/cycle_<date>.md`, lisible par un non-informaticien : ce qui est entré, ce qui a changé
de grappe, mots appris, seuils modifiés, retours en arrière, alertes. Lien dans ETAT.md.

## Tests
Corpus synthétique : le système améliore la séparation de deux grappes sur 3 cycles ; un corpus
piégé (sources fausses qui se citent entre elles) ne contamine pas les lexiques ; le retour en
arrière se déclenche sur une dégradation simulée ; aucune requête réelle dans les tests.

## Suite
Documente (DECISIONS.md : « proposées », docs/conception/phase9.md, docs/utilisateur.md).
Termine REPONSES_SEDNAL_4.md et 6, puis fais la phase 9 par étapes avec commits. Ne lance aucun
cycle réel avec `autonome: true` : Sednal l'activera lui-même quand il aura configuré les
fournisseurs.
