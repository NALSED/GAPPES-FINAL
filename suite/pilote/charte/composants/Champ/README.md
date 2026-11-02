Un champ, son libellé au-dessus, son aide en dessous. Jamais de libellé à l'intérieur du champ.

Le libellé est en `legende` et en `encre-douce`, 6 px au-dessus du champ, et il est lié par `for`/`id` —
sans quoi il ne sert à rien au clavier ni au lecteur d'écran. L'aide est en `legende` et `encre-pale`,
sous le champ.

Le champ fait 36 px de haut, remplissage horizontal 12 px, `rayon-controle`, texte en `controle`. Son
contour est `trait-fort` : c'est ce contour qui dit qu'un champ est là, donc il tient le 3:1 exigé. Le
contour clair employé avant cette charte était à 1,4:1 et ne le tenait pas.

Un champ de script ou de valeur technique passe en `code`, famille `mono`.

**Le focus se voit** : anneau `accent` de 2 px, décollé de 2 px, comme sur un bouton.

Une clé d'API ne s'affiche jamais en clair : le champ reste masqué et n'affiche que « clé enregistrée ».

Le consommateur fournit le libellé, l'`id`, la valeur et l'aide.