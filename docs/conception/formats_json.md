# Formats JSON d entrée (proposition minimale, Q2)

Schémas **proposés**, non issus de données réelles : à remplacer par les vrais exemples de Sednal (Q2). Entrée : fichiers `.json` (liste) ou `.jsonl` (un objet par ligne). Les champs absents sont tolérés sauf ceux marqués obligatoires ; un enregistrement invalide est rejeté et compté dans le rapport de rejets, sans interrompre le lot.

## X (`x`)

Obligatoire : `author` (`{"handle": "@x"}` ou chaîne), et `id` ou `text`.

````json
{"id": "1001", "author": {"handle": "@Chef_Demo"}, "created_at": "2026-03-01T10:00:00Z",
 "text": "...", "lang": "fr",
 "entities": {"mentions": [{"handle": "@y"}], "urls": [{"url": "https://t.co/a", "expanded_url": "https://..."}], "hashtags": ["Cuisine"]},
 "metrics": {"likes": 10, "retweets": 3, "replies": 1}}
````

* `expanded_url` est préféré à `url` ; aucune résolution réseau.
* Sans `entities.mentions` / `hashtags`, extraction par regex dans le texte.
* `created_at` : ISO 8601 ou epoch en secondes ; illisible -> `ts = None`.
* `engagement` = likes + retweets + replies.

## Telegram (`telegram`)

Obligatoire : `channel`, et `message_id` ou `text`.

````json
{"message_id": 7, "channel": "@Canal", "date": "2026-03-02T08:30:00+00:00", "text": "...",
 "forwarded_from": "@autre", "entities": [{"type": "url", "url": "https://..."}, {"type": "mention", "text": "@y"}],
 "views": 120, "reactions": 5}
````

* Mentions = `@` du texte + entités `mention` + `forwarded_from`.
* `engagement` = views + reactions.

## Web (`web`)

Obligatoire : `url`.

````json
{"url": "https://www.exemple.test/page/", "title": "...", "text": "...", "fetched_at": "2026-03-03T12:00:00Z",
 "outlinks": ["https://autre.test/p"]}
````

* Source = domaine canonique. Texte = titre + corps.
* Liens sortants canonicalisés ; les liens vers le même domaine sont écartés.

## Identité et doublons

`obs_id` = SHA-256 tronqué de (écosystème, id natif, texte) : deux enregistrements identiques donnent le même `obs_id` et le second est compté comme doublon.
