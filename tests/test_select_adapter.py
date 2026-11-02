import json
from pathlib import Path

import pytest

from scripts.select_adapter import select_adapter


def test_selects_external_adapter_without_copying_checkpoints(tmp_path: Path) -> None:
    source = tmp_path / "artifacts_locales" / "runs" / "qlora_r16"
    source.mkdir(parents=True)
    (source / "adapter_config.json").write_text('{"r": 16}\n', encoding="utf-8")
    (source / "adapter_model.safetensors").write_bytes(b"adapter-weights")
    (source / "checkpoint-50").mkdir()
    (source / "run_metrics.json").write_text("{}\n", encoding="utf-8")
    target = tmp_path / "repo" / "adapter"
    target.mkdir(parents=True)
    (target / "README.md").write_text("# Adapter\n", encoding="utf-8")

    selection_path = select_adapter(source, target)

    assert sorted(path.name for path in target.iterdir()) == [
        "README.md",
        "adapter_config.json",
        "adapter_model.safetensors",
        "selection.json",
    ]
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    assert selection["selected_run"] == "qlora_r16"
    assert len(selection["sha256"]) == 64


def test_rejects_run_without_adapter_weights(tmp_path: Path) -> None:
    source = tmp_path / "run"
    source.mkdir()
    (source / "adapter_config.json").write_text("{}\n", encoding="utf-8")

    with pytest.raises(FileNotFoundError):
        select_adapter(source, tmp_path / "adapter")
