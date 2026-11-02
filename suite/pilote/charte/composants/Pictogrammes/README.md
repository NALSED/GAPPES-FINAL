Le jeu de pictogrammes de grappes : trente et un dessins, et aucun autre.

Tous sur une grille de 24 (`viewBox="0 0 24 24"`), trait de **1,6 px**, `stroke-linecap` et
`stroke-linejoin` arrondis, `fill="none"`. Aucun dessin n'est rempli, aucun n'a de couleur propre.

**Deux tailles seulement.** 20 px dans les lignes, les boutons et les panneaux ; 28 px sur les tuiles du
plan de travail. Rien entre les deux, et le rapport avec le texte voisin ne change jamais.

**La couleur est celle du texte à côté**, selon la règle de Carbon : `stroke="currentColor"` et le
pictogramme suit. Donc `encre-douce` dans une ligne de tableau, `role-…` sur une étiquette de rôle, blanc
dans un bouton principal. Un pictogramme centré sur le texte, jamais aligné sur sa ligne de base.

Trois dessins portent une couleur imposée, par exception à la règle ci-dessus : `attention` est toujours
en `etat-attention`, et `aide` et `ia` sont en `accent` quand ils annoncent la fenêtre d'aide ou un
contenu produit par une IA. Partout ailleurs la règle du texte voisin s'applique.

**Un dessin, une seule chose.** L'engrenage est l'onglet Réglages ; les curseurs sont le rôle OUTIL. Le
pilote employait les curseurs pour les deux, et c'est corrigé ici. De même, la loupe sert à l'onglet
Recherche et au rôle CHERCHER, parce que c'est la même idée — ce n'est pas un doublon.

**Un pictogramme sans libellé** ne s'emploie que dans trois cas : le `×` de fermeture, le chevron de
dépliage, et les ports d'une tuile. Chacun porte alors un `aria-label`. Partout ailleurs, un pictogramme
accompagne un mot et ne le remplace pas.

Une seule exception aux deux tailles : le `×` qui retire une tuile du plan de travail est dessiné à
**12 px**, trait de 2,4 px, parce qu'il tient dans un bouton de 20 px posé dans le coin de la tuile.

Une cible tactile fait au moins 44 px : ajoute du remplissage autour du dessin plutôt que de l'agrandir.

## Le code à reprendre

````html
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
     stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <path d="M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zM20.5 20.5L16 16"/>
</svg>
````

## Les trente et un tracés

### Navigation

| Nom | Emploi | Tracé |
| :-- | :-- | :-- |
| `tableau-de-bord` | Onglet Tableau de bord | `M4 20h16M7.5 20v-6M12 20V8M16.5 20v-9` |
| `recherche` | Onglet Recherche, et toute action de recherche | `M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zM20.5 20.5L16 16` |
| `reglages` | Onglet Réglages | `M12 9.6a2.4 2.4 0 1 0 0 4.8 2.4 2.4 0 0 0 0-4.8zM12 3v2.6M12 18.4V21M3 12h2.6M18.4 12H21M5.64 5.64l1.84 1.84M16.52 16.52l1.84 1.84M18.36 5.64l-1.84 1.84M7.48 16.52l-1.84 1.84` |
| `tri` | Onglet Tri | `M7 4.5v15M7 4.5L4 7.5M7 4.5l3 3M17 19.5v-15M17 19.5l-3-3M17 19.5l3-3` |

### Rôles

| Nom | Emploi | Tracé |
| :-- | :-- | :-- |
| `chercher` | Rôle CHERCHER. Le même dessin que l'onglet Recherche : c'est la même idée | `M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zM20.5 20.5L16 16` |
| `verifier` | Rôle VÉRIFIER | `M12 3l7 3v5c0 5-3 8-7 10-4-2-7-5-7-10V6l7-3zM9 12l2 2 4-4` |
| `enrichir` | Rôle ENRICHIR | `M12 3l9 5-9 5-9-5 9-5zM3 13l9 5 9-5` |
| `catalogue` | Rôle CATALOGUE | `M5 4h10a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3V4zM5 17a3 3 0 0 1 3-3h10` |
| `outil` | Rôle OUTIL. Les curseurs disent une brique qu'on règle | `M4 7h10M18 7h2M4 17h2M10 17h10M14 4v6M6 14v6` |
| `rapprocher` | Rôle RAPPROCHER | `M10 14a4 4 0 0 0 6 0l3-3a4 4 0 0 0-6-6l-1 1M14 10a4 4 0 0 0-6 0l-3 3a4 4 0 0 0 6 6l1-1` |

### Objets

| Nom | Emploi | Tracé |
| :-- | :-- | :-- |
| `source` | Une source, dans une liste ou un titre | `M12 3.5c4.4 0 8 1.1 8 2.5s-3.6 2.5-8 2.5S4 7.4 4 6s3.6-2.5 8-2.5zM4 6v12c0 1.4 3.6 2.5 8 2.5s8-1.1 8-2.5V6M4 12c0 1.4 3.6 2.5 8 2.5s8-1.1 8-2.5` |
| `saisie` | Ce que tu saisis : la tuile de départ du plan de travail | `M4 9h16v6H4zM7.5 12h9` |
| `grappe` | Une grappe, et la tuile de résultat | `M12 4.5a3 3 0 1 1 0 6 3 3 0 0 1 0-6zM6 13.5a3 3 0 1 1 0 6 3 3 0 0 1 0-6zM18 13.5a3 3 0 1 1 0 6 3 3 0 0 1 0-6zM10.2 10.2l-2.4 3.6M13.8 10.2l2.4 3.6` |
| `quota` | Un quota, un plafond | `M4 17.5a8 8 0 1 1 16 0M12 17.5l4.5-5` |
| `cout` | Un coût, un budget | `M12 4a8 8 0 1 0 0 16 8 8 0 0 0 0-16zM15.5 9.5A3.6 3.6 0 0 0 9.4 12a3.6 3.6 0 0 0 6.1 2.5M8 11h5.5M8 13h5.5` |
| `ia` | L'outil Assistant IA, et tout contenu produit par une IA | `M10.5 4.5c0 3.3 1.2 4.5 4.5 4.5-3.3 0-4.5 1.2-4.5 4.5 0-3.3-1.2-4.5-4.5-4.5 3.3 0 4.5-1.2 4.5-4.5zM17 13.5c0 2.2.8 3 3 3-2.2 0-3 .8-3 3 0-2.2-.8-3-3-3 2.2 0 3-.8 3-3z` |

### Actions

| Nom | Emploi | Tracé |
| :-- | :-- | :-- |
| `ajouter` | Ajouter | `M12 5v14M5 12h14` |
| `modifier` | Modifier | `M4.5 19.5h4L19 9a2.83 2.83 0 0 0-4-4L4.5 15.5v4zM14 6l4 4` |
| `retirer` | Retirer : réversible, ne touche à aucun fichier | `M12 4a8 8 0 1 0 0 16 8 8 0 0 0 0-16zM8 12h8` |
| `supprimer` | Supprimer : définitif, et seulement là où la charte l'autorise | `M5 7h14M9.5 7V4.5h5V7M6.5 7l.9 13h9.2l.9-13M10.5 11v5.5M13.5 11v5.5` |
| `interrupteur` | Allumer ou éteindre | `M8 8h8a4 4 0 0 1 0 8H8a4 4 0 0 1 0-8zM16 10.5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3z` |
| `lancer` | Lancer une recherche ou un test | `M8 5l11 7-11 7V5z` |
| `tester` | Tester sur un exemple | `M9.5 3h5M10.5 3v7.2l-4 7.6A2 2 0 0 0 8.3 21h7.4a2 2 0 0 0 1.8-3.2l-4-7.6V3M8.2 15h7.6` |
| `reutiliser` | Réutiliser une recherche sauvegardée | `M20 12a8 8 0 1 1-2.4-5.7M20 4.5V9h-4.5` |
| `ranger` | Ranger les tuiles du plan de travail | `M4 5h6.5v6H4zM13.5 5H20v4h-6.5M13.5 11H20v8h-6.5zM4 13h6.5v6H4z` |

### Interface

| Nom | Emploi | Tracé |
| :-- | :-- | :-- |
| `deplier` | Déplier ou replier. Tourne de -90° quand c'est replié | `M6.5 9.5l5.5 5.5 5.5-5.5` |
| `fermer` | Fermer une fenêtre ou un panneau | `M6.5 6.5l11 11M17.5 6.5l-11 11` |
| `filtrer` | Filtrer une liste affichée | `M4 5.5h16l-6.2 7.2V19L10.2 17v-4.3L4 5.5z` |
| `pays` | Pays d'une source | `M12 4a8 8 0 1 0 0 16 8 8 0 0 0 0-16zM4 12h16M12 4c2.2 2.2 3.4 5 3.4 8s-1.2 5.8-3.4 8c-2.2-2.2-3.4-5-3.4-8S9.8 6.2 12 4z` |
| `aide` | La fenêtre Aide, repliée ou dépliée | `M12 4.5c-4.1 0-7.5 2.8-7.5 6.2 0 1.9 1 3.6 2.7 4.7L6.5 19.5l3.9-2c.5.1 1.1.1 1.6.1 4.1 0 7.5-2.8 7.5-6.2S16.1 4.5 12 4.5z` |
| `attention` | Un avertissement avant une action. Toujours en `etat-attention`, jamais en `danger` | `M12 4.6L20.8 19.4H3.2L12 4.6zM12 10.2v4.1M12 16.9v.1` |
