"""Configuration commune des tests : une copie de `config/` sans masquage des personnes, pour les
tests qui vérifient des identifiants en clair (le défaut du dépôt est `redact_persons: true`, D30)."""

import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _copie_claire() -> Path:
    dest = Path(tempfile.mkdtemp(prefix="grappes_config_clair_")) / "config"
    shutil.copytree(ROOT / "config", dest)
    path = dest / "scoring.yaml"
    path.write_text(
        path.read_text(encoding="utf-8").replace("redact_persons: true", "redact_persons: false"),
        encoding="utf-8",
    )
    return dest


CONFIG_CLAIR = _copie_claire()
