# Phase 7 — données réelles (plan, non exécuté)

Statut : **proposée** (D17). Bloquée par Q2 (JSON anonymisés) et la base légale (Q7b) ; Q7 est réglée sur `retention_days` et `redact_persons` (D20 : aucun des deux). Aucune donnée réelle n'est ingérée avant ces réponses, et aucune donnée réelle ne passe par le compte gratuit.

## 1. Prérequis

````text
Q2  exemples de JSON anonymisés par écosystème   -> formats réels
Q7b base légale                                  -> à fournir (retention_days et redact_persons : aucun, D20)
Q3  langues des corpus                           -> normalisation et lexiques
````

## 2. Étapes

1. **Formats réels** : comparer les JSON fournis à `docs/conception/formats_json.md` ; adapter les fetchers (champs, imbrications, identifiants, dates) ; ajouter des fixtures anonymisées minimales et leurs tests ; consigner chaque écart en `DECISIONS.md`. Reprendre le cas `t.me` (D14) sur les vrais liens.
2. **Conservation** : pas de `retention_days` ni de `redact_persons` (D20) ; `purge` reste manuelle. Documenter la base légale (Q7b) dans `docs/` dès qu'elle est fournie.
3. **Lexiques réels** : fournis par Sednal (jamais écrits par l'agent) ; `scale` et poids par grappe ; versionnés hors dépôt public si Sednal le demande.
4. **Calibrage des seuils** : `seuil_min`, `marge_ambiguite`, `crossref.*`, `crossref_floor`, `poids_complementaire` ; sur un échantillon annoté par Sednal, mesurer précision et rappel par grappe, choisir les valeurs, les tracer en `DECISIONS.md` (passage de « proposée » à « actée » par Sednal). (Q15 tranchée par D19.)
5. **Passage à l'échelle** : rejouer `outils/charge.py` sur le volume réel estimé ; revoir les index SQLite si besoin.
6. **Recette** : `ingest → run → export` sur un lot réel ; revue manuelle d'un échantillon d'`explain` ; rejeu à l'identique.

## 3. Critères de sortie

* Tests verts, y compris sur les fixtures anonymisées.
* Écarts de format documentés ; aucun rejet inexpliqué.
* Seuils tracés avec leur justification.
* Base légale documentée (Q7b).
