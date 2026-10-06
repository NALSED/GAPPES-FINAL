> **OBSOLÈTE** : remplacé par `FINAL.md` (référence unique, 2026-10-06). Conservé pour l'historique uniquement ; ne pas s'y référer.

# Sortie finale attendue (complète CADRAGE.md, prioritaire sur §12 de MISSION.md)

## Livrable principal
`sorties/resultat.csv` : UNE SEULE COLONNE.
En-tête exactement : NOM
Une ligne par entité retenue, rien d'autre dans le fichier.

## Règles
- NOM = nom lisible de l'entité (organisation, média, site, canal, compte).
  Jamais un identifiant technique ni une URL brute.
- Dédoublonne les variantes d'écriture (casse, accents, espaces, suffixes).
- Trie par ordre alphabétique.
- N'exporte que les entités assignées à une grappe (confirmées et probables), seuil configurable.
- Un fichier par grappe si plusieurs grappes : `sorties/resultat_<grappe>.csv`.
- UTF-8 sans BOM.

## Inchangé
`entites.csv`, `appartenances.csv`, la base SQLite et le serveur MCP restent comme prévu :
ils gardent les scores, la confiance et les explications. `resultat.csv` est la sortie simple
destinée à être utilisée directement.

## Suite
Mets à jour DECISIONS.md, docs/utilisateur.md et ETAT.md. Ajoute des tests : dédoublonnage,
tri, entité sans nom lisible, fichier vide.
