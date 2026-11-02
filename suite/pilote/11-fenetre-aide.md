# 11 — Fenêtre Aide

## Ce qu'on implémente

Une fenêtre d'assistance en bas à droite qui aide à se servir de grappes.

**Lis d'abord ceci** : ce n'est pas une fenêtre de chat habillée. L'exigence de Sednal est explicite —
l'Aide doit être **un vrai outil dans l'outil, puissant et robuste**. Le modèle de langue n'est que la
couche qui comprend une phrase libre. **Enlève le modèle : l'outil fonctionne encore.**

## La forme

**380 px de large, 468 px de haut**, à 24 px du bord droit et du bas. `ombre-fenetre`.

Elle **ne se ferme pas**. Elle se **replie** sur sa barre de titre et se déplie d'un clic. Donc **pas de
`×`** dessus : le chevron `deplier`, avec `aria-label="Replier"`.

Repliée, c'est une barre de 44 px : pictogramme `aide` en `accent`, le mot *Aide*, un chevron vers le
haut.

**Pas de voile gris derrière.** Elle parle du plan de travail qu'on est en train de monter ; le masquer
pendant qu'on en parle n'aurait aucun sens. La page reste utilisable fenêtre dépliée.

> Sur le mot : Sednal a dit « réduite », la charte retient **Replier**, parce que *Filtrer* est déjà
> défini comme « réduit une liste affichée ». Deux verbes proches pour deux choses différentes, c'est
> exactement ce que la liste close évite. Validé le 26/10/2026.

## Le cœur : elle appelle des fonctions, elle n'écrit pas des faits

C'est la règle qui tient tout le reste. L'Aide ne répond **jamais de mémoire** sur l'état de grappes.
Elle appelle une fonction, reçoit des données réelles, et se contente de les formuler.

C'est le patron du *function calling* : le modèle **choisit l'outil et met en forme**, il ne produit pas
le contenu.

### Les six fonctions, et aucune autre

| Fonction | Ce qu'elle lit | Ce qu'elle rend |
| :-- | :-- | :-- |
| `lister_sources(rôle, pays, état)` | La configuration des sources | Des sources réelles |
| `lire_plan()` | Le plan de travail en cours | Ses tuiles et ses liens |
| `proposer_plan(objectif, pays)` | La configuration et les préréglages | Une suite de tuiles et de liens, **non posée** |
| `verifier_plan()` | Le plan, la configuration, les quotas | Une liste de constats |
| `definir(mot)` | `charte/nommage.md` | La définition exacte, mot pour mot |
| `ouvrir(écran)` | — | Emmène l'utilisateur au bon endroit |

**Conséquence à ne pas casser** : si l'Aide affiche *DILA — JOAFE*, c'est que le nom vient du retour de
`lister_sources`, pas du modèle. Elle **ne peut pas** inventer une source — pas parce qu'on le lui
interdit dans une consigne, parce qu'elle n'a pas par où.

Ne laisse jamais le modèle produire directement le texte affiché d'un nom de source, de tuile ou
d'option. Ces chaînes viennent du retour de fonction, point.

## `verifier_plan()` : des règles, pas un avis

**Aucun modèle n'intervient.** C'est une liste de contrôles déterministes sur le plan de travail — le
principe d'un *linter*. Les mêmes tuiles donnent toujours les mêmes constats.

| # | Contrôle | Constat | Niveau |
| :-- | :-- | :-- | :-- |
| 1 | Tuile sans lien entrant | Elle n'est jamais interrogée | bloquant |
| 2 | Tuile sans lien sortant, sauf Grappes | Son résultat se perd | bloquant |
| 3 | Source posée mais éteinte dans Réglages | Elle ne répondra pas | bloquant |
| 4 | Deux sources du même rôle sans RAPPROCHER derrière | Les doublons arriveront jusqu'à la grappe | remarque |
| 5 | Quota au-delà de 80 %, ou atteint | La recherche s'arrêtera en route | remarque |
| 6 | Source dans une autre langue, sans Traduction avant | Elle cherchera avec les mots d'une autre langue | remarque |
| 7 | Lien vers une tuile qui n'accepte pas cette entrée | Le lien ne passera rien | bloquant |
| 8 | Assistant IA posé | Rappel : sa sortie est marquée IA | remarque |

Le contrôle 6 s'appuie sur le champ **Langue** de la fiche source (`05`) et sur la langue détectée de la
saisie.

**Deux niveaux, pas trois.** *bloquant* : pastille `etat-attention`, la recherche ne donnera rien.
*remarque* : pastille `trait-fort`, elle tournera mais mal.

Chaque constat **nomme la tuile concernée**, et cliquer dessus la sélectionne sur le plan.

## Ce qu'elle ne diagnostique pas

Elle s'arrête **au plan de travail**. Le contenu des grappes — un résultat douteux, un rapprochement
douteux — ne se juge pas depuis cette fenêtre.

L'Aide dit pourquoi une recherche **ne peut pas** marcher. Elle ne dit pas si un résultat est vrai. Ne
laisse personne élargir son périmètre sur ce point.

## Elle propose, elle ne pose pas

Quand `proposer_plan` renvoie quelque chose, la fenêtre affiche une **carte** : titre en `etiquette`, une
ligne par tuile — nom à gauche, étiquette de rôle à droite, un trait `trait-fort` qui tient la colonne.
*Ta saisie* et *Grappes* n'ont pas de rôle : pastille neutre `surface-creuse` / `encre-pale`.

Deux boutons, **un seul principal** : *Poser ces tuiles*, puis *Annuler*.

**L'Aide ne pose jamais rien d'elle-même, n'allume rien, ne retire rien, ne supprime rien.** Toute action
passe par un bouton pressé. C'est la différence entre un assistant et un automate.

## Sans modèle, elle marche encore

Les trois puces du bas appellent les fonctions **directement** :

| Puce | Fonction | Modèle nécessaire |
| :-- | :-- | :-- |
| **Comment je fais…** | `proposer_plan` sur un objectif choisi dans une liste | non |
| **Pourquoi ça n'a rien donné ?** | `verifier_plan` | non |
| **Ça veut dire quoi…** | `definir` sur un mot de la liste close | non |

Seule la **phrase libre** tapée dans le champ a besoin d'un modèle, et seulement pour traduire la phrase
en appel de fonction.

**Modèle absent, éteint, hors quota : le champ de saisie se grise, les puces continuent de fonctionner,
et la fenêtre reste un outil.** Implémente ce mode dégradé dès le début, pas comme un rattrapage : c'est
la condition qui rend l'Aide robuste.

## Ce qu'elle n'est pas

Ce n'est pas l'**Assistant IA** (`10`), qui est un outil du plan de travail et transforme des résultats.
L'Aide ne produit rien qui entre dans une grappe : elle ne porte donc jamais la marque « IA », et elle
ne la remplace pas non plus.

## Où regarder

- `charte/composants/Aide/README.md` — la spécification complète du composant
- `charte/composants/Aide/preview.html` — les deux états, dépliée et repliée
- `maquettes/Recherche.dc.html` — la fenêtre avec un plan proposé et trois constats
- `maquettes/Main.dc.html` — la même fenêtre avec une réponse de `definir`
