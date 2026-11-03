# Mode de recherche, extraction d'entités nommées, et personnes physiques

Décisions de Sednal du 2026-11-03 — détail de `DECISIONS.md` D83 et D84, QUESTIONS.md Q21/Q26/Q27.

## 1. Mode de recherche (D83)

Nouveau réglage **fermé**, au niveau de la recherche (pas d'une tuile), deux valeurs :

* **Trouver des sites/comptes qui correspondent aux critères** — défaut, comportement actuel, rien ne
  change.
* **Lire le contenu pour en extraire les acteurs** — active l'extraction d'entités nommées (organisations,
  personnes citées) dans les textes lus par les sources de cette recherche.

L'extraction ne tourne **jamais** en dehors du second mode : elle est hors-sujet pour une recherche qui vise
directement des sites/comptes.

### Pourquoi (contexte, pour mémoire)

Mesuré le 2026-10-12 (Q26) : au plus 17 % de la référence Wikidata existe comme candidat, parce que grappes
compare la source (site, compte) à la référence, alors que la référence attend souvent l'acteur cité dans
le texte. Plus de crawl ou d'autonomie d'apprentissage ne change rien (déjà mesuré, sans effet). Extraire
les entités nommées du texte lu est la seule piste qui peut lever ce plafond — mais seulement utile quand
la recherche porte sur la lecture de contenu, pas sur la recherche de sites/comptes eux-mêmes.

### Ce que momo construit

* Un réglage de recherche fermé, deux valeurs (voir plus haut), dans la configuration de lancement d'une
  recherche (même zone que les autres réglages de recherche existants).
* Un module d'extraction d'entités nommées, appelé seulement quand le mode est « lire le contenu » — pas
  de chemin qui l'appelle depuis l'autre mode.
* Les entités extraites deviennent candidates pour le recoupement (comme les sources le sont aujourd'hui),
  sans changer le fonctionnement existant pour l'autre mode.
* Documenter dans `MISSION.md` (ou son fichier de corrections) que l'extraction d'entités nommées est une
  méthode ajoutée par décision explicite (D83), pas dans la liste d'origine.

## 2. Personnes physiques — critère de correspondance (D84)

L'ancienne règle « en cas de doute, une personne, donc exclue » perdait des résultats utiles : une
recherche sur le football doit pouvoir ramener un compte Instagram public de sportif, personne physique,
parce qu'il correspond à la recherche — pas parce qu'on cible cette personne par un leak ou un autre moyen.

### La règle qui remplace Q21/D32

Trois issues possibles pour un compte de réseau social trouvé (personne physique ou pas) :

1. **Matche directement la recherche** (nom, mot-clé, critère explicite de la recherche) → gardé dans
   `resultat.csv`, qu'il s'agisse d'une personne ou d'une institution.
2. **Hors sujet / bruit** (apparaît sans répondre au critère, ex. quelqu'un qui a juste commenté) → exclu,
   comme avant.
3. **Doute** (le programme ne peut pas trancher avec certitude) → part dans un fichier séparé, proposition
   de nom `resultat_a_trancher.csv` (à confirmer par momo selon ce qui s'intègre le mieux), où Sednal
   décide au cas par cas.

`redact_persons` reste le réglage qui protège contre le ramassage de personnes non visées — il ne doit
jamais retirer un résultat qui répond réellement au critère de recherche.

### Boucle d'apprentissage

La décision de Sednal sur un cas du fichier « à trancher » (garder/exclure) compte comme une **ancre de
confiance** pour l'apprentissage (garde-fou de Q20/D41, resté actif par défaut — D82). Une décision
manuelle confirmée peut enseigner un mot-clé à grappes, au même titre qu'une entité confirmée descendant
d'une ancre existante.

### Ce que momo construit

* Le critère de correspondance (candidat matche-t-il la recherche ?) prime sur le type de compte
  (personne/institution) pour décider de l'inclusion dans `resultat.csv`.
* Nouveau fichier de sortie pour les cas douteux, avec une interface (web ou CLI, au choix de momo selon ce
  qui s'intègre le mieux à l'existant) où Sednal peut dire garder/exclure, cas par cas.
* Cette décision alimente le même mécanisme d'apprentissage que les ancres de confiance existantes
  (Q20/D41) — pas un second mécanisme parallèle.

## 3. Consigne d'interface (les deux points ci-dessus)

Nouveau réglage, nouveaux résultats : **lisibilité d'abord**, en suivant la charte déjà en place
(`suite/pilote/charte/`), pas une interface improvisée :

* **Jamais de couleur seule** pour porter une information (règle déjà appliquée par le composant Pastille,
  WCAG 1.4.1) : toujours la couleur ET le mot.
* **Vocabulaire fermé**, pas de reformulation libre — les deux valeurs du mode de recherche et les trois
  issues des personnes physiques sont des mots fixes, comme les rôles ou les états de source le sont déjà.
* Réutiliser les jetons de couleur et composants existants (`charte/jetons.css`, `charte/composants/`)
  plutôt qu'en inventer de nouveaux ; si aucun composant existant ne convient au mode de recherche ou au
  fichier « à trancher », en proposer un nouveau dans `charte/composants/` en suivant le même gabarit
  (README + preview.html) que les composants actuels, pas une mise en forme ad hoc dans une seule page.
