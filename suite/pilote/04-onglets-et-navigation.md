# 04 — Onglets et navigation

## Ce qu'on implémente

La coquille de l'application : une barre d'onglets en haut, un titre de page, et la zone de contenu.

## Les quatre onglets, dans cet ordre

| Onglet | Pictogramme | État |
| :-- | :-- | :-- |
| Tableau de bord | `tableau-de-bord` | **pas conçu** — visible, grisé, inactif |
| Recherche | `recherche` | conçu |
| Réglages | `reglages` | conçu |
| Tri | `tri` | **pas conçu** — visible, grisé, inactif |

L'ordre est fixe. Au singulier quand c'est possible, sans sous-titre dans la barre.

Les deux onglets non conçus restent **visibles et grisés** (`encre-pale`), pas cachés : l'utilisateur
doit voir que ça existe et que ça arrive. Ne devine aucun contenu pour eux.

## Les sous-parties

**Réglages** : *Sources* et *Outils*, en deux boutons côte à côte sous le titre, chacun avec son
pictogramme (`source`, `outil`) et son compteur.

**Recherche** : *Recherche simple*, *Recherche avancée*, *Recherches sauvegardées*, en trois cartes
repliables empilées, pas en onglets.

## L'onglet actif

Texte en `encre`, graisse 600, et un trait de 2 px en `accent` sous l'onglet. Les autres en
`encre-douce`, graisse normale, sans trait. Jamais la couleur seule : la graisse et le trait font le
travail ensemble.

Pictogramme à 20 px, 8 px d'écart avec le libellé, centré sur le texte.

## Le titre de page

Un seul `titre-l` (22 px) par écran, sous la barre d'onglets. Il reprend exactement le nom de l'onglet.

## Où regarder

- `charte/composants/Onglets/preview.html` et son `README.md`
- `maquettes/Main.dc.html` — la barre complète en situation
