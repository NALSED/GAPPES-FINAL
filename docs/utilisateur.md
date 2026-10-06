# Guide utilisateur

## Flux

1. `grappes ingest <dossier> --ecosystem x|telegram|instagram|web` : lit les `.json` / `.jsonl`, normalise, stocke (idempotent sur `obs_id`). Affiche nouvelles observations, doublons, rejets.
2. `grappes run` : scoring sémantique, citations, recoupement itératif borné, affectation. Le `run_id` dépend des observations et de la configuration : rejouer donne le même résultat.
3. `grappes export --out ./sorties` : `entites.csv` (une ligne par entité) et `appartenances.csv` (format long).
4. `grappes explain <entity_id> [--grappe G]` : preuves (termes trouvés, citants, validation par recoupement).
5. `grappes purge --older-than 180` : supprime les observations plus anciennes que N jours.
6. `grappes mcp` : serveur MCP lecture seule (voir `README.md`).

## Configuration (`config/`)

* `grappes/*.yaml` : une grappe par fichier (`id`, `label`, `scale`, `lexicon.terms`, `lexicon.negative`, `anchors`, `oppositions`). Les lexiques réels sont à fournir ; ceux du dépôt sont des démonstrations neutres.
* `sources.yaml` : poids par écosystème et surcharges par source.
* `scoring.yaml` : seuils (`seuil_min`, `marge_ambiguite`, niveaux), poids de la confiance, `crossref` (`min_citers`, `min_ecosystems`, `min_weight_sum`, `min_citer_confidence`, `window_days`), `crossref_floor`, `max_iter`, format CSV.
* `config_hash` (empreinte des fichiers) est enregistré avec chaque run.

## Lire le CSV

* `cluster_id` : grappe principale ; vide si `non_classé` (confiance < `seuil_min`).
* `confidence_level` : `confirmé` ≥ 70, `probable` ≥ 40, `faible` sinon.
* `status` : `classé`, `ambigu` (grappe proche ou opposée), `non_classé`.
* `validated_via_crossref` : `oui` si l appartenance principale vient du recoupement.
* Confiance = S + (100 − S)·(0,6·E + 0,4·A) / 100 (S sémantique, E recoupement, A ancrage, tous sur 0 à 100). Sans citations, confiance = S. E vaut 0 tant que le recoupement n'est pas validé (D19) ; `explain` signale alors `recoupement_partiel` et l'E potentiel non retenu. Valeurs initiales, configurables (`poids_complementaire`, voir `DECISIONS.md` D15). L'ancienne formule 0,5·S + 0,3·E + 0,2·A reste disponible avec `formule_confiance: ponderee` (poids dans `poids_confiance`).
* Proximité sémantique : 100 × (1 − exp(−brut / scale)), `scale = 3` par défaut (par grappe). Un terme de poids 1 donne ≈ 28, trois termes ≈ 63 (D7).

## Limites connues

* Formats JSON d entrée proposés, non réels (Q2) : `docs/conception/formats_json.md`.
* Les liens `t.me` créent une entité `web:t.me`.

## Corpus synthétique

````bash
.venv/bin/python outils/corpus_synthetique.py /tmp/corpus   # x/, telegram/, web/, attendu.json
.venv/bin/grappes --db /tmp/corpus/c.db ingest /tmp/corpus/x --ecosystem x
````

Thèmes neutres inventés, graine fixe : mêmes fichiers à chaque génération. `attendu.json` donne le statut attendu des cibles de recoupement (validé, refusé, ambigu).


## Recherche de candidats (phase 8)

````bash
grappes search --keywords "soupe,potager"          # dry-run : journal seulement, aucun appel
grappes search --grappe G-DEMO-A                   # les termes de la grappe servent de mots-clés
grappes search --keywords "soupe" --provider mon_api --execute   # appels réels (si autorisés)
````

Résultat : `sorties/candidats.csv` (`ecosysteme`, `identifiant`, `url`, `mot_cle`, `fournisseur`, `raison`, `date`, `extra`). Les liens déjà cités dans vos données sont ajoutés sans appel externe (fournisseur `liens_internes`). Les candidats ne sont jamais ingérés sans règle d'autonomie explicite.

Tout est **désactivé par défaut**. Un appel réel demande trois choses : le fournisseur dans `actifs` (`config/recherche.yaml`), `execution_autorisee: true` dans ce même fichier, et l'option `--execute`. Les clés passent par des variables d'environnement, jamais par un fichier du dépôt.

### Brancher une nouvelle API en 10 minutes

1. **Copiez un exemple** de `config/recherche/exemples/` (API JSON à clé, flux RSS, serveur MCP) dans `config/recherche/`, sous le nom de votre choix, et changez `id`.
2. **Adaptez l'URL et les paramètres** : `{mots_cles}` (le mot-clé), `{limite}`, `{page}`, `{decalage}`, `{curseur}` sont remplacés ; les autres valeurs restent telles quelles.
3. **Authentification** (`auth`) : `header` (`name`, `env`, `prefix`), `query` (`name`, `env`), `bearer`, `basic` (`user_env`, `password_env`), `oauth_env` (jeton obtenu ailleurs, fourni par la variable `env`), ou rien. Exportez la clé : `export MA_CLE_API=...`. Sans clé, le fournisseur reste inactif.
4. **Méthode et corps** : `method: POST` avec `body: {type: json|form, content: {...}}`.
5. **Pagination** (`pagination`) : `page` (`param`, `start`), `offset` (`param`, `size`), `cursor` (`param`, `cursor_path`), `next_link` (`next_path`) ; `max_pages` (3 par défaut, 20 au plus).
6. **Réponse** : `format: json | xml | csv`, `items` = chemin vers la liste des résultats (`data.results`, `rss.channel.item`, `feed.entry`...).
7. **Champs** (`fields`) : `title`, `url`, `id`, `description`, `date`, chacun par un chemin (`a.b[0].c`, `lien.@href` pour un attribut XML) ou par un mapping : `template: "{owner}/{name}"` (concaténation), `regex` + `group`, `prefix`, `suffix`, `default`.
8. **Activez-le** : ajoutez son `id` à `actifs` dans `config/recherche.yaml`, puis lancez d'abord `grappes search --keywords test` (dry-run : le journal montre la requête exacte qui serait envoyée, sans secret).
9. **Cas trop complexe** : écrivez un plugin Python dans `plugins/` (il est découvert tout seul, aucun fichier du dépôt n'est modifié) :

````python
from grappes.search import Candidate, SearchProvider, register_provider


@register_provider
class MonFournisseur(SearchProvider):
    type = "mon_fournisseur"  # référencé par `type:` dans le YAML

    def search(self, keyword, limit):
        if not self.ctx.execute:  # dry-run : journaliser sans appeler
            self.ctx.journal.log(self.id, keyword, "ma requête", "dry-run")
            return
        # ... appelez votre source avec self.options (le reste du YAML), puis :
        yield Candidate("web", "exemple.test", "https://exemple.test/", keyword, self.id, "raison")
````

Les champs spécifiques d'un fournisseur sont conservés tels quels dans la colonne `extra`. Interdits : scraping de réseaux sociaux, comptes de connexion, contournement de limites, contenu privé.
