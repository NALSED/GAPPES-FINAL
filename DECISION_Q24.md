# Decision de Sednal sur Q24 : poids des sources via methodes eprouvees, pas inventees

Principe directeur : n'inventer aucun barème. Adapter des methodes etablies du domaine de
l'analyse de renseignement et de la gestion de donnees.

## 1. Code Admiralty (systeme OTAN 6x6) pour le poids des sources
Methode standard d'analyse de renseignement, deux notes separees :
- Fiabilite de la source (A a F), fixee par type de fournisseur, documentee dans
  config/fiabilite_sources.yaml :
    A : registre officiel d'Etat (SIRENE, RNA, enseignement superieur)
    B : agence de presse / media etabli (a lister nommement si connu)
    C : Wikipedia / Wikidata
    D : web generique (recupere via Tavily/RSS)
    E/F : source inconnue ou jamais verifiee
- Credibilite de l'info (1 a 6), qui reste liee au RECOUPEMENT existant (min_ecosystems,
  min_citers) : 1 = confirmee par au moins 2 ecosystemes independants, jusqu'a 6 = ne peut
  pas etre jugee. Ne remplace pas le recoupement, le formalise avec l'echelle standard.
- Integre la fiabilite (A-F) dans min_weight_sum existant : une source A pese plus dans le
  total que D ou E. Le recoupement entre au moins 2 ecosystemes reste une condition
  SEPAREE et obligatoire, jamais contournable par un poids eleve a elle seule.

## 2. Tranco list pour objectiver la notoriete d'un domaine web
Au lieu d'inventer un chiffre de "referencement", utilise le classement Tranco
(tranco-list.eu), liste academique ouverte et gratuite, concue pour la recherche,
resistante a la manipulation. Pour un domaine web generique (categorie D), le rang Tranco
peut affiner le poids a l'interieur de cette categorie (un domaine bien classe pese un peu
plus qu'un domaine absent du classement), sans jamais remonter au-dessus de B ou A.
Documente la source et la date du classement utilise (il est mis a jour periodiquement,
telecharger/mettre en cache, ne pas interroger en boucle).

## 3. Registres officiels (deja evoque) : validation legale, pas juste un poids
Garde la proposition precedente : un match actif dans un registre d'Etat (SIRENE, RNA,
enseignement superieur) place la source en categorie A de fiabilite. Documente si cela
suffit, combine a UNE SEULE autre citation independante, a atteindre le niveau "confirmee"
(credibilite 1-2 Admiralty), ou si 2 ecosystemes independants restent necessaires meme avec
une source A. Propose ton analyse technique dans DECISIONS.md avant de trancher par defaut
sur l'option la plus prudente (2 ecosystemes requis dans tous les cas).

## Implementation
- config/fiabilite_sources.yaml : tableau documente, pas de valeur inventee a la volee.
- Champ "fiabilite_admiralty" et "credibilite_admiralty" dans les observations/citations.
- resultat.csv : pas de changement de colonnes pour l'instant, sauf si tu juges utile
  d'exposer le niveau Admiralty quelque part (a ton jugement, documente le choix).
- Tests : une source A + une source D independante converge plus vite vers "confirmee"
  qu'une source D seule ; aucune source, meme A, ne confirme seule sans 2 ecosystemes.

Applique dans cet ordre : 1 (Admiralty) -> 3 (registres) -> 2 (Tranco, optionnel si le temps
le permet). Documente chaque choix dans DECISIONS.md (statut "proposee"). Relance un cycle
reel une fois le point 1 en place au minimum.
