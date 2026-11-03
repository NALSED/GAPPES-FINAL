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

## 3.8.09 — Assistant IA : code prêt, agent pas installé sur .115

`suite_ia.py` (appel silencieux à l'agent Claude Code, `claude -p … --model …`) et le registre
`operations_ia/` (résumer, classer, extraire des mots-clés — extensible comme `formats/`) sont écrits et
testés avec l'agent **simulé** (aucun agent réel n'est accessible dans ce bac à sable). Pas câblés dans
`pont/executer.py` : `NON_APPLIQUES["ia"]` reste tel quel.

Reste à faire, sur .115, avant de câbler pour de vrai :

* Installer l'agent Claude Code, le connecter une fois avec l'abonnement Pro/Max de Sednal (même principe
  que `/areas/agent-ia.md` sur .250).
* Vérifier que `claude --model <nom>` liste bien les modèles disponibles comme la spec le suppose (pour le
  menu fermé « Modèle » de la tuile) — pour l'instant « Modèle » est un champ texte libre, faute de pouvoir
  l'interroger ici.
* Confirmer si l'agent installé expose un réglage d'effort de raisonnement en ligne de commande ; sinon le
  champ « Effort » de la spec ne s'ajoute pas (elle le permettait).
* Décider comment séparer, dans le journal, le coût de l'appel à l'agent (facturé par l'abonnement, pas par
  appel) du compteur budget en crédits (3.8.08) — la spec le demande explicitement, je n'ai rien inventé.

## 3.8.10 — RSSHub : code prêt, instance pas déployée

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
