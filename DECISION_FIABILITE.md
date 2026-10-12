# DECISION_FIABILITE — décisions de Sednal (recopiées telles quelles le 2026-10-12)

Décisions de Sednal, actées. Recopier d'abord ces instructions dans /opt/grappes/DECISION_FIABILITE.md, prendre le prochain numéro libre dans DECISIONS.md, puis appliquer DANS L'ORDRE. Reprendre en autonomie et ne s'arrêter que sur les points listés à la fin.

## PÉRIMÈTRE

Ressources francophones uniquement pour l'instant. Cible : structures formelles, structures informelles, et personnes (les personnes en dernier, étape 4). Pas de limite de temps de développement. Principe d'architecture : un outil = une seule fonction ; si une fonctionnalité prend trop de place elle devient une application séparée, le signaler. grappes est une multiprise : sa fonction unique est de produire une liste de noms à partir d'un sujet. Le format de sortie ne doit plus être figé : profils de sortie configurables, au minimum tsites (nom;ville;pays) et brut (tout, avec score et sources), resultat.csv restant disponible comme profil.

## RÉPONSE À Q26

Oui, mais le problème est plus large que la lecture de noms. Constat qui commande tout le reste : les entités produites sont des SOURCES (domaines, articles), pas des ACTEURS. Aucun indice de fiabilité ne corrigera cela, un score parfaitement calibré sur de mauvais candidats reste inutile. On corrige donc d'abord ce que sont les candidats, et on les note ensuite.

## ÉTAPE 1 — REGISTRES COMME SOURCE DE DÉCOUVERTE

Aujourd'hui Wikidata, SIRENE et le RNA servent seulement à noter la fiabilité ou à construire les références. Mesure du sujet handball : la liste des 17 clubs existait déjà, complète, dans une requête Wikidata gratuite, pendant que la collecte web n'en retrouvait qu'un seul. C'est incohérent avec le code Admiralty, où un registre d'État est le niveau le plus haut. Les brancher comme fournisseurs de la multiprise : pour un sujet, interroger d'abord les bases structurées et verser ces entités directement dans les candidats, avec leur commune quand le registre la donne. La difficulté réelle est de traduire la phrase de sujet en requête de registre : c'est le cœur de cette étape, et le travail est déjà proche puisque les sujets de test ont été tirés des classes Wikidata. Sources gratuites et sans quota. Non-circularité : sur un sujet dont la référence vient de Wikidata, le fournisseur Wikidata reste désactivé pendant la mesure ; mesurer donc l'apport des registres sur des sujets dont la référence ne vient pas d'eux, et le dire dans le rapport.

## ÉTAPE 2 — LES NOMS DANS LES TEXTES, COMME SOURCE DE PLUS

N'inventer aucun mécanisme : modèle de reconnaissance d'entités nommées existant, catégorie ORG, branché en multiprise, choix du modèle en configuration et jamais en dur, plusieurs modèles installables. Par défaut Jean-Baptiste/camembert-ner (français, F1 documenté 0,82 sur ORG). Option disponible Babelscape/wikineural-multilingual-ner pour un changement de langue ultérieur. Ce fournisseur peut créer de NOUVELLES entités depuis le texte, pas seulement confirmer des entités connues : c'est le changement nécessaire, différent de D54. Garde-fou : seuil de confiance documenté, et toute entité extraite doit correspondre à un segment de texte réellement présent. Pour les variantes d'un même nom, utiliser nomenklatura (OpenSanctions, local, base SQLite) ; ne pas écrire son propre rapprochement de noms.

## ÉTAPE 3 — INDICE DE FIABILITÉ UNIQUE

Décision : rapport de vraisemblance, puis calibration. On ABANDONNE la découverte de vérité comme mécanisme de notation : la mesure du matin a montré que les cinq algorithmes donnaient un résultat identique, parce qu'il n'y a pas de valeurs contradictoires à arbitrer. Garder le code comme point de comparaison si utile, mais ce n'est plus le mécanisme retenu.

Cadre à adopter, existant et documenté : le guide européen ENFSI pour le rapport évaluatif en science forensique. Ce qu'on en reprend :

* Deux propositions opposées explicites : cette entité est un acteur réel du sujet, contre elle ne l'est pas. Tout se calcule contre cette paire.
* Chaque élément, quelle que soit sa nature, est ramené à un rapport de vraisemblance : combien de fois plus probable est cette observation si la première proposition est vraie plutôt que la seconde. Les rapports se combinent, la nature de la source disparaît du calcul, il ne reste que son poids. C'est ce qui rend l'indice universel quelle que soit la prise branchée.
* La catégorie Admiralty de la source fournit son poids d'entrée. Tranco et les registres restent ce qu'ils sont aujourd'hui.
* Principe de logique, strict : on calcule la probabilité des OBSERVATIONS sachant la proposition, jamais l'inverse. L'inversion produit des scores faussement rassurants.
* Une seule échelle pour toutes les sources, bornes fixées et documentées, avec une restitution verbale à bandes, de « aucun apport » à « soutien extrêmement fort ».

Puis calibration : ajustement sigmoïde ou régression isotone (scikit-learn), qualité mesurée par diagramme de fiabilité, score de Brier et erreur de calibration espérée. Objectif : qu'un 80 signifie réellement 80 chances sur 100. Produire le diagramme de fiabilité dans le rapport. Hors de la zone calibrée (informels, personnes) le chiffre est une estimation étendue et non une mesure : la ligne de sortie doit le dire. Principe de robustesse du même guide : un raisonnement structuré et documenté est acceptable quand les données manquent, à condition de l'annoncer.

## ÉTAPE 4 — LES PERSONNES, SEULEMENT APRÈS

Le périmètre les inclut mais pas en même temps que le reste : une variable à la fois, sinon on ne sait plus ce qui a amélioré quoi. Préparer le paramètre de périmètre en configuration, par défaut sur personnes dans un rôle public uniquement (dirigeant inscrit à un registre, porte-parole cité, compte public s'exprimant au nom d'une structure), jamais les particuliers, le masquage actuel restant disponible. Ne pas l'activer et ne collecter aucune personne tant que les étapes 1 à 3 ne sont pas mesurées. Documenter ce choix : c'est une question de données personnelles, elle mérite d'être traitée dans la conception et non ignorée.

## MESURES À CHAQUE ÉTAPE

Comparer systématiquement au chiffre de départ établi le matin (autocal/resultats/base_dev.json) sur les mêmes données archivées. Collecter une fois, rejouer mille fois : aucune requête réseau pour un essai de paramètres. Jeux de mise au point et validation uniquement. Le jeu de test reste FERMÉ, ouvert une seule fois à la fin, paramètres figés, date et heure notées. Critères pré-enregistrés de docs/CERTIFICATION.md inchangés.

## S'ARRÊTER ET DEMANDER UNIQUEMENT POUR

* toute baisse du nombre minimal d'écosystèmes sous deux comme valeur par défaut : devoir de MESURER ce que donne la valeur un et de rapporter le chiffre, sans l'appliquer ;
* toute suppression de données déjà collectées ;
* l'activation de la collecte de personnes.

Tout le reste, décider seul.

## RESSOURCES

8 vCPU et environ 15,6 Go de RAM, vérifier avec nproc et free -h. La doc mentionnant 2 vCPU est obsolète.
