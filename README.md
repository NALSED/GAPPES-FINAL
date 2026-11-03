# GRAPPES

## Installation sur une VM neuve

Dépôt d'installation de référence (le moteur, à la racine, et `pilote/`, l'interface web). Pour une
installation complète, sans rien choisir à la main, voir [`INSTALLATION.md`](INSTALLATION.md) :

```bash
sudo apt-get update && sudo apt-get install -y git tmux
git clone https://github.com/NALSED/GAPPES-FINAL.git grappes-final
cd grappes-final
tmux new -s grappes
./installer_grappes.sh
```

Pour une installation minimale sans les paquets système (déjà présents) : `./installer.sh` puis
`./lancer.sh`.