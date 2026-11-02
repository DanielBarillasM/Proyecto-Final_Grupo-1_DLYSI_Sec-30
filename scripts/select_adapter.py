from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADAPTER_CONFIG = "adapter_config.json"
WEIGHT_CANDIDATES = ("adapter_model.safetensors", "adapter_model.bin")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def select_adapter(
    source: Path,
    target: Path,
    selection_basis: str = "external_evaluation",
) -> Path:
    source = source.resolve()
    target = target.resolve()
    if source == target:
        raise ValueError("La corrida fuente no puede ser el directorio adapter/ de entrega.")
    if not source.is_dir():
        raise FileNotFoundError(f"No existe el directorio de corrida {source}")

    config_path = source / ADAPTER_CONFIG
    if not config_path.is_file():
        raise FileNotFoundError(f"No existe {ADAPTER_CONFIG} en {source}")
    weights = [source / name for name in WEIGHT_CANDIDATES if (source / name).is_file()]
    if len(weights) != 1:
        raise FileNotFoundError(
            "La corrida debe contener exactamente un archivo de pesos: "
            + " o ".join(WEIGHT_CANDIDATES)
        )
    weight_path = weights[0]
    if weight_path.stat().st_size == 0:
        raise ValueError(f"El archivo de pesos está vacío: {weight_path}")

    target.mkdir(parents=True, exist_ok=True)
    for item in target.iterdir():
        if item.name != "README.md":
            shutil.rmtree(item) if item.is_dir() else item.unlink()
    shutil.copy2(config_path, target / config_path.name)
    shutil.copy2(weight_path, target / weight_path.name)

    manifest = {
        "selected_run": source.name,
        "selection_basis": selection_basis,
        "adapter_weight": weight_path.name,
        "sha256": sha256(weight_path),
    }
    selection_path = target / "selection.json"
    selection_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return selection_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Copia el adapter ganador al directorio oficial adapter/.")
    parser.add_argument("source", type=Path, help="Directorio de la corrida ganadora.")
    parser.add_argument(
        "--selection-basis",
        default="external_evaluation",
        help="Criterio verificable que justificó la selección.",
    )
    args = parser.parse_args()
    source = args.source if args.source.is_absolute() else ROOT / args.source
    target = ROOT / "adapter"
    selection_path = select_adapter(source, target, args.selection_basis)
    print(f"Adapter copiado a {target.resolve()}")
    print(f"Selección registrada en {selection_path}")


if __name__ == "__main__":
    main()
