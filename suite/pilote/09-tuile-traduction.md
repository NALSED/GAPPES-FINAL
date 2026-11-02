# 09 — Tuile Traduction

## Pourquoi elle existe

Les sources de grappes ne parlent pas toutes la même langue. Interroger un registre allemand avec des
mots français ne renvoie rien — pas une erreur, **rien**, ce qui est pire : l'utilisateur croit qu'il n'y
a pas de résultat.

## Les trois règles

### 1. Elle ajoute, elle ne remplace jamais

La traduction se range **à côté** de l'original, qui reste intact. Chaque résultat garde la trace de la
langue dans laquelle il a été trouvé. Sans ça, on perd ce que la source a réellement dit, et le résultat
n'est plus vérifiable.

### 2. Les noms propres ne se traduisent pas

C'est le piège n° 1 de la recherche multilingue. « Jean Dupont » ne devient rien, « Charity Commission »
non plus. Option présente dans la tuile, **active par défaut**.

Côté implémentation : repérer les entités nommées avant de traduire et les remettre telles quelles
après. Ne te lance pas dans une solution maison — prends une bibliothèque de reconnaissance d'entités
nommées existante.

### 3. Elle sort vers plusieurs langues à la fois

**Le point le plus important de cette tuile.** `charpentier` donne `Zimmermann` ou `Tischler` selon qu'on
parle du charpentier ou du menuisier. Les deux mots existent, ils ne désignent pas le même métier. Parier
sur une seule traduction fait rater des résultats **en silence**.

Donc : une tuile Traduction, **plusieurs langues en sortie**, et chaque langue part vers sa propre
branche du plan de travail. Une tuile, plusieurs liens sortants. Le canevas libre le permet déjà.

Valeur par défaut dans la maquette : `français, anglais, allemand`.

## Les options de la tuile

| Option | Valeur par défaut | Note |
| :-- | :-- | :-- |
| Langue d'entrée | `détecter` | Ne force pas l'utilisateur à la déclarer |
| Traduire vers | `français, anglais, allemand` | **Plusieurs, séparées par des virgules** |
| Ne pas traduire | `les noms propres` | — |

**Détection, pas devinette.** Pour la langue d'entrée, utilise une bibliothèque de détection de langue
éprouvée. N'écris pas d'heuristique maison sur les accents ou les mots fréquents.

## Deux positions sur le plan

La même tuile sert à deux choses selon où on la pose :

- **Avant une source** — elle traduit la *requête*, pour chercher dans la langue de la source.
- **Après une source** — elle traduit les *résultats*, pour qu'on puisse les lire et les comparer.

Ne crée pas deux outils. C'est la position sur le plan qui décide, et c'est à l'utilisateur de la
choisir.

## Le moteur : ne rien réinventer

Deux options retenues, à trancher avec Sednal :

**LibreTranslate auto-hébergé** sur la VM. Pas de quota, pas de clé, pas de donnée qui sort. C'est
l'option cohérente avec le reste du projet. Attention à la place disque : les modèles pèsent quelques
gigaoctets, et il restait 81 Go sur la VM dont 60 réservés à yente.

**DeepL**, 500 000 caractères par mois en offre gratuite, meilleure qualité sur les langues européennes.
Demande une clé, et les données sortent.

Proposition : LibreTranslate par défaut, DeepL en option quand la qualité compte. Le choix du moteur est
**un réglage de la tuile**, pas une décision figée dans le code.

## Ce qui n'est pas tranché : la translittération

Traduire ne suffit pas pour les écritures non latines. `Երևան` → `Yerevan`, `Москва` → `Moskva` : ce
n'est pas une traduction, c'est une translittération, et c'est un mécanisme différent.

Il faudra le traiter dès qu'une source non latine entre dans grappes. Deux pistes : une option de cette
tuile, ou une tuile à part. **Ne tranche pas seul** — voir `14-questions-ouvertes.md`.

Quand ça viendra : utilise une translittération standard (ICU ou équivalent), pas une table maison.

## Le champ Langue des sources

Cette tuile a rendu nécessaire un champ **Langue** sur chaque source (voir `05`). C'est lui qui permet à
la fenêtre d'Aide de dire « cette source cherche en français, ta saisie est en anglais ».

## Où regarder

- `maquettes/Main.dc.html` — la fiche de l'outil, dans `tools()`
- `maquettes/Recherche.dc.html` — la brique dans la palette
