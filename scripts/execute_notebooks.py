from __future__ import annotations

import argparse
import os
from pathlib import Path

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NOTEBOOKS = (
    "01_datos.ipynb",
    "02_entrenamiento.ipynb",
    "03_evaluacion.ipynb",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ejecuta y guarda los notebooks reproducibles del proyecto."
    )
    parser.add_argument("notebooks", nargs="*", default=list(DEFAULT_NOTEBOOKS))
    parser.add_argument("--timeout", type=int, default=300)
    return parser.parse_args()


def execute(path: Path, timeout: int) -> None:
    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=timeout,
        kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
        record_timing=True,
    )
    client.execute(cwd=str(ROOT))
    nbformat.validate(notebook)
    nbformat.write(notebook, path)
    code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    if not all(cell.execution_count is not None for cell in code_cells):
        raise RuntimeError(f"Quedaron celdas sin ejecutar en {path}")
    print(f"Ejecutado: {path.name} ({len(code_cells)} celdas de código)")


def main() -> None:
    args = parse_args()
    cache_root = ROOT / ".cache" / "jupyter"
    ipython_dir = cache_root / "ipython"
    config_dir = cache_root / "config"
    runtime_dir = cache_root / "runtime"
    for path in (ipython_dir, config_dir, runtime_dir):
        path.mkdir(parents=True, exist_ok=True)
    os.environ["IPYTHONDIR"] = str(ipython_dir)
    os.environ["JUPYTER_CONFIG_DIR"] = str(config_dir)
    os.environ["JUPYTER_RUNTIME_DIR"] = str(runtime_dir)
    os.environ["MPLCONFIGDIR"] = str(cache_root / "matplotlib")
    for name in args.notebooks:
        path = ROOT / "notebooks" / name
        if not path.is_file():
            raise FileNotFoundError(path)
        execute(path, args.timeout)


if __name__ == "__main__":
    main()
