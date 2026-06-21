from __future__ import annotations

from pathlib import Path
import yaml


def load_config(config_path: str | Path) -> dict:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found at {path}. Copy config/config.example.yaml to config/config.yaml and set keys."
        )
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)
