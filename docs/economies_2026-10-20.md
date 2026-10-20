# Point sur l'économie de jetons : ccr et rtk (2026-10-20)

Chiffres relevés le 20/10/2026. **Mesuré** signifie lu dans une base qui compte les jetons. **Estimé** signifie calculé par l'outil lui-même (rtk compte octets ÷ 4). Rien n'est inventé ; ce qui n'est pas mesurable est dit.

## 1. Côté Pro (compte principal) : d'où viennent les jetons

Source : `ccusage daily` (transcriptions locales de Claude Code, tous projets du compte `sednal`), du 04/10 au 20/10. **Mesuré.**

| Poste | Jetons | Part |
|---|---|---|
| Lectures de cache (contexte relu à chaque tour) | 1 210 M | **98,3 %** |
| Écritures de cache (ce qui entre dans le contexte) | 16,2 M | 1,3 % |
| Sorties du modèle | 4,84 M | 0,4 % |
| Entrées hors cache | 0,01 M | ~0 % |
| **Total** | **1 231 M** | |

Équivalent au tarif de l'API (indicatif, l'abonnement Pro ne se paie pas ainsi) : 293 $.

**Lecture** : presque tout le volume, ce sont des **relectures du contexte**. Chaque sortie de commande qui entre dans une conversation est relue à chaque tour suivant. Raccourcir ce qui entre dans le contexte (le rôle de rtk) et raccourcir les sessions comptent donc beaucoup plus que la longueur des réponses.

## 2. rtk

Source : `rtk gain` (toutes portées) et `rtk gain -d`. **Estimé** par rtk (octets ÷ 4), uniquement sur la sortie qu'il intercepte.

* Affiché : 2 649 commandes, 2,40 M jetons d'entrée, **1,84 M « économisés » (76,6 %)**.
* **Ce chiffre est gonflé.** Quatre commandes `ls` sur `donnees/autocal…` (un dossier de plusieurs milliers de fichiers) comptent à elles seules 1,31 M, soit 71 % du total. Sans rtk, Claude Code aurait de toute façon tronqué ces sorties (au-delà d'environ 30 Ko, la sortie est rangée dans un fichier). Ces 1,31 M n'auraient donc jamais été lus : ce n'est pas une économie réelle.
* **Économie crédible : environ 0,53 M jetons estimés** sur environ 1,09 M interceptés (environ 48 %). Elle vient surtout de `read` (402 K, lectures de fichiers résumées), `find` (28 K), `grep` (47 K) et `git log` (10 K).
* Ordre de grandeur : 0,53 M sur les 16,2 M écrits dans le contexte, soit **environ 3 %** de ce qui entre. L'effet réel est plus grand, car un jeton évité au tour n l'est aussi à chaque relecture suivante. Ce multiplicateur **n'est pas mesurable** avec les données disponibles, je ne le chiffre pas.
* **Qualité du filtrage** : 0 rappel sur 150 coupures (`rtk gain --recalls`). Aucune coupure n'a forcé l'agent à revenir chercher la sortie complète, donc rtk ne coûte pas de tours en plus. 28 échecs d'analyse, tous rattrapés (repli sur la sortie brute).
* Par projet : grappes affiche 89,5 %, mais c'est la même illusion (les 4 `ls` y sont). pilote affiche 13,4 % (beaucoup de `pytest`, peu compressible). Note : mes commandes de ce jour sont comptées sous grappes, car le shell repart de `/opt/grappes` à chaque appel.
* Aujourd'hui : 63 commandes, 3,3 K économisés (5,8 %). Le travail du jour, des tests et des éditions, se compresse mal.

## 3. ccr (compte gratuit `sednal-free`, OpenRouter)

Source : `~sednal-free/.claude-code-router/app-data/usage.sqlite`, lue en lecture seule. **Mesuré**, requête par requête.

| Jour | Modèle | Requêtes | Jetons (entrée + sortie + cache) |
|---|---|---|---|
| 04/10 | cohere/north-mini-code:free | 22 | 84 030 |
| 04/10 | nvidia/nemotron-3-ultra:free | 16 | 249 232 |
| 13/10 | nemotron | 10 | 136 424 |
| 14/10 | divers (essais de modèles) | 10 | 0 |
| 15/10 | cohere + gemma + nemotron | 8 | 31 545 |
| 17/10 | cohere + nemotron | 19 | 71 950 |
| 19/10 | cohere + nemotron | 12 | 250 139 |
| **Total** | | **97** | **823 320** |

* Répartition : entrée 750 888, cache lu 56 160, **sortie 16 272 seulement**.
* **Taux d'échec : 26 requêtes sur 97 (27 %)** : 16 erreurs 400, 4 limites 429, 1 erreur 404, 5 sans réponse.
* Par requête réussie (71) : en moyenne **10,6 K jetons d'entrée pour 230 jetons de sortie**.
* Le journal de grappes (`donnees/.journal_ccr.log`, 30 tâches : 17 le 06/10, 6 le 13/10, 7 le 19/10) **ne se recoupe pas** avec la base de ccr : 17 tâches le 06/10 dans le journal, aucune requête ce jour-là dans la base, mais 38 le 04/10. Le coût par tâche n'est donc pas calculable proprement ; seul le coût par requête est sûr.
* **Ce que ça économise vraiment sur le Pro.** Pas 823 K. Chaque appel `claude -p` envoie tout le contexte de Claude Code (10,6 K jetons d'entrée en moyenne par requête) pour produire une petite fixture. Fait directement sur le Pro, le même travail aurait coûté la sortie (environ 16 K jetons sur toute la période) plus la place de la fixture dans le contexte, relue ensuite à chaque tour. L'économie réelle est donc de l'ordre de **quelques dizaines de milliers de jetons, plus l'effet des relectures** : faible au regard des 1 231 M du Pro (moins de 0,1 % même en comptant 823 K entiers).
* Aujourd'hui : **0 appel gratuit**. Le travail du jour (retrait, interface, revue, tests) était du jugement ; `ruff` a tourné en local sans IA, comme le prévoit CLAUDE.md.

## 4. L'outil de suivi existant ne mesure rien

`outils/comparer_tokens.sh` a écrit quatre lignes dans `donnees/.economies_tokens.csv`, dont trois à zéro, et le côté gratuit est toujours à 0. Il interroge OpenRouter avec `OPENROUTER_MANAGEMENT_KEY`, **absente** de l'environnement, donc sa colonne « gratuit » est fausse. La donnée existe pourtant localement dans la base d'usage de ccr. `ECONOMIES.md` (généré le 11/10) est périmé.

## 5. Conclusions et leviers, par ordre d'effet

1. **Le gros poste, ce sont les relectures du contexte (98 %).** Les leviers efficaces : sessions plus courtes ou compactées plus tôt, ne pas laisser entrer de longues sorties (journaux de pytest : utiliser `-q` et `| tail`, ce qui est déjà fait), lire les fichiers par tranches.
2. **rtk fait son travail** (environ 48 % sur ce qu'il intercepte, zéro rappel). Mais le « 76,6 % » affiché ne doit pas servir de chiffre d'économie : il est faussé par 4 commandes. Une remise à zéro (`rtk gain --reset`) donnerait des chiffres propres à partir d'aujourd'hui. **Je ne l'ai pas faite** : elle efface l'historique, c'est à vous de décider.
3. **ccr apporte peu tel qu'il est utilisé.** Environ 10,6 K jetons d'entrée par requête pour environ 230 jetons utiles, et 27 % d'échecs. Pour qu'il serve : grouper plusieurs fixtures dans un seul appel, et éviter `claude -p` pour une tâche qu'un script fait seul.
4. **Réparer la mesure** : faire lire à `comparer_tokens.sh` (ou `bilan_jetons.py`) la base `usage.sqlite` de ccr au lieu de l'API OpenRouter, puis régénérer `ECONOMIES.md`. Petit changement, je peux le faire si vous le voulez.
