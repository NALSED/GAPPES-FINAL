# Réponses de Sednal — 06/10/2026

Appliquer dans l'ordre. Tout reste « proposée » dans DECISIONS.md tant que Sednal ne l'a pas passé à « actée ».

## 1. D7 : scale

On garde scale = 3.0 (configurable par grappe). La phrase « ≈ 86 » de MISSION était une erreur de Sednal. Corrige-la dans ta doc : un terme de poids 1 donne ≈ 28, trois termes ≈ 63.

## 2. D12 / D15 : formule de confiance

Remplace la formule de confiance par :

conf = S + (100 − S) × (0.6·E + 0.4·A) / 100

Sans citations, conf = S. Conserve l'ancienne formule (0.5 / 0.3 / 0.2) comme option dans config/scoring.yaml.

Mets à jour assign.py, config/scoring.yaml, les tests (cas : S seul, E seul, A seul, tous), les exports et la doc.

Enregistre-le en D15 (proposée), avec le motif : l'ancienne formule plafonnait à 50 sans recoupement, sous un seuil_min de 40.

## 3. D13 : SDK MCP

Confirme dans DECISIONS.md que mcp.server.fastmcp n'existe plus en mcp 2.3.0 et que l'import correct est mcp.server.mcpserver.MCPServer. Sednal met MISSION §13.1 à jour.

## 4. Réponses aux questions

* QA : confirmé, tu suis MISSION.md (grappes).
* Q1 : garde « grappes » comme nom de travail.
* Q12 : réglée (hook migré, vérifié).
* Q13 : pas de watchdog pour l'instant. Note chaque interruption « session limit » dans ETAT.md.
* Q14 : classification mécanique / jugement validée, N = 5 (atteint : 8 lignes).
* Q4, Q5, Q9 : garde les valeurs actuelles (CSV ; UTF-8 sans BOM, règle d'opposition par marge, seuils par défaut). Provisoire, à recalibrer avec des données réelles.
* Q2, Q3, Q7, Q10, Q11 : pas encore de réponse. N'invente rien.
* Q12 à Q14 manquent dans le §17 de MISSION.md : Sednal les ajoute. Ne touche pas à MISSION.md.

## 5. QC : phase 7

Pas de phase 7 « données réelles » tant que Sednal n'a pas fourni des JSON anonymisés (Q2) et répondu à Q7 (base légale, conservation, redact_persons). N'ingère aucune donnée réelle avant la réponse à Q7.

## 6. En attendant

a. Revue de code complète (entrées vides, doublons, encodages, très longs textes, dates absentes, citations circulaires), avec tests ajoutés.
b. Corpus synthétique plus riche : thèmes neutres, 3 écosystèmes, ~2 000 observations, avec des cas de recoupement validés, refusés et ambigus. Vérifie le pipeline complet dessus.
c. Test du serveur MCP sur ce corpus, avec la requête « les 10 sources les plus influentes de la Grappe A ».
d. Plan de phase 7 écrit dans DECISIONS.md (proposée), sans l'exécuter : ingestion de données réelles, calibrage des seuils, formats JSON réels.

## 7. Règles inchangées

* Pas de modification de ~/.claude/settings.json.
* Pas de donnée réelle vers le compte gratuit ; tâches mécaniques via appeler_gratuit.sh.
* gh reste absent : le pilotage continue par tmux et par ce fichier.

## 8. Retour attendu

Mets ETAT.md et QUESTIONS.md à jour, puis résume en 10 lignes maximum ce qui est fait et ce qui bloque.
