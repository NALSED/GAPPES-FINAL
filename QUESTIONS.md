# QUESTIONS — grappes

Statut au 2026-10-06. Référence unique : `FINAL.md`. Aucune réponse inventée. Rien ci-dessous n'est une condition d'avancement : chaque point a une valeur par défaut documentée.

## Ouvertes (valeur par défaut en attendant)

* **Q3** Close (D82, 2026-11-03) : normalisation multilingue reste le défaut, pas de changement tant qu'aucun cas réel multilingue ne le justifie.
* **Q10** Close (D82) : client visé = agent Claude (abonnement Pro/Max), même machine que grappes (.115 production, .250 test) ; stdio/lecture seule déjà le cas, pas d'exposition réseau nécessaire.
* **Q11** Close (D82) : pas de scoring par embeddings — moins vérifiable à l'œil que le lexique, rien ne montre que le lexique rate des recoupements ; à revoir seulement si un cas réel le montre.

* **Q20** Close (D82) : le garde-fou reste actif par défaut, mais c'était déjà un réglage réel (`autonomie.yaml: apprentissage.exiger_racine_de_confiance`, chargé par `autonomy.py`) — confirmé, rien à coder.
* **Q21** Close (D82) : remplacé par un critère de correspondance en trois cas (matche directement / hors sujet / doute → `resultat_a_trancher.csv`), pas une exclusion de principe. Détail et code : D82, `clustering/resultat.py`.

* **Q28** (nouvelle, 2026-11-03) Boucle d'apprentissage et `resultat_a_trancher.csv` (901/Q21) : la décision de Sednal sur un cas « à trancher » (garder/exclure) doit compter comme ancre de confiance (garde-fou Q20), mais le mécanisme par lequel cette décision est enregistrée et relue (quel fichier, quelle colonne) n'est pas spécifié. Défaut en attendant : aucune boucle de retour, le fichier reste un export à relire à la main.

* **Q22** Réglée (D46) : écosystèmes `rss` et `wikipedia` ajoutés comme fournisseurs. Voir Q24 pour ce qui reste.
* **Q23** Réglée (D47) : nouveau sujet, `seuil_ingestion` auto-ajustable dans [5 ; 40].
* **Q24** Close (acceptée, D56) : « probable » est le niveau maximal pour le sujet actuel ; D50 à D55 restent en place pour plus tard.

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
* **Q25** Close (D61) : aucun filtre, on garde toutes les sources ; ville = résultat de trouver-sites. Énoncé d'origine : Distinguer, dans les sorties, les articles Wikipédia d'**organisations** de ceux de **concepts ou d'événements** (trouver-sites ne peut rien trouver pour ces derniers). Faisabilité : oui, avec les catégories Wikipédia déjà lues à l'ingestion (elles servent à écarter les personnes), mais elles ne sont pas conservées en base : il faudrait les stocker. Essai à blanc sur le jeu actuel (catégories lues le 2026-10-11, 5 articles) : 4 lignes sur les 8 de `resultat.csv` seraient écartées (« Mouvements étudiants en France », « Mouvements lycéens », « Mouvement contre le contrat première embauche de 2006 », « Mouvement lycéen et étudiant de 2026 en France » : catégories « Mouvement social… », « Mouvement étudiant », « Manifestation en… », « Conflit social… », « Grève étudiante »), 1 conservée (« Union nationale des étudiants de France » : « Syndicat étudiant en France », « Organisation étudiante représentative », « Association… »). Les 3 lignes de sites web (L'Étudiant, Le Bonbon, Valeurs actuelles) ne sont pas concernées. Réserve : la règle repose sur deux listes de préfixes de catégories (événement/mouvement d'un côté, organisation de l'autre), donc sur un critère à valider ; sur d'autres sujets elle pourrait écarter à tort (ex. un mouvement qui est aussi une organisation). Si accord : filtre appliqué seulement à `resultat_tsites.csv`, ou aussi à `resultat.csv` (à préciser).

## Q26 — Autocalibration : plafond de rappel de 0 à 17 % (2026-10-12) — Close (D82, 2026-11-03)

Sur dev et validation, au plus 17 % de la référence Wikidata existe comme candidat vérifié « juste » (12 sujets mesurés) ; R-précision stricte observée 0,020 / 0,007, identique pour tous les algorithmes. Le seuil 0,90 du critère 1 est inatteignable avec des entités = sources. Pistes à chiffrer avant tout gel (rien n'est appliqué) : (a) crawl plus grand, (b) extraction d'entités nommées dans les textes lus (hors liste des méthodes de la mission, donc à décider par Sednal), (c) nom lisible des domaines. Sans changement d'architecture, le verdict sera « non certifié ».

Mesures complémentaires (2026-10-12) : (1) trois cycles de collecte successifs sur handball-pro et sur g-q56199177 (réseau réel) ne changent rien : 21 puis 37 candidats, plafond de rappel inchangé (5,9 % et 17,4 %) ; le crawl plus long ne relève pas le plafond. (2) `min_ecosystemes = 1` (autonomie, apprentissage des termes) rejoué sur les 12 sujets de dev et validation : mêmes candidats, mêmes « justes » ; aucun effet mesurable sur un cycle. Rapporté, non appliqué. (3) Un classement parfait plafonne la R-précision stricte à ≤ 0,17 ; atteindre 0,90 suppose que les ACTEURS (organisations nommées dans les textes) soient les candidats, pas les sources.

**Décision (D82)** : Sednal autorise l'extraction (b), sa seule utilité étant pour un mode de recherche précis (une recherche qui cible directement des sites/comptes n'a rien à en extraire). Nouveau réglage **`scoring.mode_recherche`**, deux valeurs fermées : `sites` (défaut, comportement actuel) ou `extraction` (lit le contenu, les acteurs nommés deviennent candidats de recoupement). Réutilise le classement de production déjà mesuré (D63-D65) plutôt que d'inventer un nouveau mécanisme. Code et tests : `config.py`, `classement/production.py::cc_pour_mode`, `tests/test_phase4.py`, `tests/test_classement_production.py`. Le gain de rappel réel (le chiffrage du plafond avec extraction activée) reste à mesurer sur un vrai cycle réseau, hors de ce sandbox.

## Q27 — D69 : trois décisions qui reviennent à Sednal (2026-10-13) — Close (D82, 2026-11-03)

Détail et chiffres : `docs/conception/cibles.md` §§ 4, 5 et 7.

* **Thésaurus de types** : décision (D82) : rattachement au code NAF officiel (INSEE) ↔ classe plutôt qu'une liste de synonymes inventée — nomenclature déjà existante et autoritaire. **Pas encore codé.**
* **Amorces par requêtes web** : mesure du mécanisme TREC autorisée par Sednal (~3 crédits Tavily/sujet), décision d'implémentation seulement après ce chiffrage. **Pas lancée ici** : coûte des crédits réels, à faire dans une session dédiée avec le budget alloué.
* **Nouveau jeu test** : confirmé nécessaire avant toute certification ; à geler juste avant la prochaine tentative, pas avant si aucune n'est encore visée. **Pas fait.**
