# 06 — Réglages › Outils

## Ce qu'on implémente

La grille des outils, et la fiche d'un outil. **Chaque outil allumé devient une brique posable sur le
plan de travail.** C'est tout le lien entre les deux écrans.

## La grille

Des cartes, une par outil, en grille qui se réajuste (minimum 260 px par carte). Chaque carte porte :
le nom, l'étiquette de rôle, la description, l'état (pastille + mot), puis *Modifier* et
*Allumer* / *Éteindre*.

**Attention à l'accord** : les états d'un outil sont au masculin — *opérationnel*, *éteint*. Table de
libellés distincte de celle des sources.

## Les neuf outils livrés

| Outil | Rôle | Allumé d'origine |
| :-- | :-- | :-- |
| Format JSON / CSV | OUTIL | oui |
| Traduction | OUTIL | oui — voir `09` |
| Condition « si » | OUTIL | oui |
| Boucle | OUTIL | oui |
| Fusion / doublons | RAPPROCHER | oui |
| Filtre | OUTIL | oui |
| Attente (quota) | OUTIL | non |
| Compteur budget | OUTIL | non |
| RSSHub | OUTIL | non |
| **Assistant IA** | OUTIL | **non, et l'allumer passe par un avertissement** — voir `10` |

## La fiche outil

Panneau latéral, **520 px**. Deux natures d'outil, choisies par puces en haut :

**Modèle** — un outil fourni, qu'on règle. On choisit le modèle, puis ses options.

**Script** — un script Python collé dans un champ long, en style `code` (IBM Plex Mono, 12 px). Signature
imposée :

````python
def run(resultats):
    # resultats : liste de dictionnaires
    return [r for r in resultats if r.get("pays") == "FR"]
````

### Les champs communs

| Champ | Rôle |
| :-- | :-- |
| Nom | — |
| Rôle | OUTIL ou RAPPROCHER |
| Ce qu'il fait | une phrase, affichée sur la carte |
| Ce qu'il reçoit | décrit l'entrée — repris dans la fenêtre de tuile |
| Ce qu'il renvoie | décrit la sortie — idem |
| Effet dans le Tableau de bord | *journal*, *compteur*, *alerte*, *rien* |
| Options | paires libellé / valeur, reprises telles quelles sur la tuile |

### Le test

Deux champs côte à côte : **un exemple d'entrée**, et **ce qu'on attend en sortie**. Bouton *Lancer le
test* avec le pictogramme `tester`.

Le test est ce qui fait passer un outil de *à vérifier* à *opérationnel*. Pas de passage automatique sans
test réussi.

## Le lien avec le plan de travail

Un outil **éteint** apparaît quand même dans la palette de la Recherche avancée, **grisé et marqué
« éteinte »**, et ne se pose pas. L'utilisateur voit que la brique existe et qu'il faut l'allumer ici.
Ne le cache pas : un outil invisible est un outil qu'on ne trouve jamais.

## Où regarder

- `charte/composants/Champ/` — dont le champ long pour le script
- `charte/composants/Bouton/`, `Pastille/`, `Role/`
- `maquettes/Main.dc.html`, sous-partie Outils
