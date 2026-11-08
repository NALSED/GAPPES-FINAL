# LibreTranslate auto-hébergé (tuile Traduction)

S'installe là où le disque des copies est monté sur la machine (≈ 8 Go avec les dépendances : environnement
Python, modèles, cache) — jamais un chemin en dur dans un fichier livré (retour du 08/11/2026 : le service
systemd pointait vers `/mnt/carte/pilote-copies/…`, le chemin d'une machine précédente, absent sur `.60` qui
monte son disque sur `/srv/grappes`).

````
python3 -m venv venv && ./venv/bin/pip install argostranslate libretranslate
XDG_DATA_HOME=$PWD/donnees XDG_CACHE_HOME=$PWD/cache ./venv/bin/python installer_modeles.py   # fr, es, de, it, ar, ru, zh <-> en
./lancer.sh                                                                                  # écoute en 127.0.0.1:5000 seulement
````

Puis, dans `config/pilote.yaml` :

````
suite:
  traduction_url: http://127.0.0.1:5000
````

Pour démarrer au lancement de la machine : le fichier livré porte `%CIBLE%` à la place du chemin (même
convention que `outils/searxng.service`), à remplacer par le chemin réel de ce dossier avant de l'installer :

````
sed "s|%CIBLE%|$PWD|g" libretranslate-pilote.service | sudo tee /etc/systemd/system/libretranslate-pilote.service
sudo systemctl daemon-reload && sudo systemctl enable --now libretranslate-pilote
````

Les modèles vont de et vers l'anglais ; une paire sans l'anglais (fr → es) passe par lui en deux appels, faits par `suite_traduction.traduire` (le pivot du service renvoie le texte anglais intermédiaire avec ces versions). Le processeur de la machine n'a pas AVX : les roues utilisées tournent quand même (contrôlé).
