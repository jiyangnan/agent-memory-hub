from pathlib import Path

import yaml


CONFIG_NAME = "agentmemory.yaml"


def config_path(root: Path) -> Path:
    return root / CONFIG_NAME


def load_config(root: Path) -> dict:
    path = config_path(root)
    if not path.exists():
        raise FileNotFoundError(f"missing {CONFIG_NAME}: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"{CONFIG_NAME} must contain a mapping")
    return payload

