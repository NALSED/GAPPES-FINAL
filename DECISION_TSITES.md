# DECISION — Passerelle grappes -> trouver-sites

Décidée par Sednal le 2026-10-11. A appliquer. Prends le prochain numéro libre dans DECISIONS.md.

## Contexte

Le projet trouver-sites (dépot NALSED/trouver-final, meme VM, /opt/trouver-sites) prend un CSV
en entrée et cherche le site web et les réseaux sociaux de chaque entité. Les sorties de grappes
doivent pouvoir l'alimenter sans retouche manuelle.

Format d'entrée imposé par trouver-sites (pipeline/tsites/importer.py, constante COLONNES) :
- en-tete obligatoire, exactement les colonnes nom, ville, pays ; séparateur point-virgule ; UTF-8
- colonne manquante = import refusé ; colonne en trop = ignorée avec un avertissement
- nom non vide obligatoire (ligne ignorée sinon)
- ville peut etre vide
- pays = code ISO deux lettres majuscules ; vide ou inconnu accepté, mais la recherche perd
  la langue déduite du pays

Vérifié sur le code réel : le resultat.csv actuel (une colonne NOM) est refusé a l'import,
message « Colonnes manquantes : ville, pays ».

## Décision

1. sorties/resultat.csv NE CHANGE PAS. Une colonne NOM, format figé par FINAL.md.

2. Nouvelle sortie supplémentaire sorties/resultat_tsites.csv, écrite par le meme export, a
   chaque cycle, au format nom;ville;pays : séparateur point-virgule, UTF-8 sans BOM, en-tete
   en minuscules, meme tri alphabétique et meme déduplication que resultat.csv.

3. Remplissage de ville : la renseigner seulement quand tu la connais déja, jamais l'inventer.
   - Source prioritaire : les registres officiels déja branchés (API Recherche d'entreprises,
     API Association/RNA). Ils renvoient la commune du siege : utilise-la quand l'appariement
     a réussi.
   - Source secondaire : une ville explicitement présente dans les données déja collectées de
     l'entité (infobox Wikipédia, mentions légales d'une page déja lue).
   - Sinon : colonne vide. Pas de déduction, pas de département ni de région a la place.

4. Remplissage de pays : nouveau champ de configuration, aucune valeur en dur dans le code.
   Ajoute dans config/autonomie.yaml une section export_tsites avec deux clés : actif (booléen,
   true par défaut) et pays_defaut (chaine, FR par défaut). pays_defaut s'applique a toutes les
   lignes, sauf si tu disposes d'un code pays fiable pour l'entité (registre officiel, Wikipédia).
   actif a false doit désactiver proprement cette sortie.

5. Aucun filtrage de contenu dans cette sortie : les memes noms que resultat.csv, ni plus ni
   moins. Le constat D58 (médias vs acteurs) reste tranché comme il l'est : on garde tout.

6. Documentation : décris le fichier et sa configuration dans docs/utilisateur.md, et ajoute une
   ligne dans FINAL.md (section des sorties) précisant que resultat.csv reste la sortie de
   référence et que resultat_tsites.csv est une sortie de compatibilité.

7. Tests : au moins un test vérifiant l'en-tete exact, le séparateur, l'absence de BOM, une ligne
   avec ville renseignée, une ligne avec ville vide, et le respect de actif a false. Ne recopie
   pas le code de trouver-sites dans tes tests : vérifie le format, pas leur implémentation.

## A remonter a Sednal, ne pas trancher seul

Dans resultat.csv, plusieurs noms ne sont pas des organisations mais des titres d'articles
Wikipédia décrivant un concept ou un événement (« Mouvements étudiants en France », « Mouvement
contre le contrat premiere embauche de 2006 »). trouver-sites ne peut structurellement rien
trouver pour eux : ils consommeront du budget de recherche pour rien.

Tu disposes déja d'un mécanisme éprouvé pour ce tri : les catégories Wikipédia, que tu utilises
pour écarter les personnes physiques. Si une distinction « article d'organisation » / « article de
concept ou d'événement » est faisable avec ce mécanisme, sans inventer de nouveau critere, écris
une proposition chiffrée (combien de lignes écartées sur le jeu actuel) et attends l'accord de
Sednal. Ne l'applique pas de ta propre initiative.
