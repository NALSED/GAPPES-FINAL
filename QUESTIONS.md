# QUESTIONS — grappes

Statut au 2026-10-06. Référence unique : `FINAL.md`. Aucune réponse inventée. Rien ci-dessous n'est une condition d'avancement : chaque point a une valeur par défaut documentée.

## Ouvertes (valeur par défaut en attendant)

* **Q3** Langues des corpus ? Défaut : normalisation multilingue (accents latins retirés, autres écritures intactes).
* **Q10** Clients MCP visés et lieu d'exécution ? Défaut : serveur MCP stdio en lecture seule.
* **Q11** Scoring par embeddings plus tard, oui ou non ? Défaut : non (lexique et recoupement).

* **Q20** Garde-fou de la boucle d'apprentissage (D41) : une entité confirmée n'enseigne des mots que si elle descend d'une ancre ou d'une source trouvée par la recherche. Sans ancre et avant la première recherche réelle, rien n'est appris. Faut-il relâcher cette exigence (`apprentissage.exiger_racine_de_confiance: false`) ? Défaut : non, par prudence.
* **Q21** Personnes physiques (D32) : exclues de `resultat.csv` par défaut ; un compte X ou Instagram sans indice institutionnel explicite dans son nom est traité comme une personne (« en cas de doute, une personne »). La liste d'indices est intégrée (`resultat.indices_institution` pour la remplacer). Défaut : à garder.

* **Q22** Réglée (D46) : écosystèmes `rss` et `wikipedia` ajoutés comme fournisseurs. Voir Q24 pour ce qui reste.
* **Q23** Réglée (D47) : nouveau sujet, `seuil_ingestion` auto-ajustable dans [5 ; 40].
* **Q24** (bloquant, constat du cycle réel du 2026-10-11) Aucun recoupement entre écosystèmes n'a lieu : les sites cités par plusieurs sources le sont uniquement par des articles Wikipédia, et un élément RSS ne cite personne (titre, résumé et adresse de son propre article seulement). Les pages web pouvant citer les mêmes sites sont rares. Voies, qui changent la règle de recoupement ou le sens de « écosystème » : (1) un flux qui cite son propre site (auto-corroboration, déconseillé) ; (2) extraction d'entités nommées dans le texte des éléments RSS pour les relier à des sites (fonctionnalité nouvelle) ; (3) beaucoup plus de pages web par cycle (quotas et seuil de proximité plus larges : plus de bruit, plus de requêtes sur des sites tiers) ; (4) accepter « probable » pour ce sujet tant qu'un autre écosystème qui cite réellement des sites n'est pas branché. Défaut : (4), rien n'est modifié.

## À trancher sur les premières vraies données collectées (Q16 à Q19)

Aucun export n'est attendu de Sednal (`FINAL.md` § 3) : ces points se tranchent sur les premières données réellement ramenées par la collecte, quelle qu'en soit l'origine. Les formats actuels viennent d'échantillons construits d'après les documentations officielles ; aucun champ n'a été supposé au-delà (détail dans `docs/conception/formats_json.md`).

* **Q16** Telegram (export Desktop) :
  * l'URL d'un `text_link` est-elle bien dans `href` ? L'échantillon n'en contient pas ; le fetcher lit `href`, à défaut `url` ;
  * champs des messages de service (`action`, `actor`...) : ils sont seulement ignorés ; certains portent-ils une information utile (ajout de membres, épinglage) ?
  * l'export ne donne que le nom affiché du canal (`name`), pas son nom public : l'identifiant vient de la table d'équivalence de configuration (D25, référence), à défaut du nom mis en forme, marqué « hypothèse ». Existe-t-il un champ de nom public dans les vrais exports ?
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
* **Q19** Web (partiellement confirmée le 2026-10-11, voir `ETAT.md`) : le format d'entrée est une proposition de Sednal (aucun standard). `published_at` préféré à `fetched_at`, `canonical_url` préférée à `url`, `links[].anchor` ignoré. Format réel du collecteur à fournir.

## Réglées ou provisoires

* **Q7** Cadre de données : valeurs proposées par Claude (D30) — sources publiques seulement, `retention_days` 90, `redact_persons` actif, personnes physiques exclues de `resultat.csv` — réversibles par Sednal ; elles remplacent D20 et D21.
* **Q15** Réglée (D19) : E vaut 0 tant que le recoupement n'est pas validé ; `explain` indique `recoupement_partiel`.
* **Q1** Réglée : « grappes » reste le nom de travail.
* **Q4, Q5, Q9** Valeurs actuelles gardées (seuils par défaut ; CSV `;`, UTF-8 sans BOM ; règle d'opposition par marge). Provisoire, à recalibrer avec des données réelles.
* **Q6** Thèmes neutres de démonstration conservés (jeux d'essai ; les vraies grappes viennent des sujets).
* **Q8** Sans objet (plage horaire supprimée).
* **Q12** Réglée : hook `Stop` migré et vérifié.
* **Q13** Pas de watchdog pour l'instant (D4 reste « proposée »). Chaque interruption « session limit » est notée dans `ETAT.md`.
* **Q14** Classification mécanique / jugement validée ; N = 5, atteint (8 lignes dans le journal).
* **QA** Confirmé : on suit `MISSION.md` (`grappes`).
* **QB** Réglée : hook `Stop` vers `/opt/grappes/outils/continuer.sh`.
* Corrections de `MISSION.md` (dont les Q12 à Q19 manquantes du §17) : proposées dans `docs/conception/corrections_mission.md` ; `MISSION.md` n'est pas modifié.
