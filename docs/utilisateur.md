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
grappes search --sujet "jardins partagés en ville"   # {sujet} dans les gabarits ; appels réels seulement si `autonome`
````

Résultat : `sorties/candidats.csv` (`ecosysteme`, `identifiant`, `url`, `mot_cle`, `fournisseur`, `raison`, `date`, `extra`). Les liens déjà cités dans vos données sont ajoutés sans appel externe (fournisseur `liens_internes`). Les candidats sont ingérés automatiquement par `grappes cycle` selon les règles générales (publics, hors interdits, assez proches d'un sujet), sans validation humaine.

Tout est **désactivé par défaut**. Un appel réel demande deux choses : le fournisseur dans `actifs` (`config/recherche.yaml`) et `autonome: true` (`config/autonomie.yaml`, false par défaut = dry-run) ; le fichier `donnees/STOP` arrête tout. Les clés passent par des variables d'environnement, jamais par un fichier du dépôt.

### Brancher une nouvelle API en 10 minutes

1. **Copiez un exemple** de `config/recherche/exemples/` (API JSON à clé, flux RSS, serveur MCP) dans `config/recherche/`, sous le nom de votre choix, et changez `id`.
2. **Adaptez l'URL et les paramètres** : `{sujet}` (la phrase du sujet), `{mots_cles}` (le mot-clé), `{limite}`, `{page}`, `{decalage}`, `{curseur}` sont remplacés ; les autres valeurs restent telles quelles.
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

## Sortie finale : `sorties/resultat.csv`

`grappes export` écrit, en plus de `entites.csv` et `appartenances.csv`, le fichier `sorties/resultat.csv` : **une seule colonne** `NOM`, une ligne par entité retenue (assignée à une grappe, confirmée ou probable), triée par ordre alphabétique, en UTF-8 sans BOM. Avec plusieurs grappes, un fichier `resultat_<grappe>.csv` par grappe s'ajoute.

* Le nom est lisible (organisation, média, site, canal, compte institutionnel), jamais un identifiant ni une URL. Une entité sans nom connu n'est pas exportée.
* Les variantes d'écriture (casse, accents, espaces, suffixes comme « officiel ») sont fusionnées.
* Seuil : `resultat.confiance_min` dans `config/scoring.yaml` (défaut : niveau « probable »).
* **Personnes physiques exclues par défaut.** Un compte est une personne, sauf indice explicite dans son nom (association, journal, radio, mairie...). En cas de doute : une personne.

````yaml
resultat:
  inclure_personnes: false   # NE PASSEZ À true QU'EN CONNAISSANCE DE CAUSE
````

**Avertissement.** Avec `inclure_personnes: true`, les noms de personnes physiques figurent **en clair** dans `resultat.csv` : le masquage (`redact_persons`) ne s'applique plus à ce fichier. `entites.csv`, le serveur MCP et le rapport continuent de masquer les personnes. Le fichier est alors un traitement de données personnelles : à votre charge.

## Cadre de données

Valeurs proposées, réversibles dans `config/scoring.yaml` : sources publiques uniquement ; `retention_days: 90` (observations plus anciennes supprimées par `grappes purge` et par chaque cycle ; `null` = illimité) ; `redact_persons: true` (personnes masquées par un pseudonyme dans `entites.csv` et le serveur MCP). La base SQLite garde les identifiants nécessaires au calcul : protégez l'accès au fichier.

## Canaux Telegram : table d'équivalence

L'export Telegram Desktop ne donne que le nom affiché d'un canal. `config/telegram.yaml` associe un nom affiché à l'identifiant public (celui de `t.me/<identifiant>`). Sans entrée, l'identifiant est déduit du nom et marqué « hypothèse » : `grappes explain` liste ces citations (`citations_hypothetiques`) et elles ne valident jamais un recoupement. Deux canaux de même nom ne sont jamais fusionnés.

## Bilan des économies de jetons

````bash
.venv/bin/python outils/bilan_jetons.py          # régénère ECONOMIES.md
````

Le rapport `ECONOMIES.md` croise deux sources, et seulement elles : `donnees/.journal_ccr.log` (les appels routés vers le compte gratuit) et `rtk gain --daily --format json` (le hook RTK). Il donne le nombre d'appels gratuits et la période couverte, le gain RTK du projet et du compte, un total consolidé avec sa marge d'incertitude, une ligne par jour et le détail des hypothèses.

Lecture à garder en tête :

* **Le gain RTK est une estimation** (octets / 4) limitée à la sortie interceptée par rtk ; ce n'est pas l'économie totale de jetons ni de coût.
* **Le journal gratuit ne contient ni jetons ni octets** : le volume est affiché « non disponible », jamais estimé. Le total consolidé est donc un minimum chiffrable.
* La marge d'incertitude repose sur deux ratios octets/jeton **déclarés comme hypothèses** (`--ratio-bas`, `--ratio-haut`, 3 et 5 par défaut), pas sur une mesure.
* Une source absente, vide ou illisible est signalée dans le rapport, qui continue avec l'autre.

## Mise en route autonome (ce que Sednal fournit, et rien d'autre)

1. **Un ou plusieurs sujets**, une phrase chacun, dans `config/sujets.yaml` :

````yaml
sujets:
  - "jardins partagés et potagers collectifs en milieu urbain"
````

2. **Les clés des fournisseurs de recherche** : un fichier YAML par fournisseur dans `config/recherche/` (voir « Brancher une nouvelle API en 10 minutes »), son `id` dans `actifs` (`config/recherche.yaml`), la clé dans une variable d'environnement.
3. **Les limites générales** dans `config/autonomie.yaml` : quotas par cycle (requêtes, pages, nouvelles sources, observations), profondeur d'exploration, seuil de proximité, et la liste des **INTERDITS** (`interdits.domaines`, `interdits.motifs`).
4. **L'interrupteur** `autonome: true` dans `config/autonomie.yaml` (false par défaut). Le fichier `donnees/STOP` arrête tout immédiatement.

Aucun site, aucun mot-clé, aucun lexique de départ, aucun export à fournir. Le lexique de chaque sujet est amorcé automatiquement à partir de la phrase, puis affiné par la boucle ; `config/grappes/*.yaml` reste possible (ancres, oppositions) mais n'est plus nécessaire.

## Boucle automatique : `grappes cycle`

````bash
grappes cycle              # simulation tant que autonome est faux : rien n'est appelé ni écrit
grappes cycle --dry-run    # simulation forcée
grappes rollback           # annule le dernier cycle terminé
````

Un cycle fait : amorçage des sujets, collecte, ingestion, score, recoupement, assignation, apprentissage, recalibrage, export, rapport. Il est idempotent, journalisé (`donnees/cycles.jsonl`), verrouillé (un seul à la fois) et planifiable (`outils/systemd/`, hebdomadaire par défaut, à installer par Sednal). Le rapport `rapports/cycle_<date>.md` se lit sans compétence technique : ce qui est entré, ce qui a changé de grappe, mots appris, seuils modifiés, retours en arrière, alertes.

**Règles de collecte, non désactivables** : sources publiques seulement ; `robots.txt` respecté ; ni connexion ni compte ; aucun contournement de limite ni de captcha ; au moins 1 s entre deux requêtes vers un domaine ; arrêt sur 403/429 ; User-Agent identifiable ; les **réseaux sociaux ne sont jamais lus** (leurs liens deviennent des citations). Tout ce qui est reçu (API, serveur MCP, page) est une donnée non fiable, jamais exécutée ni prise pour une instruction.

**Ingestion automatique** : un candidat est ingéré s'il est public, respecte ces règles, n'est pas dans les interdits et atteint la proximité minimale avec un sujet. Une source non recoupée reste « probable » au mieux ; « confirmé » exige un recoupement sur au moins deux écosystèmes.

**Retour en arrière automatique** si un indicateur dépasse son seuil (entités qui changent de grappe, ambiguïté, chute des confirmées, dérive du lexique appris) : l'état d'avant (base, mots appris, seuils, sorties) est restauré et le rapport le dit. Détails : `docs/conception/cycle.md`.

Codes de sortie : 0 normal ou simulation, 1 erreur, 3 un autre cycle est en cours, 4 arrêt demandé, 5 cycle annulé par la stabilité.

