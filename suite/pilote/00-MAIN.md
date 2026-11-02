# grappes — pilote WebUI : ce qu'il y a à construire

Document principal. Il dit **quoi faire, dans quel ordre, et ce qui n'est pas négociable**. Chaque chose
à implémenter a son propre document, listé plus bas. Lis celui-ci en entier avant d'ouvrir les autres.

État au 26/10/2026. Écrit par Claude sous la direction de Sednal, qui tranche. Rien ici n'est une
décision de Claude : tout a été validé point par point.

---

## 1. Ce qu'est grappes, en trois phrases

grappes interroge plusieurs sources d'information en source ouverte, puis **regroupe les résultats qui
parlent de la même entité** — ce regroupement s'appelle une grappe. L'utilisateur choisit ses sources,
les relie dans un plan de travail, et lance la recherche. Le but n'est pas le volume : c'est un
**résultat sûr et vérifiable**, où l'on sait toujours d'où vient chaque information.

Cette dernière phrase commande tout le reste. Chaque fois qu'un choix d'implémentation se présente entre
« plus de résultats » et « résultats traçables », **c'est traçable qui gagne**.

## 2. Les huit règles non négociables

Elles passent avant toute considération technique. Si une contrainte les empêche, arrête-toi et remonte
le problème plutôt que de contourner.

1. **On garde toujours l'original.** Une traduction, un résumé, un rapprochement s'**ajoutent** à côté de
   la donnée source. Rien n'écrase jamais ce qu'une source a réellement renvoyé.
2. **Tout ce qui sort d'une IA est marqué « IA ».** De sa production jusqu'à la grappe finale, sans que
   la marque puisse disparaître en chemin. Un contenu marqué IA n'est jamais compté comme un fait
   vérifié.
3. **Rien n'est écrit en dur.** Aucune couleur, taille de texte, rayon ni ombre dans le code : seulement
   les jetons de `charte/jetons.css`. Aucun nom de source en dur dans l'Aide : seulement ce que la
   configuration renvoie.
4. **Retirer n'est pas supprimer.** *Retirer* est réversible et ne touche à aucun fichier. *Supprimer*
   est définitif et passe par une fenêtre d'avertissement. Ne jamais confondre les deux dans le code ni
   dans l'interface.
5. **Les mots sont fixés.** La liste close est dans `charte/nommage.md`. Si un écran a besoin d'un mot
   qui n'y est pas, on modifie cette liste d'abord — on n'invente pas un synonyme dans un coin.
6. **L'utilisateur agit, le programme propose.** L'Aide ne pose aucune tuile, n'allume rien, ne supprime
   rien de lui-même. Toute action passe par un bouton pressé par une personne.
7. **Rien d'essentiel ne dépend d'une IA.** L'Aide, la vérification de plan, les préréglages fonctionnent
   sans modèle. Un modèle absent ou hors quota dégrade le confort, jamais la fonction.
8. **grappes vise les personnes morales, pas les personnes physiques nommées.** Entreprises,
   associations, organisations — jamais une fonction de recherche par nom de personne physique. Les
   données de dirigeants (une personne physique apparaissant sur la fiche d'une personne morale) ne
   servent jamais de clé de rapprochement. Raison et détail dans `14-questions-ouvertes.md` §8 et
   `15-mecanismes-et-references.md` §8. Tranché le 26/10/2026 — c'est la seule des sept-devenues-huit
   règles qui touche au droit plutôt qu'à l'ergonomie ; si un besoin futur semble l'exiger, remonte la
   question avant de l'écarter.

## 3. Ce qu'on construit : quatre onglets

| Onglet | État | Document |
| :-- | :-- | :-- |
| Tableau de bord | pas encore conçu | — |
| Recherche | conçu | `07`, `08`, `12` |
| Réglages | conçu | `05`, `06` |
| Tri | conçu le 26/10/2026 | `16` |

Le Tableau de bord reste **volontairement reporté** par Sednal. N'improvise rien dessus : laisse l'onglet
visible et inactif, grisé, comme dans la maquette.

## 4. L'ordre de travail

À suivre dans cet ordre. Chaque étape s'appuie sur la précédente ; prendre les choses dans le désordre
oblige à repasser derrière.

| # | Étape | Document | Pourquoi d'abord |
| :-- | :-- | :-- | :-- |
| 1 | Jetons de style | `01-charte-graphique.md` | Tout le reste s'en sert |
| 2 | Pictogrammes | `02-pictogrammes.md` | Idem |
| 3 | Vocabulaire | `03-vocabulaire.md` | Fige les libellés avant d'écrire des écrans |
| 4 | Onglets et navigation | `04-onglets-et-navigation.md` | La coquille |
| 5 | Réglages › Sources | `05-reglages-sources.md` | Sans sources, rien à chercher |
| 6 | Réglages › Outils | `06-reglages-outils.md` | Les briques du plan de travail |
| 7 | Recherche simple | `07-recherche-simple.md` | Le chemin court, qui doit marcher seul |
| 8 | Plan de travail | `08-plan-de-travail.md` | La pièce la plus lourde |
| 9 | Tuile Traduction | `09-tuile-traduction.md` | Premier outil réel |
| 10 | Tuile Assistant IA | `10-tuile-assistant-ia.md` | Après Traduction : mêmes mécanismes, plus de précautions |
| 11 | Fenêtre Aide | `11-fenetre-aide.md` | Elle lit tout le reste, donc elle vient après |
| 12 | Recherches sauvegardées | `12-recherches-sauvegardees.md` | — |
| 13 | Quotas, coûts, budget | `13-quotas-couts-budget.md` | Transverse, à câbler quand les sources tournent |
| 14 | Onglet Tri | `16-onglet-tri.md` | Après Fusion/doublons (Splink) : c'est l'écran qui valide ses propositions |
| 15 | Brancher les sources | `17-sources-a-implementer.md` | Traduit `sources-candidates-21.10.2026.md` en consigne de branchement, triée par clé et priorité |

Questions encore ouvertes : `14-questions-ouvertes.md`. **Ne les tranche pas seul** — remonte-les.

**Avant de commencer une étape, regarde `15-mecanismes-et-references.md`.** Il nomme, pour chaque partie
dure du projet, l'outil ou la norme qui la résout déjà : le rapprochement d'entités, la cotation des
sources, la traçabilité, le canevas, et le cadre légal. Le principe du projet est de ne rien réinventer.

## 5. Ce qu'il y a dans ce dossier

````
pilote/
  00-MAIN.md                      ce document
  01-charte-graphique.md          jetons : couleurs, typo, espacements, rayons, ombres
  02-pictogrammes.md              les 31 dessins et leurs règles
  03-vocabulaire.md               les mots de l'interface
  04-onglets-et-navigation.md     la coquille et la barre d'onglets
  05-reglages-sources.md          liste des sources, fiche source
  06-reglages-outils.md           tuiles outils, modèle, script
  07-recherche-simple.md          préréglages et cases
  08-plan-de-travail.md           le canevas libre : tuiles, liens, fenêtre de tuile
  09-tuile-traduction.md
  10-tuile-assistant-ia.md
  11-fenetre-aide.md              les six fonctions et les huit contrôles
  12-recherches-sauvegardees.md
  13-quotas-couts-budget.md
  14-questions-ouvertes.md        ce qui n'est pas tranché
  15-mecanismes-et-references.md  mecanismes existants a reprendre, cadre legal
  16-onglet-tri.md                validation des rapprochements proposes
  17-sources-a-implementer.md     sources candidates traduites en consigne de branchement
  source.md                       briefing Aleph/FollowTheMoney/Maltego (fourni par Sednal)
  charte/
    jetons.css                    à inclure tel quel
    tokens.json                   la même chose, avec les justifications de contraste
    nommage.md                    la liste close des mots
    README.md                     le livret de la charte, les références externes
    composants/<Nom>/preview.html chaque motif, en HTML autonome et lisible
    composants/<Nom>/README.md    les règles de ce motif
  maquettes/
    Main.dc.html                  la page Réglages, interactive
    Recherche.dc.html             la page Recherche, interactive
    Tri.dc.html                   la page Tri, interactive
````

## 6. Comment lire les maquettes

`maquettes/*.dc.html` sont les maquettes **interactives** du pilote. Ce sont des fichiers HTML autonomes :
un gabarit en haut, puis une classe JavaScript `Component` avec une méthode `renderVals()` qui produit
toutes les valeurs affichées.

Elles servent de **référence de comportement**, pas de code à reprendre. Le format `.dc.html` est celui
de l'outil de maquettage, pas celui du pilote. Lis-les pour savoir *ce que ça fait* ; écris le vrai code
dans la pile du projet.

Pour comprendre un écran rapidement : cherche `renderVals()` dans le fichier, puis suis les clés qu'elle
renvoie jusqu'au gabarit, où elles apparaissent entre doubles accolades.

**Les maquettes sont figées au 26/10/2026.** À partir de cette date, Claude n'écrit plus de code visuel
— ni `.dc.html`, ni `preview.html` de composant. Ce qui existe reste une référence de comportement ;
tout ce qui vient après (Tableau de bord, Tri déjà couvert, et toute évolution future) arrive en texte
dans ces documents, et c'est momo qui l'écrit en code.

Les `charte/composants/<Nom>/preview.html` sont du HTML ordinaire, lisible et copiable : c'est la
définition visuelle exacte de chaque motif. Le `README.md` à côté dit les règles d'emploi — **lis-le, il
contient des interdictions que le visuel ne montre pas**.

## 7. Trois choses qui ne sont pas dans la maquette

À implémenter quand même, elles ont été décidées en discussion :

- **Les clés d'API ne s'affichent jamais en clair.** Champ masqué, et une fois enregistrée on affiche
  « clé enregistrée » et rien d'autre. Pas de bouton « voir ».
- **Les maquettes `Onglets.dc.html` et `Carte-source.dc.html`** dans l'artefact d'origine sont
  **périmées** : elles décrivent une structure antérieure. Elles ne sont pas dans ce dossier, ignore-les
  si tu les croises.
- **Le Tableau de bord et le Tri** n'ont aucune spécification. Ne devine pas.

## 8. En cas de doute

Dans cet ordre :

1. Le document de la chose concernée, dans ce dossier.
2. Le `README.md` du composant de charte correspondant.
3. La maquette, pour le comportement exact.
4. Si rien ne répond : **remonte la question**, ne tranche pas. Sednal a le dernier mot sur chaque point.
