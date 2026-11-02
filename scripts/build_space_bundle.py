from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "dist" / "huggingface-space"
TEMPLATE = ROOT / "deployment" / "huggingface-space" / "README.md"
ROOT_FILES = ("app.py", "production.py", "config.json")
SOURCE_DIRS = ("text2sql", "adapter")


def _requirements() -> str:
    lines: list[str] = []
    seen: set[str] = set()
    for filename in ("requirements.txt", "requirements-space.txt"):
        for raw_line in (ROOT / filename).read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("-r ") or line in seen:
                continue
            seen.add(line)
            lines.append(line)
    return "\n".join(lines) + "\n"


def build_bundle(output: Path = DEFAULT_OUTPUT, *, allow_outside_dist: bool = False) -> Path:
    output = output.resolve()
    allowed_root = (ROOT / "dist").resolve()
    outside_dist = output != allowed_root and allowed_root not in output.parents
    if outside_dist and not allow_outside_dist:
        raise ValueError(
            "El bundle solo puede generarse en dist/ o en una ruta explícita de prueba."
        )
    if output.exists():
        if outside_dist:
            raise ValueError("No se reemplaza una ruta existente fuera de dist/.")
        shutil.rmtree(output)
    output.mkdir(parents=True)

    shutil.copy2(TEMPLATE, output / "README.md")
    for filename in ROOT_FILES:
        shutil.copy2(ROOT / filename, output / filename)
    for dirname in SOURCE_DIRS:
        shutil.copytree(
            ROOT / dirname,
            output / dirname,
            ignore=shutil.ignore_patterns("*.safetensors", "__pycache__", "*.pyc"),
        )
    (output / "requirements.txt").write_text(_requirements(), encoding="utf-8", newline="\n")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Construye el repositorio mínimo del Space.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = build_bundle(args.output)
    files = sum(1 for path in output.rglob("*") if path.is_file())
    print(f"Bundle listo: {output} ({files} archivos)")


if __name__ == "__main__":
    main()
