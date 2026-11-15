# Listes officielles (B1, spec 912)

Un fichier par sujet : `<sujet>.csv`, séparateur `;`, relevé à la main ou téléchargé depuis le site de l'autorité qui publie la liste. Aucune liste n'est relevée avant la validation des sujets par Sednal (`autocal/B1_sujets_proposes.md`).

````text
# source: <adresse de la page ou du fichier officiel>
# releve: <date du relevé, AAAA-MM-JJ>
nom;alias;site;siren
````

`nom` est obligatoire ; `alias` (séparés par `|`), `site` et `siren` sont facultatifs. Puis, sans réseau ni crédit :

````bash
python -m grappes.autocal.cli reference-officielle --sujet off-<sujet> --phrase "<phrase du sujet>" --liste autocal/listes_officielles/<sujet>.csv
````
