# DECISION_SOURCES — décision de Sednal (recopiée telle quelle le 2026-10-12)

Numérotation : Sednal l'appelle « D67 » ; ce numéro était déjà pris dans `DECISIONS.md` (verdict du jeu test). Elle est enregistrée sous **D68**.

Nouvelle décision D67. Écris-la dans DECISION_SOURCES.md, commit, puis applique.

POURQUOI : le test a montré que seuls 11 acteurs de référence sur 356 (3,1 %) sont
même présents parmi les candidats. Le problème est en amont, dans les sources, pas
dans le classement ni l'indice.

CHANTIER A (le seul maintenant) : brancher le serveur MCP officiel de data.gouv.fr,
public et gratuit : claude mcp add --transport http datagouv https://mcp.data.gouv.fr/mcp
Ce qui compte, ce sont ses outils search_dataservices et get_dataservice_openapi_spec :
pour un sujet donné, tu cherches dans le catalogue des APIs publiques françaises, tu lis
sa spec, et tu en écris un fichier YAML dans config/recherche/. Jamais de code Python
propre à un sujet. La multiprise doit trouver ses propres prises.
Avantage à vérifier et à dire dans le rapport : ces sources ne dérivent pas de Wikidata,
donc contrairement à Wikidata elles ne rendent pas la mesure circulaire.

CHANTIER B (petit) : quand un sujet est ambigu (ex. "brasserie" = lieu de brassage ou
café-restaurant), ne choisis pas en silence. Liste les lectures possibles et dis-le.
N'invente aucune règle pour départager.

MESURE AVANT APPLICATION : sur le jeu de mise au point seulement. Le jeu test est brûlé,
ne le rouvre pas et ne t'en sers pas pour régler quoi que ce soit. Rapporte combien
d'acteurs de référence en plus arrivent parmi les candidats, et à quel coût.

NOTÉ, NE COMMENCE PAS : SearxNG (méta-moteur auto-hébergé, à voir avec moi car ça
s'installe sur la VM), OpenStreetMap/Overpass, et "entity set expansion" (ProbExpan,
SetExpan - code de labo, pensé pour l'anglais).

AUTONOMIE inchangée : tu remontes sans appliquer tout changement de format de
resultat.csv, toute suppression de données, toute activation des personnes,
min_ecosystemes sous 2, et toute réouverture du jeu test.
