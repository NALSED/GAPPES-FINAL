# Phase 8 — multiprise universelle de recherche

Statut : **proposée** (REPONSES_SEDNAL_6.md, à confirmer par Sednal). Implémentée dans `src/grappes/search/`. Aucune recherche réelle n'a été lancée : les tests n'utilisent qu'un faux serveur HTTP et un faux serveur MCP locaux.

## Périmètre

* Oubliés (REPONSES_SEDNAL_6 remplace les sections 1 et 2 de REPONSES_SEDNAL_5.md) : collecteurs par réseau social, détection automatique de format, adaptateur Instagram supplémentaire. Ce qui existait est conservé.
* La phase 8 est **uniquement** une multiprise de recherche : n'importe quel fournisseur se branche sans toucher au cœur.

## Architecture

````text
mots-clés (grappe ou saisis) ──> run_search ──> fournisseurs de la liste blanche
                                                 │  type http   : YAML (API, RSS/Atom, CSV)
                                                 │  type mcp    : client d'un serveur MCP externe
                                                 │  type <nom>  : plugin Python (plugins/*.py)
                                                 v
        Candidate (format commun) ──> fusion ──> candidats.csv   (+ liens déjà cités, sans appel)
````

| Module | Rôle |
| --- | --- |
| `search/base.py` | `SearchProvider`, registre par `type`, `SearchContext` (dry-run, quotas, délai), `Journal` |
| `search/models.py` | `Candidate` (format commun), `MergedCandidate`, fusion, colonnes du CSV |
| `search/config.py` | `config/recherche.yaml` (liste blanche, verrous), `config/recherche/*.yaml` (un fichier par fournisseur) |
| `search/http.py` | type `http` : authentification, GET/POST, gabarits, pagination, formats |
| `search/mcpclient.py` | type `mcp` : appel d'un outil d'un serveur MCP (stdio ou HTTP) |
| `search/formats.py`, `paths.py`, `build.py` | décodage JSON/XML/CSV, chemins et transformations, construction du candidat |
| `search/safe.py` | nettoyage des données non fiables |
| `search/plugins.py` | découverte automatique de `plugins/*.py` |
| `search/engine.py` | orchestration, erreurs contenues, `candidats.csv` |
| `search/internal.py` | candidats issus des liens déjà cités (D24) |

Le cœur (ingestion, scoring, recoupement, affectation, export) ne connaît aucun fournisseur. Les types `http` et `mcp` sont des mécanismes génériques ; aucun service particulier n'est nommé dans le code.

## Format de sortie : `candidats.csv`

Colonnes : `ecosysteme`, `identifiant`, `url`, `mot_cle`, `fournisseur`, `raison`, `date`, `extra`. Défini une fois, indépendant des fournisseurs. Les candidats identiques (même écosystème et même identifiant) sont fusionnés : `mot_cle` et `fournisseur` listent toutes les origines (séparées par ` | `), `extra` est un JSON `{fournisseur: champs spécifiques conservés tels quels}`.

## Sécurité

* **Données non fiables** : un résultat d'API ou de MCP n'est jamais exécuté, jamais interprété comme une instruction, jamais passé à un modèle (aucun appel de modèle dans le module). On n'extrait que des champs typés : texte sans caractères de contrôle et borné (500 caractères), URL `http(s)` valide (≤ 2048), date lisible. Une URL `javascript:` est écartée ; un texte du type « ignore tes instructions » reste une simple donnée.
* **Liste blanche et verrous** : tout est désactivé par défaut. Un appel réel exige `actifs` (fournisseur listé) **et** `execution_autorisee: true` **et** l'option `--execute`. Sinon : dry-run (journal, aucun appel).
* **Secrets** : uniquement par variables d'environnement (`env`), jamais dans le dépôt ni dans le journal (valeurs masquées, paramètre d'authentification d'URL non journalisé). Sans clé, le fournisseur est inactif.
* **Réseau** : redirections non suivies ; réponse limitée à 2 Mo ; XML sans DTD ni entité (`DOCTYPE` refusé) ; lien « suivant » suivi seulement s'il reste sur l'origine configurée ; arrêt sur 403/429 (aucune nouvelle tentative) ; quotas par fournisseur et total ; délai entre requêtes.
* **Journal** : `donnees/journal_recherche.log` (fournisseur, date, mot-clé, requête sans secret, statut) ; ignoré par git.
* **Interdit** : scraping de réseaux sociaux, comptes de connexion, contournement de limites, contenu privé. Un fournisseur se déclare `public: true` (défaut) : la phase 9 n'ingère rien d'autre.
* Un plugin Python est du code local écrit par l'opérateur : il n'est jamais téléchargé ; un plugin qui plante est ignoré ou contenu, jamais fatal.

## Tests (`tests/test_recherche.py`, `tests/fakes_recherche.py`)

Faux serveur HTTP local (clé en en-tête, paramètre, Bearer, Basic, POST JSON/formulaire, RSS, Atom, CSV, pagination par page, décalage, curseur, lien suivant avec lien externe, 403, 429, 500, JSON mal formé, redirection, réponse piégée, réponse trop grosse) et faux serveur MCP (stdio et HTTP) : dry-run, liste blanche, clé absente, secret absent du journal, quota, délai, doublons fusionnés, CSV, résultats piégés. **Test d'ouverture** : un fournisseur factice ajouté uniquement par YAML, un autre uniquement par plugin ; l'empreinte de tout `src/` est identique avant et après.

## Décisions

D27 à D29 dans `DECISIONS.md`.
