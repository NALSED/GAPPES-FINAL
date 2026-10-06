# Phase 7 — données réelles (plan, non exécuté)

Statut : **proposée** (D17). Bloquée par Q2 (JSON anonymisés) et Q7 (base légale, conservation, `redact_persons`). Aucune donnée réelle n'est ingérée avant la réponse à Q7, et aucune donnée réelle ne passe par le compte gratuit.

## 1. Prérequis

````text
Q2  exemples de JSON anonymisés par écosystème   -> formats réels
Q7  base légale, retention_days, redact_persons  -> règles de conservation
Q3  langues des corpus                           -> normalisation et lexiques
````

## 2. Étapes

1. **Formats réels** : comparer les JSON fournis à `docs/conception/formats_json.md` ; adapter les fetchers (champs, imbrications, identifiants, dates) ; ajouter des fixtures anonymisées minimales et leurs tests ; consigner chaque écart en `DECISIONS.md`. Reprendre le cas `t.me` (D14) sur les vrais liens.
2. **Conservation et pseudonymisation** : appliquer `retention_days` (commande `purge`, planifiable) et `redact_persons` selon Q7 ; vérifier que les exports et le MCP respectent le réglage.
3. **Lexiques réels** : fournis par Sednal (jamais écrits par l'agent) ; `scale` et poids par grappe ; versionnés hors dépôt public si Sednal le demande.
4. **Calibrage des seuils** : `seuil_min`, `marge_ambiguite`, `crossref.*`, `crossref_floor`, `poids_complementaire` ; sur un échantillon annoté par Sednal, mesurer précision et rappel par grappe, choisir les valeurs, les tracer en `DECISIONS.md` (passage de « proposée » à « actée » par Sednal). Trancher Q15 avant.
5. **Passage à l'échelle** : rejouer `outils/charge.py` sur le volume réel estimé ; revoir les index SQLite si besoin.
6. **Recette** : `ingest → run → export` sur un lot réel ; revue manuelle d'un échantillon d'`explain` ; rejeu à l'identique.

## 3. Critères de sortie

* Tests verts, y compris sur les fixtures anonymisées.
* Écarts de format documentés ; aucun rejet inexpliqué.
* Seuils tracés avec leur justification ; Q15 tranchée.
* Q7 appliquée de bout en bout (conservation, pseudonymisation).
