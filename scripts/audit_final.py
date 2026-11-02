from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "README.md",
    "app.py",
    "production.py",
    "config.json",
    "requirements-space.txt",
    "docs/PLAN_PROYECTO_FINAL.md",
    "docs/ARQUITECTURA.md",
    "docs/PROCEDENCIA.md",
    "informe/main.tex",
    "presentacion/index.html",
    "presentacion.pdf",
    "resultados/dataset_manifest.json",
    "resultados/resumen.json",
    "adapter/registry.json",
)
README_SECTIONS = (
    "## 1. Problemática",
    "## 2. Planificación",
    "## 3. Supuestos",
    "## 4. Modelo planteado",
    "## 5. Validación de hipótesis",
    "## 6. Herramientas y arquitectura",
    "## 7. Evidencias del pase a producción",
)


def _has_files(directory: Path, patterns: tuple[str, ...]) -> bool:
    return directory.is_dir() and any(
        path.is_file() for pattern in patterns for path in directory.glob(pattern)
    )


def collect_checks(root: Path = ROOT) -> dict[str, bool]:
    readme = (root / "README.md").read_text(encoding="utf-8")
    config = json.loads((root / "config.json").read_text(encoding="utf-8"))
    manifest = json.loads(
        (root / "resultados" / "dataset_manifest.json").read_text(encoding="utf-8")
    )
    registry = json.loads((root / "adapter" / "registry.json").read_text(encoding="utf-8"))
    presentation = root / "presentacion.pdf"
    deployment = root / "docs" / "evidencias" / "despliegue.md"
    deployment_text = deployment.read_text(encoding="utf-8") if deployment.is_file() else ""

    return {
        "required_files_present": all((root / path).is_file() for path in REQUIRED_FILES),
        "readme_has_seven_sections": all(section in readme for section in README_SECTIONS),
        "readme_declares_ai_use": "## Uso de inteligencia artificial" in readme,
        "dataset_is_frozen": (
            manifest.get("training_accepted") == 2592
            and manifest.get("validation_examples") == 40
            and manifest.get("training_sha256")
            == "9e28bcd7079dd7b2d41ca305b5f792055e78f3ecfdba455be1981295100049a8"
        ),
        "adapter_is_pinned": (
            config.get("adapter_repo_id") == registry.get("repo_id")
            and config.get("adapter_revision") == registry.get("revision")
            and bool(registry.get("adapter_sha256"))
        ),
        "adapter_is_enabled": config.get("usar_adapter") is True,
        "presentation_is_pdf": (
            presentation.is_file()
            and presentation.stat().st_size > 10_000
            and presentation.read_bytes()[:4] == b"%PDF"
        ),
        "deployment_recorded": bool(
            re.search(r"https://", deployment_text)
            and re.search(r"\b[0-9a-f]{40}\b", deployment_text)
        ),
        "screenshots_recorded": _has_files(
            root / "docs" / "evidencias" / "capturas", ("*.png", "*.jpg", "*.webp")
        ),
        "logs_recorded": _has_files(
            root / "docs" / "evidencias" / "logs", ("*.jsonl", "*.json")
        ),
        "smoke_tests_recorded": _has_files(
            root / "docs" / "evidencias" / "pruebas", ("*.md", "*.json", "*.txt")
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audita la entrega del Proyecto Final.")
    parser.add_argument(
        "--final",
        action="store_true",
        help="Exige evidencia del servicio público.",
    )
    args = parser.parse_args()
    checks = collect_checks()
    preparation = {
        "required_files_present",
        "readme_has_seven_sections",
        "readme_declares_ai_use",
        "dataset_is_frozen",
        "adapter_is_pinned",
        "adapter_is_enabled",
        "presentation_is_pdf",
    }
    required = set(checks) if args.final else preparation
    print(
        json.dumps(
            {"mode": "final" if args.final else "preparation", "checks": checks},
            indent=2,
            ensure_ascii=False,
        )
    )
    if not all(checks[name] for name in required):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
