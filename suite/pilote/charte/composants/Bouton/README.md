Trois sortes de boutons, et la liste des verbes est close.

**Un seul bouton principal par écran.** Au-delà, il n'y a plus d'action principale — c'est la règle du
GOV.UK Design System. Les autres actions sont secondaires.

Le libellé est le verbe qui nomme exactement ce qui va se passer, en minuscules, avec son complément
quand il est utile : « Ajouter une source » plutôt que « Ajouter ». Jamais de capitales, jamais « OK ».

Les verbes autorisés : Ajouter, Modifier, Enregistrer, Annuler, Fermer, Allumer, Éteindre, Retirer,
Supprimer, Lancer, Réutiliser, Remettre par défaut, Ranger, Filtrer, Replier, Déplier, Confirmer, Séparer.
La section « Les mots de grappes » donne pour chacun ce qu'il fait et ce qu'il remplace.

**Retirer et supprimer ne sont pas la même chose.** Retirer sort de la liste, ne touche à aucun fichier,
et se défait. Supprimer est définitif et demande une confirmation. Le bouton danger ne sert qu'à ces deux
verbes, et il reste rare : un écran qui en montre trois est un écran à revoir.

Mesures : hauteur 36 px, remplissage horizontal 16 px, `rayon-controle`, style de texte `controle`,
pictogramme à 20 px dans la couleur du texte, 8 px entre le dessin et le mot.

Le principal est `accent` avec du blanc dessus, à 6,1:1. Le secondaire est `surface` avec un contour
`trait-fort`, qui tient le 3:1 exigé d'un bord porteur d'information. Le danger est `surface` avec texte
et contour `danger`, à 8,1:1.

**Le focus se voit** : un anneau `accent` de 2 px, décollé de 2 px. Ne le retire jamais. Une cible
tactile fait au moins 44 px, remplissage compris.