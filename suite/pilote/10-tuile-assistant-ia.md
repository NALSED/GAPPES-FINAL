# 10 — Tuile Assistant IA

## Lis ceci avant d'implémenter

C'est la tuile la plus dangereuse du programme. La priorité de grappes est **la fiabilité : un résultat
sûr et vérifiable**. Une tuile où l'on écrit une phrase libre et où un modèle fait ce qu'il veut est
l'inverse exact : non reproductible, non vérifiable, et capable d'inventer avec assurance.

Elle est quand même construite, parce qu'elle est utile. Mais **les garde-fous ne sont pas optionnels**.

## Les trois règles

### 1. Tout ce qui sort est marqué « IA »

Visiblement, dans la grappe, et **la marque ne se retire jamais en chemin**. Elle suit la donnée d'une
étape à la suivante, jusqu'au résultat final.

Côté implémentation : la marque est un **champ de la donnée**, pas une décoration d'affichage. Si une
étape ultérieure recopie la donnée sans recopier la marque, le garde-fou est cassé. Prévois-le dès la
structure de données, pas à la fin.

Un contenu marqué IA n'est **jamais** compté comme un fait vérifié, et n'est jamais fondu dans un
résultat sourcé.

### 2. Elle transforme, elle n'ajoute pas

Elle travaille sur ce qui a **déjà été collecté**. Elle peut résumer, extraire, classer ce qui est là.
Elle ne peut **pas** produire un fait nouveau qui entrerait dans une grappe comme s'il venait d'une
source.

### 3. Opérations nommées d'abord, phrase libre en secours

| Opération | Ce qu'elle fait |
| :-- | :-- |
| `résumer` | Un résumé court de ce qui est passé |
| `extraire` | Noms, dates, lieux — dans des champs séparés |
| `classer` | Range les résultats dans des catégories données |
| `reformuler la requête` | Réécrit ce qu'on cherche |
| *phrase libre* | Disponible, **mais pas le réglage par défaut** |

Ces opérations sont les usages connus et éprouvés d'un modèle de langue. La phrase libre reste une porte
de sortie, pas la porte d'entrée.

## Éteinte à la livraison

**L'outil est `off` dans la configuration livrée.** Ce n'est pas un détail d'affichage : c'est l'état par
défaut, décidé par Sednal.

Dans la palette de la Recherche avancée, il apparaît **grisé, marqué « éteinte »**, et ne se pose pas.

## L'avertissement à l'allumage

Cliquer sur *Allumer* n'allume pas : ça ouvre une **fenêtre d'avertissement de 480 px** que l'utilisateur
doit lire. Les quatre points, mot pour mot :

1. Ce que cette tuile produit ne vient d'aucune source : c'est une IA qui l'écrit.
2. Le résultat peut changer d'un lancement à l'autre, avec la même question et les mêmes données.
3. Une IA peut écrire quelque chose de faux avec assurance. Rien de ce qu'elle produit ne compte comme un
   fait vérifié.
4. Tout ce qui sort de cette tuile est marqué « IA » dans la grappe, et le reste à chaque étape.

Boutons : **Allumer** en principal, **Annuler** en secondaire.

Triangle `attention` en `etat-attention`, **jamais en `danger`** : le rouge est réservé à ce qui efface.
Allumer un outil est réversible.

**L'éteindre ensuite ne redemande rien.** On n'avertit que dans le sens risqué.

## Les modèles

Précision factuelle : « avec ou sans compte » n'existe pas pour Claude et ChatGPT, **les deux demandent
une clé d'API**. Les options sans clé sont le local ou les offres gratuites.

| Option | Clé | Données qui sortent | Note |
| :-- | :-- | :-- | :-- |
| Ollama local | non | non | Demande de la mémoire sur la VM |
| Groq, Mistral, Gemini | oui, offre gratuite | oui | — |
| Claude, ChatGPT | oui, payante | oui | — |

Le modèle est **un réglage de la tuile**, pas un choix figé dans le code. Valeur par défaut :
`local (Ollama)`, cohérente avec le reste du projet.

La clé suit la même règle que pour les sources : **jamais affichée en clair**, « clé enregistrée » et
rien d'autre.

## L'avertissement ne remplace pas la marque

L'avertissement se lit **une fois**, à l'allumage. La marque « IA », elle, reste visible **pour
toujours**. L'un prévient, l'autre prouve. N'en supprime aucun des deux en pensant que l'autre suffit.

## Ce qu'elle n'est pas

Ce n'est pas la **fenêtre Aide** (`11`), qui est un outil d'assistance à l'interface et ne produit rien
qui entre dans une grappe. Deux objets, deux noms, deux endroits.

## Où regarder

- `charte/composants/Avertissement/` — la fenêtre et ses règles
- `maquettes/Main.dc.html` — la tuile et l'avertissement, fonctionnels
