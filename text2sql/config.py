from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    modelo_base: str
    modelo_revision: str | None
    adapter: Path
    adapter_repo_id: str | None
    adapter_revision: str | None
    usar_adapter: bool
    semilla: int


def load_config(path: str | Path | None = None) -> ProjectConfig:
    config_path = Path(path) if path else ROOT / "config.json"
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    missing = {"modelo_base", "adapter", "usar_adapter", "semilla"} - payload.keys()
    if missing:
        raise ValueError(f"Faltan campos en config.json: {', '.join(sorted(missing))}")

    adapter = Path(payload["adapter"])
    if not adapter.is_absolute():
        adapter = (config_path.parent / adapter).resolve()

    return ProjectConfig(
        modelo_base=str(payload["modelo_base"]),
        modelo_revision=(str(payload.get("modelo_revision", "")).strip() or None),
        adapter=adapter,
        adapter_repo_id=(str(payload.get("adapter_repo_id", "")).strip() or None),
        adapter_revision=(str(payload.get("adapter_revision", "")).strip() or None),
        usar_adapter=bool(payload["usar_adapter"]),
        semilla=int(payload["semilla"]),
    )
