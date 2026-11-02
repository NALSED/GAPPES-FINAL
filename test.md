# test.md — Review totale et grand test, instructions pour momo

Document écrit le 26/10/2026, pour momo. À lancer **une fois tout le reste du dépôt implémenté** :
`pilote/` entier (WebUI), `pilote/17-sources-a-implementer.md` (sources branchées), `source.md` et
`15-mecanismes-et-references.md` (Splink pour Fusion/doublons, etc.). Si une de ces pièces manque encore,
dis-le à Sednal plutôt que de commencer le test sur une base incomplète.

Trois temps, dans cet ordre :

1. **Review totale** — toi seul, avant que Sednal regarde quoi que ce soit. Une check-list, pas une
   impression.
2. **Partie 1 — sorties connues** : on sait déjà ce que grappes doit trouver, on vérifie qu'il le trouve
   vraiment, et qu'il ne dit pas faux avec assurance.
3. **Partie 2 — grandeur réelle, sans filet** : on pousse le programme dans ses retranchements, sans se
   retenir sur le volume, pour voir ce qu'il donne quand personne n'a préparé la réponse à l'avance.

Rien ici n'est une méthode inventée pour l'occasion — chaque partie reprend une méthode existante,
documentée, utilisée ailleurs. Le détail et les liens sont en bas (section « Sources »).

---

## 1. Review totale

Avant toute chose, repasse sur **les huit règles non négociables de `pilote/00-MAIN.md`**, une par une,
et note pour chacune *rempli* / *pas rempli* / *partiellement* avec un exemple concret (pas juste « oui ») :

1. L'original est toujours gardé — une traduction, un résumé, un rapprochement s'ajoutent, rien n'écrase.
2. Tout ce qui sort d'une IA porte la marque « IA », du début à la fin, sans qu'elle puisse se perdre en
   route.
3. Rien n'est écrit en dur — jetons de charte, mots de `charte/nommage.md`, noms de sources en config.
4. *Retirer* ne touche aucun fichier ; *Supprimer* est définitif et confirmé. Vérifie que le code ne les
   confond nulle part.
5. Les mots affichés sont ceux de `charte/nommage.md`, aucun autre.
6. L'utilisateur agit, le programme (et l'Aide) ne font qu'proposer — aucune action automatique sans un
   bouton pressé par une personne.
7. Rien d'essentiel ne dépend d'un modèle de langue — débranche l'IA (ou mets-la hors quota) et vérifie
   que l'Aide, `verifier_plan()` et les préréglages marchent encore.
8. Aucune fonction de recherche par nom de personne physique ; les données de dirigeants ne sont jamais
   une clé de rapprochement (voir `pilote/14-questions-ouvertes.md` §8).

Ensuite, repasse les points précis suivants, chacun avec un exemple réel à l'appui :

- **Clé d'API** : jamais affichée en clair nulle part (page, journal, export) — seulement « clé
  enregistrée ».
- **Fiabilité A–F** sur chaque source configurée (`pilote/05-reglages-sources.md`), et le champ
  **Langue**.
- **Onglet Tri** (`pilote/16-onglet-tri.md`) : la file est triée du rapprochement le moins certain au
  plus certain, *Confirmer* et *Séparer* ne suppriment rien, et « Déjà tranchés » garde la trace de
  chaque décision.
- **Assistant IA** éteint par défaut, l'avertissement s'affiche avant de l'allumer, et il reste possible
  de s'en servir sans jamais l'allumer.
- Toutes les sources listées « P1 » dans `pilote/17-sources-a-implementer.md` répondent réellement — pas
  seulement présentes dans la configuration.

**Rends un rapport texte**, une ligne par point ci-dessus, *rempli* / *pas rempli* / *partiellement*, avec
l'exemple qui le prouve. Un point « partiellement » ou « pas rempli » n'empêche pas de passer à la suite,
mais doit être signalé — ne corrige pas en silence un écart à une règle sans le dire.

---

## 2. Partie 1 — sorties connues : est-ce que grappes dit vrai ?

**Principe** : on construit des cas où la bonne réponse est déjà écrite avant de lancer grappes, puis on
compare. C'est la méthode la plus ancienne et la plus éprouvée en recherche d'information — le
**paradigme de Cranfield**, celui des campagnes TREC depuis les années 1990 : un jeu de requêtes, une
vérité-terrain, un score. Rien à inventer, seulement à appliquer.

### 2.1 Fusion/doublons (Splink) — la vérité-terrain existe déjà en kit

**Avant de commencer, deux choses à ne pas confondre — voir `pilote/18-calibrage-26.10.2026.md` §2 pour
le détail :**

- Le jeu décrit ci-dessous (FEBRL / `recordlinkage`) est un jeu **externe**, sans aucun rapport avec
  `autocal/jeux.json`. Le faire tourner ne touche à rien du système de certification de grappes.
- **N'exécute jamais `python -m grappes.autocal.test_final` sans l'option `--essai dev` ou
  `--essai validation`.** Le jeu test (`autocal/jeux.json["test"]`) a déjà été ouvert une fois, le
  12/10/2026, et il est **brûlé** : une seconde ouverture est refusée par le code et consignée comme une
  tentative de brûlage, elle n'est pas une mesure à refaire « pour voir ». Si tu veux rapporter la mesure
  déjà faite ce jour-là (critères 1 à 8 de `docs/CERTIFICATION.md`), restitue-la **telle qu'elle existe**
  (fichiers déjà produits côté VM), ne la relance pas.
- Cette mesure autocal rejoue des données déjà archivées, zéro réseau : elle ne dit rien sur la vérité
  des sources **en direct**. C'est ce que couvre 2.2 ci-dessous — les deux parties se complètent, elles
  ne font pas le même travail.

Fusion/doublons est Splink (voir `pilote/15-mecanismes-et-references.md` §1). Splink a sa propre
méthode de contrôle qualité, directement réutilisable :

1. Prendre un jeu de fiches avec une **colonne vérité** indiquant quelles fiches désignent la même
   entité (un identifiant de cluster). La bibliothèque `recordlinkage` (Python) et **FEBRL** fournissent
   des jeux **déjà prêts**, avec des doublons fabriqués exprès (fautes de frappe, variantes de nom,
   champs manquants) — ne pas construire ce jeu à la main, le prendre tout fait.
2. Faire tourner grappes sur ce jeu, laisser Fusion/doublons proposer ses rapprochements.
3. Comparer **les propositions à la vérité-terrain** à chaque seuil de score : combien de vrais
   positifs, faux positifs, faux négatifs. Splink fait ça nativement (`truth_space_table_from_labels_column`
   dans sa propre documentation) — reprendre la même logique sur les sorties de grappes plutôt que d'en
   écrire une autre.
4. **Lire un par un les faux positifs et les faux négatifs**, pas seulement le chiffre global. C'est là
   que se voient les vrais défauts (deux associations homonymes dans des villes différentes confondues,
   par exemple).
5. Refaire la même chose avec un jeu de fiches **françaises réelles mais déjà connues** (quelques
   associations ou entreprises que tu connais toi-même, dont tu sais à l'avance si elles sont dupliquées
   dans les sources branchées ou non) — le jeu synthétique teste l'algorithme, le jeu réel teste le
   branchement complet.

### 2.2 Chercher, Vérifier, Enrichir — des requêtes dont tu connais déjà la réponse

Construire une **dizaine de requêtes** par catégorie (entreprises, associations, organisations
officielles, presse, lieux) dont tu connais la bonne réponse avant de lancer grappes — une entreprise que
tu sais radiée depuis telle date, une association que tu sais basée à telle adresse, un article que tu
sais avoir été publié par telle rédaction à telle date. Lance la recherche, et vérifie :

- **CHERCHER** trouve bien la fiche, et seulement celle-là (pas une homonyme).
- **VÉRIFIER** confirme ce que tu sais vrai et signale ce que tu sais faux ou périmé — ne se contente pas
  de dire « trouvé », il doit redire **ce qu'il a confirmé**.
- **ENRICHIR** ajoute des informations correctes, traçables jusqu'à la source qui les a données.

### 2.3 La fiabilité et la crédibilité affichées sont-elles honnêtes ?

Pour chaque fiche produite dans ce test, vérifie que la **fiabilité (A–F)** affichée correspond à ce que
tu sais réellement de la source (une source officielle ne doit jamais sortir en D), et que deux sources
qui ne font que se recopier **ne comptent pas comme une double confirmation** — un des pièges documentés
du code Admiralty (`pilote/15-mecanismes-et-references.md` §2).

### 2.4 L'Assistant IA et l'Aide ne doivent jamais se confirmer eux-mêmes

Règle directement issue d'une norme de vérification OSINT réelle (OWASP OOVS, exigence n°8) :
**« une sortie automatisée ne confirme jamais ses propres entrées. »** Concrètement : allume l'Assistant
IA sur un des cas connus de 2.2, et vérifie que ce qu'il produit reste marqué « IA » et n'est jamais
compté comme la confirmation d'un fait — même s'il tombe juste.

### Ce que tu rends pour la partie 1

Un tableau : cas de test → résultat attendu → résultat obtenu → conforme oui/non. Pour Fusion/doublons,
ajoute le tableau précision/rappel par seuil, et la liste des faux positifs/négatifs avec leur score.

---

## 3. Partie 2 — grandeur réelle, sans filet

**Principe** : ici on ne sait pas à l'avance ce que ça va donner — c'est fait pour. Mais « sans
contrainte » ne veut pas dire sans méthode, sinon le résultat n'est qu'une impression. La méthode
existante pour ça s'appelle le **test exploratoire en sessions** (*Session-Based Test Management*) :
chaque session a **une seule mission** (une « charte »), une durée fixée à l'avance, et à la fin un
rapport court — ce qui a été essayé, ce qui a été trouvé, ce qui reste à essayer. Pas de script à suivre
pendant la session elle-même : c'est le but.

**Sur le volume** : pousse vraiment, ne te retiens pas par prudence. Lance des recherches réelles sur
toutes les catégories, sur plusieurs pays, avec des plans de travail qui branchent plusieurs sources à la
fois. Les seules limites qui doivent t'arrêter sont les **quotas réels** de chaque source (et ça, c'est
justement une chose à observer, pas à éviter — voir 3.2).

### 3.1 Exemples de chartes à essayer (adapte, en invente d'autres)

- « Pendant 30 minutes, trouve autant d'entreprises radiées ou en liquidation que possible, et regarde
  si VÉRIFIER le détecte correctement à chaque fois. »
- « Pendant 30 minutes, construis le plan de travail le plus chargé possible — toutes les catégories,
  Traduction, Assistant IA allumé — et regarde ce qui casse ou ralentit. »
- « Pendant 20 minutes, cherche des noms d'associations ambigus ou très proches entre eux, et regarde ce
  que Fusion/doublons en fait. »
- « Pendant 20 minutes, utilise l'Aide pour des questions de plus en plus tordues, et essaie de la
  faire répondre à côté ou inventer une source qui n'existe pas. »

### 3.2 Faire exprès de casser des choses (injection de panne)

Pratique courante pour tester la résistance d'un système qui dépend de services externes : provoquer
volontairement l'échec plutôt que d'attendre qu'il arrive seul.

- Éteins une source **en plein milieu** d'une recherche en cours — grappes doit continuer sur les autres
  sources et dire clairement laquelle a manqué, pas planter ni se taire.
- Pousse une source jusqu'à son quota réel et observe ce qui se passe au-delà : message clair, source
  marquée, pas de boucle qui recommence indéfiniment.
- Mets une mauvaise clé d'API et vérifie que l'erreur remonte lisiblement, sans jamais afficher la clé
  elle-même.
- Lance une recherche avec une saisie dans une langue que les sources ne couvrent pas, sans avoir allumé
  Traduction — vérifie que c'est signalé (c'est exactement ce que `verifier_plan()` doit faire).

### 3.3 Ce qu'il faut noter à chaque session

Pas de format figé, mais toujours : la charte (la mission du moment), la durée réelle, ce qui a été
essayé, ce qui a surpris (en bien ou en mal), et toute chose qui casse une des huit règles de la section 1
— un rapprochement non traçable, une action automatique sans bouton pressé, un mot qui n'est pas dans
`charte/nommage.md`.

### Ce que tu rends pour la partie 2

Un rapport par session (charte, durée, constats), et une liste séparée des anomalies trouvées, chacune
avec les étapes pour la reproduire.

---

## 4. Avant de tout soumettre à Sednal

Les trois rapports (review, partie 1, partie 2) vont à Sednal **tels quels**, y compris ce qui est
« pas rempli » ou « anomalie » — ne résume pas en « tout va bien » si un point précis dit le contraire.
C'est lui qui décide de la suite, pas une moyenne de ces résultats.

---

## Sources

**Méthode de test à sorties connues**
- Paradigme de Cranfield et collections de test en recherche d'information : https://www.ccs.neu.edu/home/vip/teach/IRcourse/IR_surveys/FnTIR.pdf
- OWASP OOVS, norme de vérification OSINT (dix exigences, dont « une sortie automatisée ne confirme jamais ses propres entrées ») : https://owasp.org/OWASP-Open-Source-Intelligence-Standard/requirements.html
- Méthode de contrôle qualité de Splink à partir d'une colonne vérité-terrain : https://nbviewer.org/github/moj-analytical-services/splink_demos/blob/max_pair/example_accuracy_analysis_from_labels_column.ipynb
- Jeux de données de test pour le rapprochement d'entités (`recordlinkage`, FEBRL) : https://recordlinkage.readthedocs.io/en/stable/ref-datasets.html

**Méthode de test exploratoire**
- Session-Based Test Management (James et Jonathan Bach) : https://ryancraventech.substack.com/p/session-based-test-management
- Injection de panne / chaos testing sur des API : https://www.gravitee.io/blog/chaos-testing-techniques
