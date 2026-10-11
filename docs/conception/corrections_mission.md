# Correctifs proposés pour `MISSION.md`

Statut : **proposition** (`FINAL.md` § 13). `MISSION.md` est en lecture seule pour l'agent : rien n'y a été modifié. Les numéros de ligne sont ceux de `MISSION.md` au 2026-10-11. À appliquer par Sednal, ou à écarter.

## 1. Erreurs de fond

| Ligne | Texte actuel | Correctif proposé | Motif |
| --- | --- | --- | --- |
| 371 (§ 9.1) | « trois termes de poids 1 donnent ≈ 86 » | « un terme de poids 1 donne ≈ 28, trois termes ≈ 63 » (ou garder ≈ 86 et passer `scale` à 1,5) | `100 × (1 − exp(−3/3)) = 63,2`. Décision D7 : `scale = 3` conservé. |
| 558–566 (§ 11) | `confiance = 0.50 × S + 0.30 × E + 0.20 × A` | `confiance = S + (100 − S) × (0,6·E + 0,4·A) / 100` ; ancienne formule disponible par `formule_confiance: ponderee` | D15 : l'ancienne formule plafonnait à 50 sans recoupement, sous `seuil_min` (40). |
| 563 (§ 11) | `E = 100 × min(1, Σ poids des citants / (2 × min_weight_sum))` | ajouter : « **E vaut 0 tant que le recoupement n'est pas validé** » | D19 : un recoupement refusé (ex. un seul écosystème) ne doit pas suffire à classer l'entité. |
| 560–575 (§ 11) | niveaux « confirmé » ≥ 70 | « confirmé » = confiance ≥ 70 **et** recoupement validé ; sans recoupement, « probable » au mieux | `FINAL.md` § 7, D39. |
| 606–616 (§ 13.1) | `from mcp.server.fastmcp import FastMCP` ; `mcp = FastMCP("grappes")` | `from mcp.server.mcpserver import MCPServer` ; `server = MCPServer("grappes")` ; `mcp==2.3.0` épinglé | D13 : `fastmcp` n'existe plus dans `mcp` 2.3.0. |
| 696–720 (§ 17) | Q1 à Q11 | ajouter Q12 à Q14 (hook migré ; watchdog non voulu ; classification mécanique/jugement, N = 5) et Q15 à Q19 (voir `QUESTIONS.md`) | Questions citées dans le texte mais absentes de la liste. |

## 2. Sortie finale (§ 12 et « Produits finaux », ligne 31)

* Ajouter aux produits finaux : **`sorties/resultat.csv`**, une seule colonne `NOM` (organisations, médias, sites, canaux, comptes institutionnels ; noms lisibles ; variantes fusionnées ; tri alphabétique ; UTF-8 sans BOM), et `resultat_<grappe>.csv` quand il y a plusieurs grappes. Personnes physiques exclues par défaut (`inclure_personnes: false`). Voir D32.
* Le § 12 décrit `entites.csv` et `appartenances.csv` : inchangés ; ajouter qu'un nom de personne y est masqué quand `redact_persons` est actif.

## 3. Phrases qui supposent que Sednal fournit des sources, des sites, des mots-clés ou des exports

Le principe de `FINAL.md` § 1–2 : le système trouve lui-même ses sources ; Sednal ne fournit que des sujets, des clés de fournisseurs, des limites et l'interrupteur `autonome`.

| Ligne | Texte actuel | Réécriture proposée |
| --- | --- | --- |
| 18 | « transforme des JSON bruts multi-sources » | « transforme des contenus publics collectés automatiquement (et, au besoin, des JSON fournis) en une base structurée » |
| 24 (schéma) | `JSON bruts ─▶ Fetchers ─▶ Observations` | ajouter en amont : `Sujets ─▶ Recherche (multiprise) ─▶ Pages publiques` |
| 180 (§ 5) | « Ingestion de JSON bruts fournis de l'extérieur » | « Collecte automatique de sources publiques ; les fichiers JSON restent acceptés comme lecteurs de secours » |
| 358 (§ 8.2) | « Phase 1 : momo propose un schéma ... et le soumet à Sednal (Q2). » | supprimer la soumission à Sednal : les formats réels se tranchent sur les premières données collectées (Q16 à Q19) |
| 462 (§ 9.3) | « Les vrais lexiques sont fournis par Sednal. » | « Le lexique de départ de chaque sujet est amorcé automatiquement à partir de sa phrase ; Sednal n'en fournit pas. » |
| 701 (Q2) | « Peux-tu fournir 2-3 exemples de JSON bruts ? » | marquer « sans objet : plus une condition d'avancement » |
| 669–680 (§ 15) | phases 0 à 6 | ajouter les phases 7 et suivantes de `FINAL.md` § 14 (multiprise, amorçage, récupérateur, ingestion automatique, boucle) et retirer toute validation par Sednal |
| 53–55 (§ 2.1) | pilotage par les issues `NALSED/agent-momo` | indiquer que `gh` n'est pas installé et que le pilotage se fait par fichiers et par tmux |

## 4. Ce qui reste valable tel quel

Principes d'architecture (§ 6), modèles (§ 7), scoring (§ 9 hors l'exemple), recoupement (§ 10), stockage SQLite, serveur MCP en lecture seule (hors l'import), CLI de base. La migration d'environnement (§ 4) est faite ; le hook `Stop` pointe vers ce dépôt.
