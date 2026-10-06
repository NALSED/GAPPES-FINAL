# Réponses de Sednal n°3 — Q2 : échantillons de formats

* Dans /opt/grappes/donnees/echantillons/ : x_1.json, telegram_1.json, instagram_1.json, web_1.json.
* Ce ne sont PAS des exports réels. Ils sont construits d'après les documentations officielles (export Telegram Desktop, API X v2, API Instagram Graph) avec des valeurs inventées. web_1.json est une proposition de format : il n'existe pas de standard.
* Les fichiers se citent volontairement entre eux (exemple-a.example.test, compte_demo_a, canal_demo_a, t.me/+...) pour tester le recoupement entre écosystèmes.

## À faire

1. Compare ces formats à tes fetchers actuels et documente le résultat dans docs/conception/formats_json.md.
2. Adapte les fetchers X, Telegram et web, crée InstagramFetcher, avec des tests sur ces échantillons.
3. Liste dans QUESTIONS.md les points à confirmer sur de vrais exports : Telegram (href des text_link, champs des messages de service), X (id dans les mentions), Instagram (structure de paging), web (format d'entrée). N'invente aucun champ.
4. Revérifie D14 (liens t.me, y compris t.me/+...).

## Règles

* Q7 reste sans réponse : n'ingère aucune donnée réelle.
* Ne tente jamais de ré-identifier un compte.
