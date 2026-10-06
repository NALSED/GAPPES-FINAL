> **OBSOLÈTE** : remplacé par `FINAL.md` (référence unique, 2026-10-06). Conservé pour l'historique uniquement ; ne pas s'y référer.

# Phase 7 — données réelles (plan, non exécuté)

Statut : **proposée** (D17). Ne dépend plus que de vrais exports (Q2 : des échantillons synthétiques ont été livrés et les fetchers adaptés, D24 à D26 ; reste Q16 à Q19) ; Q7 et Q7b sont levées (D20, D21). Aucune donnée réelle n'est ingérée avant la livraison de vrais exports, et aucune donnée réelle ne passe par le compte gratuit.

## 1. Prérequis

````text
Q2  exemples de JSON anonymisés par écosystème   -> formats réels
Q7  levée (D20, D21)                             -> ni conservation limitée ni masquage
Q3  langues des corpus                           -> normalisation et lexiques
````

## 2. Étapes

1. **Formats réels** : (comparaison faite sur les échantillons synthétiques, `formats_json.md`) comparer les JSON fournis à `docs/conception/formats_json.md` ; adapter les fetchers (champs, imbrications, identifiants, dates) ; ajouter des fixtures anonymisées minimales et leurs tests ; consigner chaque écart en `DECISIONS.md`. Reprendre le cas `t.me` (D14) sur les vrais liens.
2. **Conservation** : pas de `retention_days` ni de `redact_persons` (D20, D21) ; `purge` reste manuelle.
3. **Lexiques réels** : fournis par Sednal (jamais écrits par l'agent) ; `scale` et poids par grappe ; versionnés hors dépôt public si Sednal le demande.
4. **Calibrage des seuils** : `seuil_min`, `marge_ambiguite`, `crossref.*`, `crossref_floor`, `poids_complementaire` ; sur un échantillon annoté par Sednal, mesurer précision et rappel par grappe, choisir les valeurs, les tracer en `DECISIONS.md` (passage de « proposée » à « actée » par Sednal). (Q15 tranchée par D19.)
5. **Passage à l'échelle** : rejouer `outils/charge.py` sur le volume réel estimé ; revoir les index SQLite si besoin.
6. **Recette** : `ingest → run → export` sur un lot réel ; revue manuelle d'un échantillon d'`explain` ; rejeu à l'identique.

## 3. Critères de sortie

* Tests verts, y compris sur les fixtures anonymisées.
* Écarts de format documentés ; aucun rejet inexpliqué.
* Seuils tracés avec leur justification.
