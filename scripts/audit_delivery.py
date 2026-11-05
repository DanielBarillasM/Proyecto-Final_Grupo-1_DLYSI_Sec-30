from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def collect_checks(root: Path) -> tuple[dict[str, bool], list[str]]:
    manifest = json.loads((root / "resultados/dataset_manifest.json").read_text(encoding="utf-8"))
    config = json.loads((root / "config.json").read_text(encoding="utf-8"))
    required = [
        "solucion.py",
        "config.json",
        "requirements.txt",
        "adapter/README.md",
        "datos/revision_muestra.csv",
        "informe/main.tex",
        "informe.pdf",
        "presentacion/index.html",
        "presentacion.pdf",
        "resultados/validacion_propia.csv",
        "BITACORA.md",
        "CONTRIBUCIONES.md",
        "web/lib/client.ts",
        "web/lib/utils.ts",
    ]
    missing = [path for path in required if not (root / path).exists()]
    adapter_dir = root / "adapter"
    adapter_config = adapter_dir / "adapter_config.json"
    weights = [adapter_dir / name for name in ("adapter_model.safetensors", "adapter_model.bin")]
    adapter_ready = adapter_config.is_file() and any(
        path.stat().st_size > 0 for path in weights if path.is_file()
    )

    with (root / "datos/revision_muestra.csv").open(encoding="utf-8-sig", newline="") as stream:
        review_rows = list(csv.DictReader(stream))
    pablo = "Pablo Daniel Barillas Moreno"
    wilson = "Wilson Alejandro Calderón Argueta"
    human_decisions = {"aprobado_revision_humana", "corregido_revision_humana"}
    human_review_complete = (
        len(review_rows) == 100
        and all(row.get("revisor") == pablo for row in review_rows[:50])
        and all(row.get("revisor") == wilson for row in review_rows[50:])
        and all(row.get("decision") in human_decisions for row in review_rows)
    )
    bitacora = (root / "BITACORA.md").read_text(encoding="utf-8")
    bitacora_entries = len(re.findall(r"^## \d{4}-\d{2}-\d{2} - .+$", bitacora, re.MULTILINE))
    expected_runs = {
        "baseline.csv", "baseline.json",
        "qlora_r16.csv", "qlora_r16.json",
        "qlora_r32.csv", "qlora_r32.json",
        "ganador_direct.csv", "ganador_direct.json",
        "ganador_repair.csv", "ganador_repair.json",
    }
    runs_dir = root / "resultados/corridas"
    run_files = {path.name for path in runs_dir.iterdir()} if runs_dir.is_dir() else set()
    checks = {
        "required_files_present": not missing,
        "training_pairs_at_least_2000": manifest["training_accepted"] >= 2000,
        "mysql_validation_complete": manifest["mysql_validation_complete"],
        "validation_has_40_examples": manifest["validation_examples"] == 40,
        "human_review_complete": human_review_complete and manifest["human_review_complete"],
        "adapter_ready": adapter_ready,
        "adapter_enabled_consistently": bool(config["usar_adapter"]) == adapter_ready,
        "adapter_selected": (adapter_dir / "selection.json").is_file(),
        "experiment_outputs_complete": expected_runs.issubset(run_files),
        "bitacora_has_8_entries": bitacora_entries >= 8,
    }
    return checks, missing


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audita la preparación o la entrega final del proyecto."
    )
    parser.add_argument(
        "--final",
        action="store_true",
        help="Exige revisión humana, corridas, adapter seleccionado y bitácora completa.",
    )
    args = parser.parse_args()
    checks, missing = collect_checks(ROOT)
    result = {
        "mode": "final" if args.final else "preparation",
        "checks": checks,
        "missing": missing,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    preparation_checks = {
        "required_files_present",
        "training_pairs_at_least_2000",
        "mysql_validation_complete",
        "validation_has_40_examples",
        "adapter_enabled_consistently",
    }
    required_checks = set(checks) if args.final else preparation_checks
    if not all(checks[name] for name in required_checks):
        raise SystemExit(1)

if __name__ == "__main__":
    main()
