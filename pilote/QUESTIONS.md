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
une tâche de Sednal, séparée, pas un blocage. Coût : un simple compteur (« n appels IA ») dans le journal,
sans plafond, jamais mêlé au compteur crédits (facturé par l'abonnement, pas par appel) — tranché, rien à
inventer.

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

## 3.8.10 — RSSHub : code prêt, instance pas déployée

**Correction (revue 902)** : la spec 3.8.10 confie bien le déploiement à momo (« Déployer une instance RSSHub
auto-hébergée, image Docker officielle ») — l'hébergement avait été décidé avec Sednal, pas le geste. Écart à
reprendre, avec la réutilisation de `flux_rss.telecharger`/`lire_flux` au lieu de l'appel HTTP propre à
`suite_rsshub.py` (duplication relevée par la revue).

`suite_rsshub.py` résout l'adresse d'un flux produit par une instance RSSHub pour un site donné, et
`config.suite_rsshub_url` existe. Pas câblé dans `pont/executer.py` (vers `flux_rss.py`) :
`NON_APPLIQUES["rsshub"]` reste tel quel.

**Le contrat exact de l'API RSSHub n'est pas vérifié** : aucune instance n'est accessible ici. J'ai supposé
une route `{rsshub_url}/site/<domaine>`, mais RSSHub expose en réalité des routes PROPRES à chaque site
(`/twitter/user/x`, pas un point d'entrée générique « transforme cette adresse ») — la bonne route dépend du
type de site, pas seulement de son domaine. À revoir avec une vraie instance déployée (image Docker
officielle, décidée avec Sednal) avant de câbler le reste.

## Trou d'infra pré-existant, hors de ce pavé

`grappes.racine` dans la configuration livrée de `pilote/` pointe vers un dossier `grappes/` voisin
(`pilote/../grappes`), qui n'existe pas dans ce dépôt (le moteur est en `src/grappes`, pas `grappes/` à la
racine). Toute recherche réelle (`test_suite_plan_moteur.py`, `test_f12_recherches.py`, etc.) échoue donc par
« la configuration de grappes est introuvable » — déjà identifié dans `000-INDEX.md` (`900-demenagement-du-code.md`,
explicitement hors de ce pavé, « à valider » avant de vider `grappes/` et `pilote/` de GRAPPES). Je ne l'ai pas
touché : ce n'est pas mon rôle de le trancher seul, et plusieurs tuiles du pavé (3.8.04, 3.8.07, 3.8.09, 3.8.10)
ne pourront être vérifiées pour de vrai qu'une fois ce trou refermé.
