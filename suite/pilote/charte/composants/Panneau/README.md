Deux contenants, et le choix entre les deux n'est pas une question de goût.

**Modifier ouvre un panneau sur le côté.** On change quelque chose qui existe, en gardant la liste sous
les yeux pour se repérer. Le panneau prend un trait `accent` de 3 px à gauche, `ombre-panneau`, et ne
masque pas la page : 480 px pour une source, 520 px pour un outil.

**Ajouter ouvre une fenêtre au centre.** On crée quelque chose qui n'existe pas, et rien d'autre ne doit
distraire. La fenêtre est centrée sur un voile sombre, avec `ombre-fenetre` — la seule ombre franche de
grappes : 600 px pour une source, 640 px pour un outil, 1 040 px pour la fenêtre d'une tuile, qui montre
l'entrée, la tuile et la sortie côte à côte.

Les deux ont la même structure : un en-tête avec le titre en `titre-m` et le `×` de fermeture à droite,
les champs au milieu, les boutons en bas. Le bouton principal est à gauche, « Annuler » à droite.

Le bouton principal d'un ajout reste gris tant que les champs obligatoires ne sont pas remplis, et un mot
dit ce qui manque — jamais un bouton qui refuse sans expliquer.

Remplissage `espace-5`, `rayon-carte`, `espace-6` entre deux sections.

Le consommateur fournit le titre, les champs et les deux fonctions.