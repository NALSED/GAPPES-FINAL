#!/usr/bin/env bash
# RSSHub auto-hébergé (point 15, retour de Sednal du 08/11/2026 — Sednal décide de l'installer). Même commande
# que l'instance déjà vérifiée en réel sur .250/.115 (QUESTIONS.md, 3.8.10, D85, 03/11/2026), posée là à la
# main : ce script la rejoue à l'identique sur une nouvelle machine, au lieu de la retaper. Image Docker
# OFFICIELLE `diygod/rsshub:latest`, aucune base à importer (contrairement à Overpass), écoute en 127.0.0.1
# seulement.
# Usage : outils/installer_rsshub.sh   (RSSHUB_PORT=1200 par défaut, le port de RSSHub lui-même).
# Idempotent : si le conteneur existe déjà, il est seulement (re)démarré.
set -euo pipefail
PORT="${RSSHUB_PORT:-1200}"
if docker ps -a --format '{{.Names}}' | grep -qx rsshub; then docker start rsshub >/dev/null; echo "Conteneur rsshub démarré."; exit 0; fi
docker run -d --name rsshub --restart unless-stopped -p "127.0.0.1:$PORT:1200" diygod/rsshub:latest
echo "RSSHub installé : http://127.0.0.1:$PORT/ (ajouter « suite: {rsshub_url: http://127.0.0.1:$PORT} » dans config/pilote.yaml pour le brancher à la tuile RSSHub)."
