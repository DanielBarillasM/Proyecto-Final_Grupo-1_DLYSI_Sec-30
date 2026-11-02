from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / ".cache" / "matplotlib"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
RUN_NAMES = ("qlora_r16", "qlora_r32")
COLORS = {"qlora_r16": "#146C64", "qlora_r32": "#B34D2D"}
LABELS = {"qlora_r16": "QLoRA r=16", "qlora_r32": "QLoRA r=32"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Exporta las curvas reales de loss desde trainer_state.json."
    )
    parser.add_argument(
        "--artifacts-root",
        type=Path,
        default=ROOT.parent / "artifacts_locales",
    )
    return parser.parse_args()


def select_state(run_dir: Path) -> Path:
    candidates = sorted(
        run_dir.glob("checkpoint-*/trainer_state.json"),
        key=lambda path: int(path.parent.name.split("-")[-1]),
    )
    if not candidates:
        raise FileNotFoundError(f"No se encontró trainer_state.json bajo {run_dir}")
    return candidates[-1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_rows(run_name: str, state_path: Path) -> list[dict[str, object]]:
    state = json.loads(state_path.read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = []
    for item in state["log_history"]:
        if "loss" in item:
            rows.append(
                {
                    "run": run_name,
                    "series": "train",
                    "step": int(item["step"]),
                    "epoch": float(item["epoch"]),
                    "loss": float(item["loss"]),
                }
            )
        if "eval_loss" in item:
            rows.append(
                {
                    "run": run_name,
                    "series": "validation",
                    "step": int(item["step"]),
                    "epoch": float(item["epoch"]),
                    "loss": float(item["eval_loss"]),
                }
            )
    if not rows:
        raise ValueError(f"La corrida {run_name} no contiene registros de loss")
    return rows


def write_csv(rows: list[dict[str, object]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["run", "series", "step", "epoch", "loss"])
        writer.writeheader()
        writer.writerows(rows)


def write_chart(rows: list[dict[str, object]], path: Path) -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.edgecolor": "#8EA3A3",
            "axes.labelcolor": "#173532",
            "xtick.color": "#587074",
            "ytick.color": "#587074",
            "text.color": "#173532",
        }
    )
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), constrained_layout=True)
    for axis, series, title in (
        (axes[0], "train", "Pérdida de entrenamiento"),
        (axes[1], "validation", "Pérdida de validación"),
    ):
        for run_name in RUN_NAMES:
            selected = [row for row in rows if row["run"] == run_name and row["series"] == series]
            axis.plot(
                [row["step"] for row in selected],
                [row["loss"] for row in selected],
                marker="o",
                markersize=4,
                linewidth=2.2,
                color=COLORS[run_name],
                label=LABELS[run_name],
            )
        axis.set_title(title, loc="left", fontsize=13, fontweight="bold")
        axis.set_xlabel("Paso")
        axis.set_ylabel("Loss (escala logarítmica)")
        axis.set_yscale("log")
        axis.grid(True, which="both", color="#D9E2E2", linewidth=0.7)
        axis.legend(frameon=False, fontsize=10)
    fig.suptitle("Curvas reales de las dos corridas QLoRA", fontsize=16, fontweight="bold")
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    output_dir = ROOT / "resultados"
    output_dir.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict[str, object]] = []
    sources: dict[str, dict[str, object]] = {}
    for run_name in RUN_NAMES:
        state_path = select_state(args.artifacts_root.resolve() / "runs" / run_name)
        rows = read_rows(run_name, state_path)
        all_rows.extend(rows)
        sources[run_name] = {
            "checkpoint": state_path.parent.name,
            "sha256": sha256(state_path),
            "train_points": sum(row["series"] == "train" for row in rows),
            "validation_points": sum(row["series"] == "validation" for row in rows),
        }

    csv_path = output_dir / "curvas_loss.csv"
    chart_path = output_dir / "curvas_loss.png"
    metadata_path = output_dir / "curvas_loss.json"
    write_csv(all_rows, csv_path)
    write_chart(all_rows, chart_path)
    metadata_path.write_text(
        json.dumps(
            {
                "status": "exported_from_completed_training",
                "series": ["train", "validation"],
                "runs": sources,
                "csv": csv_path.name,
                "chart": chart_path.name,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Curvas exportadas: {csv_path}, {chart_path}, {metadata_path}")


if __name__ == "__main__":
    main()
