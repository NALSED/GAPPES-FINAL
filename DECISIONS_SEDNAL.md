# Decisions de Sednal sur Q22 et Q23

## Q22
Ajoute RSS et Wikipedia/Wikidata comme fournisseurs dans la multiprise (config YAML, § 4 de
FINAL.md). Chacun tague ses observations avec son propre ecosysteme ("rss", "wikipedia"),
distinct du "web" generique recupere via Tavily. Objectif : restaurer un vrai recoupement
entre au moins 2 ecosystemes sans brancher de reseau social. Documente le choix dans
DECISIONS.md (statut "proposee").

## Q23
Deux changements :
- Le sujet devient : "Les acteurs des blocages et mobilisations etudiantes en France en ce
  moment" (config/sujets.yaml, deja mis a jour).
- seuil_ingestion devient auto-ajustable (config/autonomie.yaml), borne entre 5 et 40,
  valeur de depart 20. Meme logique que le recalibrage borne deja prevu pour les seuils
  confirme/probable (FINAL.md § 8) : tu l'ajustes toi-meme dans ces bornes selon la
  pertinence observee, tu notes chaque changement et sa raison dans le rapport de cycle.

## Suite
Applique ces deux points, puis relance un cycle reel. Si un autre point bloquant du meme
type apparait, decris-le clairement dans ETAT.md et arrete-toi dessus, comme pour Q22/Q23.
