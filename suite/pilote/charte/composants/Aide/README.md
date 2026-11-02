Une fenêtre de 380 px posée en bas à droite, à 24 px des deux bords. Elle **ne se ferme pas** : elle se
replie sur sa barre de titre et se déplie d'un clic. Pas de `×` dessus, mais le chevron `deplier` avec
`aria-label="Replier"`. Pas de voile gris derrière : elle parle du plan de travail qu'on est en train de
monter, le masquer pendant qu'on en parle n'aurait aucun sens.

Ce qui suit n'est pas de la décoration autour d'un modèle de langue. **L'Aide est un outil**, et le
modèle n'est que la couche qui comprend une phrase libre. Enlève le modèle : l'outil fonctionne encore.

## Elle appelle des fonctions, elle n'écrit pas des faits

C'est la règle qui tient tout le reste. L'Aide ne répond **jamais** de mémoire sur l'état de grappes.
Elle appelle une fonction, reçoit des données réelles, et se contente de les formuler. C'est le patron
classique du *function calling* : le modèle choisit l'outil et met en forme, il ne produit pas le
contenu.

| Fonction | Ce qu'elle lit | Ce qu'elle rend |
| :-- | :-- | :-- |
| `lister_sources(rôle, pays, état)` | La configuration des sources | Des sources réelles, jamais inventées |
| `lire_plan()` | Le plan de travail en cours | Ses tuiles et ses liens |
| `proposer_plan(objectif, pays)` | La configuration et les préréglages | Une suite de tuiles et de liens, **non posée** |
| `verifier_plan()` | Le plan, la configuration, les quotas | Une liste de constats |
| `definir(mot)` | La liste close des mots de grappes | La définition exacte, mot pour mot |
| `ouvrir(écran)` | — | Emmène l'utilisateur au bon endroit |

Conséquence directe : si l'Aide affiche *DILA — JOAFE*, c'est que la source existe et qu'elle est
allumée — le nom vient du retour de `lister_sources`, pas du modèle. Un plan proposé n'est donc pas du
texte, c'est une liste de vraies tuiles avec leurs vraies étiquettes de rôle. **Elle ne peut pas inventer
une source**, pas parce qu'on le lui demande, parce qu'elle n'a pas par où.

## Vérifier un plan : des règles, pas un avis

`verifier_plan()` ne fait appel à aucun modèle. C'est une liste de contrôles déterministes sur le plan de
travail — le même principe qu'un *linter* : les mêmes tuiles donnent toujours les mêmes constats.

| Contrôle | Le constat |
| :-- | :-- |
| Tuile sans lien entrant | Elle n'est jamais interrogée |
| Tuile sans lien sortant (sauf Grappes) | Son résultat se perd |
| Source posée mais éteinte dans Réglages | Elle ne répondra pas |
| Deux sources du même rôle sans RAPPROCHER derrière | Les doublons arriveront jusqu'à la grappe |
| Quota au-delà de 80 %, ou atteint | La recherche s'arrêtera en route |
| Source dans une autre langue, sans Traduction avant | Elle cherchera avec les mots d'une autre langue |
| Lien vers une tuile qui n'accepte pas cette entrée | Le lien ne passera rien |
| Assistant IA posé | Rappel : sa sortie est marquée IA et ne compte pas comme un fait |

Deux niveaux seulement : **bloquant** (pastille `etat-attention`, la recherche ne donnera rien) et
**remarque** (pastille `trait-fort`, elle tournera mais mal). Chaque constat nomme la tuile concernée, et
la sélectionne sur le plan quand on clique dessus.

## Ce qu'elle ne diagnostique pas

Elle s'arrête au plan de travail. Le contenu des grappes — un résultat douteux, un rapprochement douteux
— ne se juge pas depuis cette fenêtre. L'Aide dit pourquoi une recherche **ne peut pas** marcher. Elle ne
dit pas si un résultat est vrai.

## Elle propose, elle ne pose pas

Le cœur du composant. Une carte, un titre `etiquette`, une ligne par tuile — nom à gauche, étiquette de
rôle à droite, un trait `trait-fort` qui tient la colonne. `Ta saisie` et `Grappes` n'ont pas de rôle :
pastille neutre `surface-creuse` / `encre-pale`.

Deux boutons dessous, un seul principal : **Poser ces tuiles**, puis **Annuler**. L'Aide ne pose jamais
rien d'elle-même, ne supprime rien, n'allume rien. Toute action passe par un bouton que l'utilisateur
presse — c'est la différence entre un assistant et un automate.

## Sans modèle, elle marche encore

Les trois puces du bas appellent les fonctions **directement**, sans passer par un modèle :

| La puce | La fonction | Besoin d'un modèle ? |
| :-- | :-- | :-- |
| **Comment je fais…** | `proposer_plan` sur un objectif choisi dans une liste | non |
| **Pourquoi ça n'a rien donné ?** | `verifier_plan` | non |
| **Ça veut dire quoi…** | `definir` sur un mot de la liste close | non |

Seule la phrase libre tapée dans le champ a besoin du modèle, et seulement pour traduire la phrase en
appel de fonction. Modèle absent, éteint, hors quota : le champ se grise, les puces continuent de
fonctionner, et la fenêtre reste un outil. Rien de ce qui compte ne dépend d'une IA.

## Ce qu'elle n'est pas

Ce n'est pas l'**Assistant IA**, qui est un outil du plan de travail et transforme des résultats. Deux
objets, deux noms, deux endroits. L'Aide ne produit rien qui entre dans une grappe : elle ne porte donc
jamais la marque « IA », et elle ne la remplace pas non plus.
