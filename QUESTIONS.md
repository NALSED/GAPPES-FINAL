# QUESTIONS — grappes

Statut au 2026-10-06, après `REPONSES_SEDNAL.md`. Aucune réponse inventée.

## Ouvertes

* **Q2** Échantillons de formats reçus (`REPONSES_SEDNAL_3.md`) : synthétiques, pas de vrais exports. Fetchers adaptés (D24 à D26) ; vrais exports toujours attendus pour la phase 7 (voir Q16 à Q19).
* **Q3** Langues des corpus ?
* **Q10** Clients MCP visés et lieu d'exécution ?
* **Q11** Scoring par embeddings plus tard, oui ou non ?

## À confirmer sur de vrais exports (REPONSES_SEDNAL_3, Q2)

Les échantillons de Sednal sont construits d'après les documentations officielles, avec des valeurs inventées. Aucun champ n'a été supposé au-delà de ces échantillons ; les points ci-dessous restent à vérifier (détail dans `docs/conception/formats_json.md`).

* **Q16** Telegram (export Desktop) :
  * l'URL d'un `text_link` est-elle bien dans `href` ? L'échantillon n'en contient pas ; le fetcher lit `href`, à défaut `url` ;
  * champs des messages de service (`action`, `actor`...) : ils sont seulement ignorés ; certains portent-ils une information utile (ajout de membres, épinglage) ?
  * l'export ne donne que le nom affiché du canal (`name`), pas son nom public : l'identifiant est le nom mis en forme (D25), ce qui fait correspondre `Canal Demo A` à `t.me/canal_demo_a` par hypothèse. Existe-t-il un champ de nom public, ou une table d'équivalence à fournir ?
  * `forwarded_from` est un nom affiché (pas d'identifiant) : même heuristique ;
  * `date` sans fuseau : `date_unixtime` (UTC) est préféré, est-ce toujours cohérent ?
  * export d'un groupe ou d'un compte complet (`chats.list`) : la structure diffère-t-elle ? Aujourd'hui seul `{name, messages}` est géré, et la source reste le chat, jamais l'auteur du message.
* **Q17** X (API v2) :
  * les mentions portent-elles toujours `username` en plus de `id` ? Sans `username`, résolution par `includes.users` si possible, sinon la mention est ignorée ;
  * `includes.users` est-il toujours présent ? Sans lui, aucun auteur n'est résolu et le tweet est rejeté ;
  * faut-il compter `referenced_tweets` (retweet, citation, réponse) et `in_reply_to_user_id` comme des citations ? Aujourd'hui seules les mentions et les liens citent ;
  * `engagement` = like + retweet + reply (quote, bookmark, impression exclus) : à valider.
* **Q18** Instagram (API Graph) :
  * `username` est-il toujours renvoyé par la liste de médias ? Sans lui, le média est rejeté ;
  * structure de `paging` (`cursors`, `next`) : ignorée, la collecte et le suivi des pages restent hors périmètre ; faut-il les gérer ?
  * les noms d'utilisateur peuvent contenir un point : le motif de mention actuel (`@\w+`) s'arrêterait au point ;
  * légende, mentions et hashtags n'ont pas d'entités structurées : extraction par expression régulière ;
  * les commentaires et `children` (carrousels) sont ignorés.
* **Q19** Web : le format d'entrée est une proposition de Sednal (aucun standard). `published_at` préféré à `fetched_at`, `canonical_url` préférée à `url`, `links[].anchor` ignoré. Format réel du collecteur à fournir.

## Réglées ou provisoires

* **Q7, Q7b** Levées par Sednal (D21) : pas de `retention_days`, pas de `redact_persons`, base légale non requise.
* **Q15** Réglée (D19) : E vaut 0 tant que le recoupement n'est pas validé ; `explain` indique `recoupement_partiel`.
* **Q1** Réglée : « grappes » reste le nom de travail.
* **Q4, Q5, Q9** Valeurs actuelles gardées (seuils par défaut ; CSV `;`, UTF-8 sans BOM ; règle d'opposition par marge). Provisoire, à recalibrer avec des données réelles.
* **Q6** Thèmes neutres de démonstration conservés (cuisine, jardinage).
* **Q8** Sans objet (plage horaire supprimée).
* **Q12** Réglée : hook `Stop` migré et vérifié.
* **Q13** Pas de watchdog pour l'instant (D4 reste « proposée »). Chaque interruption « session limit » est notée dans `ETAT.md`.
* **Q14** Classification mécanique / jugement validée ; N = 5, atteint (8 lignes dans le journal).
* **QA** Confirmé : on suit `MISSION.md` (`grappes`).
* **QB** Réglée : hook `Stop` vers `/opt/grappes/outils/continuer.sh`.
* **QC** Réglée : phase 7 « données réelles » dès que Q2 est livrée (Q7 levée, D21).
* Q12 à Q14 manquent dans le §17 de `MISSION.md` : Sednal les ajoute (je ne touche pas à `MISSION.md`).
