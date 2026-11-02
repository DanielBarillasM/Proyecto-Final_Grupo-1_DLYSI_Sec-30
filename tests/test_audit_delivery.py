import csv
import json
from pathlib import Path

from scripts.audit_delivery import collect_checks


def test_audit_derives_human_review_instead_of_trusting_manifest(tmp_path: Path) -> None:
    (tmp_path / "resultados").mkdir()
    (tmp_path / "datos").mkdir()
    (tmp_path / "adapter").mkdir()
    (tmp_path / "BITACORA.md").write_text("# Bitácora\n", encoding="utf-8")
    (tmp_path / "config.json").write_text(json.dumps({"usar_adapter": False}), encoding="utf-8")
    (tmp_path / "resultados/dataset_manifest.json").write_text(
        json.dumps(
            {
                "training_accepted": 2592,
                "mysql_validation_complete": True,
                "validation_examples": 40,
                "human_review_complete": True,
            }
        ),
        encoding="utf-8",
    )
    with (tmp_path / "datos/revision_muestra.csv").open(
        "w", encoding="utf-8", newline=""
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=["revisor", "decision"])
        writer.writeheader()
        for _ in range(100):
            writer.writerow({"revisor": "", "decision": "pendiente_revision_humana"})

    checks, _ = collect_checks(tmp_path)

    assert checks["human_review_complete"] is False


def test_audit_requires_real_adapter_weight(tmp_path: Path) -> None:
    adapter = tmp_path / "adapter"
    adapter.mkdir()
    (adapter / "adapter_config.json").write_text("{}\n", encoding="utf-8")
    (adapter / "adapter_model.safetensors").write_bytes(b"")

    assert not any(path.stat().st_size > 0 for path in adapter.glob("adapter_model.*"))
