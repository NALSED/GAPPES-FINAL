# Questions ouvertes — pavé de retours de Sednal du 02/11/2026

Rien n'est inventé ici : chaque point attend une décision ou une session dédiée avant d'être tranché.

## 3.8.04 — Boucle : la relance réelle du moteur n'est pas câblée

Le réglage de la tuile (origine de la liste, élément remplacé, maximum de tours) est validé et réglable depuis la
fenêtre de la tuile, mais **la recherche n'est pas encore relancée réellement une fois par élément** —
`suite_plan.py` continue de dire « pas encore branché dans le moteur » dans le plan appliqué, comme avant.

Pourquoi je m'arrête là plutôt que de câbler `ExecuteurGrappes` directement :

* Faire tourner une recherche complète par élément suppose un dossier de travail (et donc un `lancement.json`,
  un `candidats.json`, un `avancement.jsonl`…) **par tour**, alors qu'aujourd'hui tout le programme suppose un
  seul dossier par recherche. Au moins un module en dépend directement et casserait en silence :
  `mentions.py::sources_de_la_recherche()` lit `dossier_recherche / "lancement.json"` à la racine — avec un
  dossier par tour, elle ne trouverait plus rien et les mentions obligatoires (licences, ex. GDELT)
  disparaîtraient d'un export sans qu'aucun test ne le dise (`ctx.dossier` n'est testable nulle part dans ce
  bac à sable : la config `grappes.racine` manque ici — voir plus bas — donc aucune recherche réelle ne peut
  être rejouée pour vérifier un tel changement avant de le pousser).
* Je n'ai pas cherché exhaustivement tout ce qui suppose la même chose ailleurs dans `pont/executer.py` et
  consorts : le risque d'une régression silencieuse ailleurs (pas seulement les mentions) est réel sans une
  revue dédiée.
* La protection « tours × appels ne dépasse pas le budget » demandée par le pavé est elle-même ambiguë : contre
  quel budget exactement (le plafond de crédits mensuel, 3.8.08 ? un plafond propre à la recherche ?) — je n'ai
  pas inventé de seuil. « Maximum de tours » (déjà présent) reste le seul garde-fou réel pour l'instant.

**Prêt pour une session dédiée, avec un moteur grappes réellement accessible pour vérifier (pas seulement les
tests qui ne dépendent d'aucun service extérieur)** : repérer tous les endroits qui supposent un dossier de
recherche unique, décider où isoler les tours (un sous-dossier chacun, candidats accumulés dans la même
`Recherche`), puis trancher le calcul du garde-fou budget avec Sednal.

**Addendum (908, point 9.1, 09/11/2026)** : le retour de Sednal du 08/11 décrit « seule l'origine Liste
collée est branchée ; les deux autres ne font rien » et demande de brancher les deux manquantes. Relu le code
le même jour : **aucune des trois origines ne relance réellement la recherche** — `_raison_boucle()` répond
« pas encore branché dans le moteur » pour les trois, « Liste collée » comprise (seule la validation du
réglage et le compte des éléments collés fonctionnent). Le premier correctif ci-dessus (dossier par recherche
unique, pas de moteur grappes accessible pour vérifier) s'applique donc identiquement aux trois origines,
pas à deux. Je n'ai pas branché l'exécution pour cette raison — ce serait recréer exactement le risque déjà
écarté le 02/11. Fait à la place, sans toucher à l'exécuteur : le libellé qui dit le remplacement (9.2) et un
aperçu des recherches que la boucle produirait, affiché sans rien lancer (9.3) — les deux utiles même une fois
le branchement fait, et sans risque de régression silencieuse.

## 908, point 14.1/14.2 — l'Aide parle au vrai agent ; agir via les routes, pas encore (09/11/2026)

Fait (14.1) : l'Aide (fiche 11) choisissait sa fonction via un serveur Ollama local « pas tranché »
(`suite_modele.py`, Q suite-4, jamais déployé nulle part) — elle parle maintenant au même agent que
l'Assistant IA (`suite_ia.py`, 3.8.09, déjà vérifié en réel sur .250). Même contrat, même garde-fou : une
liste CLOSE de six fonctions (`lister_sources`, `lire_plan`, `proposer_plan`, `verifier_plan`, `definir`,
`ouvrir`), toutes DÉJÀ existantes et sûres — l'agent choisit, une fonction réelle exécute, jamais de code
exécuté à l'aveugle. Les trois puces (« Comment je fais… », etc.) continuent de marcher sans agent.

Pas fait (14.2, le volet « agir ») : étendre la liste aux actions qui CHANGENT l'état (allumer une source,
changer un réglage, lancer une recherche) avec confirmation avant tout geste qui dépense ou change l'état,
attribution au Journal (« IA », pas l'utilisateur), et les quatre interdits absolus (jamais supprimer un
résultat, jamais écraser une décision de Tri, jamais lever la règle 8, jamais de shell). Je n'ai pas voulu
construire ces garde-fous dans la même passe que le changement d'agent : c'est la partie qui, mal câblée,
abîmerait vraiment quelque chose (contrairement à une lecture, qui ne risque rien). Prêt à reprendre : la
liste close existe déjà comme modèle (six fonctions READ), il s'agit d'y ajouter des fonctions WRITE une par
une, chacune avec sa propre confirmation — pas un mécanisme générique « appelle n'importe quelle route ».

## 908, point 5.2 b — « source de secours » générale : pas câblée, même prudence que la Boucle (09/11/2026)

Demande de Sednal (retour du 08/11/2026) : sortir de `osm-overpass.yaml` (son essai serveur auto-hébergé puis
serveurs publics) l'idée d'une source « appelée seulement si les sources principales n'ont rien rendu ou ont
échoué », pour en faire un réglage partagé par n'importe quelle source (pas seulement Overpass, pas seulement
Scrapling).

Pourquoi je m'arrête là plutôt que de câbler cette séquence :

* « Les sources principales n'ont rien rendu » ne se sait qu'APRÈS les avoir appelées, dans la boucle qui
  interroge chaque source — `pont/executer.py` (le moteur grappes), pas un endroit où pilote décide à
  l'avance. Changer cette boucle demande de la revoir avec un moteur grappes réellement accessible pour
  vérifier (même trou d'infra que la Boucle, 3.8.04, et pour la même raison : `grappes.racine` ne résout pas
  dans cet environnement — voir « Trou d'infra pré-existant » ci-dessous).
* Le précédent d'Overpass fonctionne parce qu'il reste À L'INTÉRIEUR d'un seul adaptateur (une boucle Python
  sur une liste d'URLs, rien à voir avec l'ordonnancement entre sources différentes que demande ce point).
  Le généraliser à N'IMPORTE QUELLE source suppose de savoir, au niveau du moteur, lesquelles sont
  « principales » et lesquelles sont « secours » pour une recherche donnée, puis de reporter l'appel des
  secondes — une vraie décision d'ordonnancement, pas un réglage d'affichage.

**Prêt pour la même session dédiée que 3.8.04** (Boucle) : les deux ont besoin du même accès à un moteur
grappes réel pour être vérifiés avant de pousser quoi que ce soit qui touche `pont/executer.py`.

## 3.8.09 — Assistant IA : câblé pour de vrai, testé sur .250 (clos le 03/11/2026)

`suite_ia.py` (appel silencieux à l'agent Claude Code, `claude -p … --model …`) et le registre
`operations_ia/` (résumer, classer, extraire des mots-clés — extensible comme `formats/`) sont écrits et
testés depuis le début de session. **Vérifié depuis .250 (03/11/2026)**, où l'agent est déjà installé et
connecté : `claude -p "…"` répond bien (silencieux, code 0, texte en stdout), exactement la commande que
construit `suite_ia.commande()`. `--model <nom>` et `--effort <niveau>` sont tous les deux acceptés par
`claude -p …`, mais `claude --model` sans argument n'affiche pas une liste exploitable (sélecteur
interactif) : pas de façon simple d'interroger la liste des modèles disponibles pour en faire un menu
fermé — **le champ texte libre déjà choisi pour « Modèle » était donc le bon choix**, pas une solution
provisoire à corriger.

**Précisé par Sednal (03/11/2026, spec 901 mise à jour)** : pas la peine d'attendre .115, momo code et
teste sur .250, où l'agent est déjà installé — l'installation sur .115 (la machine de production) reste
une tâche de Sednal, séparée, pas un blocage.

**Précisé une seconde fois (904/Q33, même jour)** : le coût affiché n'est pas un nombre d'appels, mais les
**tokens réels** consommés — lus dans `usage` de `claude -p … --output-format json`, rien à estimer. Plus
un **plafond réel** (« Traiter au maximum », en plus de l'arrêt et du temps) sur le nombre de fiches
traitées. Informatif seulement : le forfait Pro/Max de Sednal n'est pas un quota en tokens (fenêtre
glissante de 5 h, sans solde publié) — jamais mêlé aux crédits, jamais plafonné lui-même. Au passage,
`--output-format json` a aussi révélé que l'agent peut rendre `is_error: true` à code de sortie 0 (modèle
inconnu, vérifié sur .250) : `suite_ia.demander()` le détecte désormais, sans quoi un échec aurait pu
passer pour un vrai résumé.

**Fait (puis corrigé par la revue 902, D84)** : `suite_plan.compiler()` compile la tuile (une seule jouée par
recherche ; refusée et dite si l'agent est absent de la machine ; options Opération, Modèle, Effort — menu fermé de
six mots, `claude --effort` existe —, Marquer les résultats). Elle devient une étape de passage sur les branches qui
la traversent : seuls les noms qui ATTEIGNENT la tuile sont traités, après les chemins et avant la vérification
(comme le demande la spec). `suite_ia.appliquer_lignes()` range le texte dans `faits["ia"]` et la marque dans
`faits["ia_marque"]` — jamais en colonne de la fiche : la première version y écrivait `resume_ia` et **toute recherche
avec une tuile IA finissait en échec** (trouvé par le test réel de la revue). Une ligne dont l'agent échoue garde son
résultat sans le champ IA, comptée à part ; l'arrêt demandé et la limite de temps sont respectés (les lignes non
traitées sont comptées). L'agent est cherché sur le PATH puis à `~/.local/bin/claude` (un service systemd n'a pas ce
dossier dans son PATH). Journal : `plan_ia_appels` (appels, échecs, non traités), séparé des crédits. Export :
colonne `ia`, « [IA] … » si marqué. Vérifié en réel sur .250 (registre des associations + Filtre + Résumer).

**Laissé de côté, sciemment, hors du périmètre demandé** : les options propres à chaque opération
(`classer` attend `categories`, `extraire_mots_cles` attend `maximum`) ne sont pas exposées dans la
fenêtre de la tuile — `_OUTILS["ia"]["options"]` n'a que Opération/Modèle/Marquer. `appliquer_lignes()`
passe `{}` : `classer` retombe sur `["autre"]`, `extraire_mots_cles` sur 5 mots. Fonctionnel, mais pas
configurable depuis l'écran — à reprendre si Sednal le demande (ajouter un champ par opération, sur le
modèle de `RENDUS_OPTIONS`).

## 3.8.10 — RSSHub : déployé sur .250, câblé, vérifié en réel (clos le 03/11/2026, D85)

**Instance** : image Docker officielle `diygod/rsshub:latest` (empreinte `sha256:1726b309…`), conteneur `rsshub`,
redémarrage automatique, à l'écoute de **127.0.0.1:1200 seulement** (rien d'exposé au réseau). Sur .115, même
commande ; puis `suite.rsshub_url: http://127.0.0.1:1200` dans `pilote.yaml` (section `suite:` ajoutée, vide par
défaut, comme `traduction_url`).

````
docker run -d --name rsshub --restart unless-stopped -p 127.0.0.1:1200:1200 diygod/rsshub:latest
````

**Contrat réel** (vérifié contre l'instance) : RSSHub n'a **pas** de point d'entrée « transforme cette adresse » ;
la route supposée avant (`/site/<domaine>`) n'existait pas. Il publie ses règles « Radar »
(`/api/radar/rules` : domaine → sous-domaine → motifs de chemin → route), celles qu'utilise l'extension RSSHub
Radar : `suite_rsshub.routes()` y cherche la route de l'adresse donnée, puis `resoudre()` lit le flux une fois
(par `flux_rss.telecharger`/`lire_flux` — plus d'appel HTTP propre, la duplication relevée par la revue est
retirée) pour vérifier qu'il rend des articles.

**Câblage** : la tuile est compilée sans réseau (`suite_plan`, refus dit sans `suite.rsshub_url`, refus si
l'adresse du site manque) ; au lancement, `api_suite` trouve le flux une fois (sinon la raison est dite dans les
outils non appliqués, et reprise dans le refus si RSSHub était la seule entrée) ; puis `materialiser` en fait une
prise du moteur par `definition_flux` — **exactement comme un flux ajouté à la main**. La spec plaçait le câblage
dans `pont/executer.py` ; les flux RSS n'y passent pas (ce sont des prises du moteur, écrites avant le pont) : le
mécanisme réellement réutilisé est celui de `moteur_sources`. Une recherche dont RSSHub est la seule entrée part.
La provenance s'affiche « RSSHub (site) », jamais l'identifiant de la prise ; au passage, un flux ajouté à la main
s'affichait « rss-… » dans Tri et à l'export (préexistant) : il s'affiche maintenant sous son nom.

**Vérifié en réel** : `https://www.lemonde.fr/international/` → route `/lemonde/international`, 20 articles,
recherche terminée en 12 s, 9 noms trouvés dans les articles. `https://www.liberation.fr/` → « RSSHub ne connaît
pas de route pour ce site », dit clairement.

**Pas utilisé** : « Rafraîchir toutes les » — RSSHub garde lui-même ses flux en cache, et pilote lit le flux une fois
par recherche ; l'option reste affichée, sans effet. Les motifs Radar avec requête (`/cherche?q=:q`) ne sont pas
pris en charge (ignorés, jamais une fausse correspondance).

**Addendum (908, point 15, 09/11/2026)** : l'instance ci-dessus avait été posée à la main sur .250/.115, sans
installeur réutilisable — c'est le manque que le point 15 du retour du 08/11 demande de combler. Fait :
`outils/installer_rsshub.sh`, qui rejoue la même commande Docker (vérifiée en réel ci-dessus) de façon
idempotente, sur le modèle des autres installeurs (`installer_overpass.sh`).

## Trou d'infra pré-existant, hors de ce pavé

`grappes.racine` dans la configuration livrée de `pilote/` pointe vers un dossier `grappes/` voisin
(`pilote/../grappes`), qui n'existe pas dans ce dépôt (le moteur est en `src/grappes`, pas `grappes/` à la
racine). Toute recherche réelle (`test_suite_plan_moteur.py`, `test_f12_recherches.py`, etc.) échoue donc par
« la configuration de grappes est introuvable » — déjà identifié dans `000-INDEX.md` (`900-demenagement-du-code.md`,
explicitement hors de ce pavé, « à valider » avant de vider `grappes/` et `pilote/` de GRAPPES). Je ne l'ai pas
touché : ce n'est pas mon rôle de le trancher seul, et plusieurs tuiles du pavé (3.8.04, 3.8.07, 3.8.09, 3.8.10)
ne pourront être vérifiées pour de vrai qu'une fois ce trou refermé.

## Deux tests rouges, pré-existants, hors de la 905 (constat, 08/11/2026)

`rtk pytest -q` (suite complète) : 658 verts, 2 rouges. Vérifiés tous les deux : rouges aussi sur le commit juste
avant la 905 §2 (bisecté par `git worktree` jusqu'à `1909984`, avant mes commits de la session) — pas une
régression de ce travail.

* `test_f19_retours_reglages.py::test_chaque_bloc_se_replie_et_garde_intitule_etat_et_rappel` : `assert blocs.count()
  == 8` rend 9 (page `/` ancienne UI, `#pg-reglages details.bloc`). Pas creusé : hors sujet de la 905/906/907,
  et touche l'ancienne UI que la 905 §3 va retirer.
* `test_suite_plan.py::test_la_tuile_jouee_ne_depend_pas_du_hasard_du_processus` : le sous-processus lancé avec
  `PYTHONHASHSEED` et `PATH=""` échoue (`CalledProcessError`) — sent la dérive d'environnement déjà vue côté
  `grappes` (Q36 de `QUESTIONS.md` racine), pas une régression de code.

## 908, point 4.2 — mapper les adresses serveur : fait pour Overpass et le code à constante, pas pour tout (09/11/2026)

Fait : le domaine d'une source fixée par adaptateur se lit désormais depuis une constante de module
(`ADRESSE`/`URL`/`BASE`/`API`, déjà présente dans ~18 adaptateurs) ; Overpass (`osm-overpass.yaml`) a son
adresse auto-hébergée sortie de la liste `serveurs` vers un réglage nommé `parametres.serveur_auto_heberge`,
modifiable depuis la fiche (modèle CKAN) ; le message rouge sur un paramètre `requis` vide est branché
(`reglages.js`) ; le libellé dit maintenant « Serveur contacté » et précise « (auto-hébergé) » (`mode.auto_heberge`,
nouveau champ de déclaration).

Pas fait, et pas inventé à l'aveugle :

* **SearXNG** (`moteur.definition.url`) : affiché en lecture seule (le correctif `domaine_source()` le lit
  désormais), mais PAS rendu modifiable comme Overpass — son URL est portée par le moteur « definition »
  (un mécanisme de grappes, pas de l'adaptateur `pilote`), et je ne l'ai pas assez vérifié pour savoir si le
  merge `parametres` + réglages utilisateur s'y applique de la même façon que pour un adaptateur. Risquer une
  mauvaise supposition là casserait la recherche en silence (même prudence que 9.1/Boucle).
* **RSSHub et LibreTranslate** ne sont pas des sources (`Declaration`) : leur adresse auto-hébergée vit dans
  `pilote.yaml` (`suite.rsshub_url`, `suite.traduction_url`), un réglage d'OUTIL, pas de source. Leur donner le
  même mécanisme `parametres_attendus` demanderait de les modeler en pseudo-sources — une vraie décision de
  conception, pas un mappage d'adresse.
* Les adaptateurs restants sans constante `ADRESSE`/`URL`/`BASE`/`API` (sur les ~50 cités par le retour) gardent
  « — » : je n'ai pas parcouru les ~30 fichiers restants pour en extraire l'adresse une par une (travail
  mécanique, sans jugement — candidat à `outils/appeler_gratuit.sh` plutôt qu'au compte Pro, comme le préfère
  CLAUDE.md), pas fait dans ce pavé.

