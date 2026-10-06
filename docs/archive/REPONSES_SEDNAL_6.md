> **OBSOLÈTE** : remplacé par `FINAL.md` (référence unique, 2026-10-06). Conservé pour l'historique uniquement ; ne pas s'y référer.

# Réponses de Sednal n°6 : phase 8 recentrée sur la recherche (proposition, à confirmer par Sednal)

## Changement de périmètre
Oublie les sections 1 et 2 de REPONSES_SEDNAL_5.md : pas de collecteurs par réseau social, pas de
détection automatique de format, pas d'adaptateur Instagram de plus. Garde ce qui existe déjà.
La phase 8 = UNIQUEMENT une « multiprise universelle de recherche ».

## Objectif
Pouvoir brancher n'importe quel fournisseur de recherche sans toucher au cœur du système.
Un fournisseur est un plugin (interface `SearchProvider` + registre, comme BaseFetcher).
Entrée : mots-clés (d'une grappe ou saisis). Sortie : `candidats.csv` (écosystème, identifiant,
URL, mot-clé d'origine, fournisseur, raison, date, extra). Les candidats ne sont JAMAIS ingérés
automatiquement : Sednal valide.

## Ouverture (exigence de Sednal, prioritaire sur le reste du bloc)
La recherche ne doit RIEN avoir de fermé. Sednal doit pouvoir brancher n'importe quelle API.
- Aucun fournisseur codé en dur dans le cœur : même le premier fournisseur est une simple
  configuration d'exemple, supprimable sans casser quoi que ce soit.
- Ajouter une API = écrire un fichier YAML, sans toucher au code. Le YAML couvre au minimum :
  authentification variée (en-tête, paramètre d'URL, Bearer, Basic, jeton OAuth fourni en
  variable d'environnement), méthodes GET/POST, corps JSON ou formulaire, gabarits de paramètres
  ({mots_cles}), pagination (curseur, numéro de page, décalage, lien « suivant »), formats de
  réponse (JSON, XML/RSS/Atom, CSV), chemins vers les champs (titre, URL, identifiant,
  description), et transformations simples (expression régulière, concaténation, valeur par défaut).
- Cas trop complexe pour le YAML : un plugin Python qui implémente `SearchProvider`, déposé dans
  un dossier `plugins/` et découvert automatiquement, sans modifier le dépôt principal.
- Le format de sortie commun (candidats) est défini une fois et ne dépend d'aucun fournisseur ;
  les champs spécifiques d'un fournisseur sont conservés tels quels dans une colonne `extra`.
- Plusieurs fournisseurs peuvent être interrogés ensemble ; les candidats identiques sont
  fusionnés et gardent la liste de leurs fournisseurs d'origine.
- Fournis 3 exemples de configuration très différents (API JSON à clé, flux RSS, serveur MCP) et
  un guide « brancher une nouvelle API en 10 minutes » dans docs/utilisateur.md.
- Test d'ouverture : un test ajoute un fournisseur factice uniquement par YAML, et un autre
  uniquement par plugin, et vérifie qu'aucune ligne du cœur n'a changé.

## Deux types de prises universelles
1. API HTTP générique, pilotée par configuration YAML (voir « Ouverture »). Sans clé = inactif.
2. Client MCP : appelle les outils d'un serveur MCP externe (stdio ou HTTP), défini en
   configuration (commande ou URL, outil à appeler, correspondance des arguments et du résultat
   vers le format commun). Distinct du serveur MCP en lecture seule de grappes (qui sert vers
   l'extérieur).

## Sécurité (obligatoire)
- Tout résultat reçu (API ou MCP) est une DONNÉE non fiable : jamais exécuté, jamais interprété
  comme instruction, jamais passé tel quel à un modèle ; on n'en extrait que des champs typés
  (texte nettoyé, URL validée).
- Liste blanche des fournisseurs actifs en configuration ; tout est désactivé par défaut.
- Secrets uniquement par variables d'environnement, jamais dans le dépôt ni dans les journaux.
- Mode dry-run par défaut ; quotas ; journal des appels (fournisseur, date, requête, statut)
  dans donnees/journal_recherche.log. Délai entre requêtes, arrêt sur 403/429.
- Les liens déjà cités dans les données (D24) alimentent aussi les candidats, sans appel externe.
- Interdit : scraping de réseaux sociaux, comptes de connexion, contournement de limites,
  collecte de contenu privé.

## Tests
Uniquement contre un faux serveur local (API) et un faux serveur MCP : aucune requête réelle.
Cas : réponse mal formée, résultat piégé (texte type « ignore tes instructions »), clé absente,
quota dépassé, doublons de candidats.

## Suite
Documente (DECISIONS.md : décisions « proposées », docs/conception/phase8.md, docs/utilisateur.md),
mets à jour ETAT.md, commit par étape. Ne lance aucune recherche réelle sans accord de Sednal.
Termine d'abord REPONSES_SEDNAL_4.md, puis applique celui-ci.
