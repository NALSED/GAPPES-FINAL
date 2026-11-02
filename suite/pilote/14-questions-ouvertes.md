# 14 — Questions ouvertes

Ce qui **n'est pas tranché** au 26/10/2026. Ne décide rien ici tout seul : remonte la question à Sednal,
qui a le dernier mot sur chaque point du projet.

---

## 1. Les rôles CATALOGUE et RAPPROCHER sur une source

Quatre sources portent aujourd'hui un rôle qu'on pensait réservé aux outils : `data.europa.eu` et
`org-id.guide` en CATALOGUE, `Wikidata (SPARQL)` et `radio-browser` en RAPPROCHER.

Faut-il l'accepter — une source peut cataloguer ou rapprocher — ou réserver ces deux rôles aux outils et
reclasser ces quatre sources ? Ça change le contrôle n° 4 de `verifier_plan()`.

**Bloquant pour** : la liste des rôles autorisés dans la fiche source.

## 2. La translittération

`Երևան` → `Yerevan`. Ce n'est pas de la traduction. Option de la tuile Traduction, ou tuile à part ?

**Pas bloquant tant qu'aucune source non latine n'entre dans grappes.** Le devient dès la première.

## 3. Le moteur de traduction par défaut

LibreTranslate auto-hébergé (pas de quota, pas de clé, rien ne sort, mais quelques gigaoctets de
modèles) ou DeepL (meilleure qualité, 500 000 caractères par mois, clé requise, données qui sortent) ?

Proposition faite à Sednal : LibreTranslate par défaut, DeepL en option. **Pas encore validé.**

## 4. Le modèle d'IA

Sednal a un serveur d'IA auto-hébergée dans le cadre d'un contrat professionnel. Question posée, **sans
réponse à ce jour** : est-il réutilisable pour grappes, ou strictement réservé au client ?

Tant que ce n'est pas tranché, l'Assistant IA vise `local (Ollama)`.

## 5. La place disque sur la VM

81 Go restants. yente en réclame 60. Aleph n'a pas été pesé. Les modèles LibreTranslate ajoutent quelques
gigaoctets.

**Ça ne tient probablement pas.** À arbitrer avant d'installer quoi que ce soit de lourd.

## 6. Radio France : les conditions d'utilisation

Une mention relayée sur un forum — **non confirmée dans les CGU elles-mêmes** — indiquerait que les
données renvoyées ne doivent pas être stockées, ni passer par un serveur intermédiaire qui les conserve.
C'est exactement ce que grappes fait par construction.

**À vérifier dans les CGU avant d'en faire une source du projet.** L'interdiction visant les
applications d'agrégation de flux live et de podcasts, elle, est confirmée et ne nous concerne pas.

## 7. Le Tableau de bord et le Tri

Aucune spécification. Reportés volontairement par Sednal. Les onglets restent visibles et grisés.
**N'improvise rien.**

## 8. Le périmètre légal : personnes morales seulement ?

**Tranché le 26/10/2026.** grappes a pour objet les **personnes morales** — entreprises, associations,
organisations. Les recommandations de la CNIL de juin 2024 disent qu'une compilation d'informations en
ligne pour constituer le profil d'une personne nommément désignée **ne relève pas de l'intérêt légitime**
et demande son consentement ; le RGPD protège les personnes physiques, pas les personnes morales, donc
rester sur les personnes morales reste hors de ce champ.

C'est maintenant la **règle non négociable n° 8** de `00-MAIN.md` : aucune fonction de recherche par nom
de personne physique, et les données de dirigeants ne servent jamais de clé de rapprochement. Détail dans
`15-mecanismes-et-references.md` §8.

## 9. Le code Admiralty remplace « Origine de l'information »

**Tranché le 26/10/2026.** Le champ fiche-source devient **Fiabilité de la source** (lettre A–F, code
Admiralty), déjà en place dans `maquettes/Main.dc.html` et `05-reglages-sources.md`. La crédibilité de
l'information (1–6, l'autre axe du même code) reste ouverte : elle s'appliquera à la fiche de résultat,
pas encore maquettée. Voir `15-mecanismes-et-references.md` §2.

## 10. L'onglet Tri est-il l'écran de validation des rapprochements ?

Tous les moteurs de rapprochement sérieux prévoient une étape de confirmation humaine. Elle n'existe
nulle part dans la maquette. L'onglet *Tri*, sans spécification, est le candidat naturel.

**Mise en place le 26/10/2026**, voir `16-onglet-tri.md` et `maquettes/Tri.dc.html`. Reste ouvert : la
crédibilité 1–6 d'un fait (axe qui s'affichera sur la fiche de résultat, pas encore maquettée) n'est pas
construite — seul le score de rapprochement l'est.

---

## Ce qui est tranché, pour mémoire

Pour éviter de rouvrir des discussions closes :

- Le plan de travail est **libre**, façon n8n. On pose, **puis** on relie. Jamais de lien automatique.
- Le rôle **LIEN** s'appelle désormais **RAPPROCHER**. Un *lien* est une flèche entre deux tuiles.
- La fenêtre d'aide se **replie**, elle ne se ferme pas, et le verbe est *Replier*, pas « Réduire ».
- L'**Assistant IA** est éteint à la livraison, et l'allumer passe par un avertissement.
- Les **clés d'API** ne s'affichent jamais en clair.
- Les sources portent un champ **Langue**.
- La tuile **Traduction** sort vers **plusieurs langues** à la fois.
- grappes vise les **personnes morales** ; aucune recherche par nom de personne physique.
- La fiche source porte une **Fiabilité (A–F)**, code Admiralty, à la place d'« Origine de l'information ».
- L'onglet **Tri** est l'écran de validation des rapprochements proposés par Fusion/doublons.
