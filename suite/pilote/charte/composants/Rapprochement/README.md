La carte de l'onglet Tri. Deux fiches côte à côte — ou plus, même disposition —, et un pied à deux
boutons : *Confirmer*, *Séparer*.

**La confiance est calculée, jamais saisie.** C'est le score que rend le moteur de rapprochement (Splink,
voir `pilote/15-mecanismes-et-references.md` §1), affiché en barre + pourcentage. La file de l'onglet Tri
trie ces cartes du pourcentage le plus bas au plus haut : le travail le plus incertain passe en premier.

## Le dire visuel d'une ligne, champ par champ

Trois états, calculés à chaque rendu, jamais écrits en dur :

| État | Style | Condition |
| :-- | :-- | :-- |
| **Accord** | fond `etat-ok-fond`, texte `etat-ok-encre`, gras | Les deux valeurs sont identiques une fois normalisées (casse, espaces) |
| **Désaccord** | fond `etat-attention-fond`, texte `etat-attention` | Les deux valeurs sont présentes et diffèrent |
| **Absence** | texte `encre-pale`, italique | Une valeur manque d'un côté — ce n'est pas un désaccord, il n'y a rien à comparer |

Les deux fiches d'une même ligne partagent toujours le même style des deux côtés : la comparaison se lit
d'un seul regard, colonne de gauche contre colonne de droite, sans sauter d'un bloc de couleur à l'autre.

Chaque colonne porte en en-tête la **source** et sa **fiabilité** (A–F, voir le composant `LigneSource`
et `pilote/05-reglages-sources.md`) — la confiance du rapprochement ne remplace pas la fiabilité de
chaque source, les deux se lisent ensemble.

## Confirmer / Séparer

Deux verbes propres à cet écran, ajoutés le 26/10/2026 à la liste close (`charte/nommage.md`). *Confirmer*
est le bouton principal — la règle du bouton unique du composant `Bouton` s'applique ici comme ailleurs.
*Séparer* est secondaire, **jamais un bouton danger** : aucune des deux actions n'efface une fiche, un
fichier ni une source. Voir `pilote/16-onglet-tri.md` pour le détail et pour « Déjà tranchés », la trace
qui garde chaque décision lisible après coup.
