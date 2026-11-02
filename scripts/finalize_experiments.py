from __future__ import annotations

import argparse
import csv
import json
import os
import random
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def write_json(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def selection_reason(summaries: dict[str, dict], winner: str) -> str:
    other = "qlora_r32" if winner == "qlora_r16" else "qlora_r16"
    left, right = summaries[winner], summaries[other]
    if left["weighted_ex"] != right["weighted_ex"]:
        return "mayor EX ponderada"
    if left["ex_by_difficulty"]["dificil"] != right["ex_by_difficulty"]["dificil"]:
        return "mejor EX difícil tras empate en EX total"
    if left["executable_rate"] != right["executable_rate"]:
        return "mayor tasa ejecutable tras empate en EX"
    if left["latency_p95_ms"] != right["latency_p95_ms"]:
        return "menor latencia p95 tras empate en EX y ejecutabilidad"
    return "menor rango tras empate en todas las métricas"


def bootstrap_hidden_interval(csv_path: Path, *, samples: int = 20_000, penalty: float = 0.10) -> list[float]:
    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    weights = {"facil": 1, "media": 2, "dificil": 3}
    values = [(weights[row["dificultad"]], row["correcto"].lower() == "true") for row in rows]
    rng = random.Random(2026)
    scores: list[float] = []
    for _ in range(samples):
        draw = [values[rng.randrange(len(values))] for _ in values]
        total = sum(weight for weight, _ in draw)
        earned = sum(weight for weight, correct in draw if correct)
        scores.append(earned / total)
    scores.sort()
    low = scores[int(0.025 * (samples - 1))]
    high = scores[int(0.975 * (samples - 1))]
    return [round(max(0.0, low - penalty), 3), round(max(0.0, high - penalty), 3)]


def run_step(status_path: Path, status: dict, name: str, command: list[str], log_path: Path, environment: dict) -> None:
    status["current"] = name
    status["steps"][name] = {"status": "running", "started_at": now(), "log": str(log_path)}
    write_json(status_path, status)
    with log_path.open("ab") as log:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            env=environment,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        status["steps"][name]["pid"] = process.pid
        write_json(status_path, status)
        return_code = process.wait()
    status["steps"][name]["return_code"] = return_code
    status["steps"][name]["finished_at"] = now()
    if return_code != 0:
        status["status"] = "failed"
        status["failed_step"] = name
        status["current"] = None
        write_json(status_path, status)
        raise SystemExit(return_code)
    status["steps"][name]["status"] = "complete"
    status["completed"].append(name)
    write_json(status_path, status)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Espera los entrenamientos y completa evaluación y selección.")
    parser.add_argument("--artifacts-root", required=True, type=Path)
    parser.add_argument("--poll-seconds", type=int, default=30)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    artifacts = args.artifacts_root.resolve()
    training_status_path = artifacts / "training_status.json"
    final_status_path = artifacts / "finalization_status.json"
    logs = artifacts / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    status = {
        "status": "waiting_for_training",
        "started_at": now(),
        "current": None,
        "completed": [],
        "steps": {},
    }
    write_json(final_status_path, status)

    while True:
        if training_status_path.is_file():
            training = load_json(training_status_path)
            if training.get("status") == "training_complete":
                break
            if training.get("status") == "failed":
                status["status"] = "blocked_by_training_failure"
                status["training_status"] = training
                write_json(final_status_path, status)
                raise SystemExit(1)
        time.sleep(max(5, args.poll_seconds))

    status["status"] = "running"
    status["training_completed_at"] = now()
    write_json(final_status_path, status)
    environment = os.environ.copy()
    environment["HF_HOME"] = str(artifacts / "hf-cache")
    environment["HF_HUB_OFFLINE"] = "1"
    python = sys.executable
    runs = artifacts / "runs"
    validation_script = str(ROOT / "scripts" / "run_validation.py")

    for name in ("qlora_r16", "qlora_r32"):
        output_json = ROOT / "resultados" / "corridas" / f"{name}.json"
        if output_json.is_file():
            status["completed"].append(name)
            status["steps"][name] = {"status": "already_complete", "output": str(output_json)}
            write_json(final_status_path, status)
            continue
        run_step(
            final_status_path,
            status,
            name,
            [python, validation_script, "--name", name, "--adapter", str(runs / name)],
            logs / f"evaluate_{name}.log",
            environment,
        )

    summaries = {
        name: load_json(ROOT / "resultados" / "corridas" / f"{name}.json")
        for name in ("qlora_r16", "qlora_r32")
    }
    winner = max(
        summaries,
        key=lambda name: (
            summaries[name]["weighted_ex"],
            summaries[name]["ex_by_difficulty"]["dificil"],
            summaries[name]["executable_rate"],
            -summaries[name]["latency_p95_ms"],
            name == "qlora_r16",
        ),
    )
    winner_path = runs / winner
    winner_reason = selection_reason(summaries, winner)
    status["winner"] = winner
    status["selection_reason"] = winner_reason
    status["selection_rule"] = (
        "weighted_ex, difficult_ex, executable_rate, inverse latency_p95_ms, prefer_r16"
    )
    write_json(final_status_path, status)

    for name, repair in (("ganador_direct", False), ("ganador_repair", True)):
        command = [python, validation_script, "--name", name, "--adapter", str(winner_path)]
        if repair:
            command.append("--repair")
        run_step(
            final_status_path,
            status,
            name,
            command,
            logs / f"evaluate_{name}.log",
            environment,
        )

    run_step(
        final_status_path,
        status,
        "select_adapter",
        [
            python,
            str(ROOT / "scripts" / "select_adapter.py"),
            str(winner_path),
            "--selection-basis",
            winner_reason,
        ],
        logs / "select_adapter.log",
        environment,
    )

    project_config_path = ROOT / "config.json"
    project_config = load_json(project_config_path)
    project_config["usar_adapter"] = True
    write_json(project_config_path, project_config)

    baseline = load_json(ROOT / "resultados" / "corridas" / "baseline.json")
    direct = load_json(ROOT / "resultados" / "corridas" / "ganador_direct.json")
    repair = load_json(ROOT / "resultados" / "corridas" / "ganador_repair.json")
    training_metrics = {
        name: load_json(runs / name / "run_metrics.json")
        for name in ("qlora_r16", "qlora_r32")
    }
    summary_path = ROOT / "resultados" / "resumen.json"
    summary = load_json(summary_path)
    summary["status"] = "experiments_complete"
    summary["experiments"]["baseline"] = {
        key: baseline[key] for key in ("weighted_ex", "executable_rate", "latency_p95_ms")
    }
    for name in ("qlora_r16", "qlora_r32"):
        summary["experiments"][name] = {
            "weighted_ex": summaries[name]["weighted_ex"],
            "executable_rate": summaries[name]["executable_rate"],
            "latency_p95_ms": summaries[name]["latency_p95_ms"],
            "trainable_parameters": training_metrics[name]["trainable_parameters"],
            "training_minutes": training_metrics[name]["duration_seconds_wall"] / 60,
        }
    summary["experiments"]["direct"] = {"weighted_ex": direct["weighted_ex"]}
    summary["experiments"]["repair"] = {"weighted_ex": repair["weighted_ex"]}
    summary["selected_adapter"] = winner
    summary["selection_reason"] = winner_reason
    summary["hidden_ex_prediction"] = round(max(0.0, direct["weighted_ex"] - 0.10), 3)
    summary["hidden_ex_prediction_interval"] = bootstrap_hidden_interval(
        ROOT / "resultados" / "corridas" / "ganador_direct.csv"
    )
    summary["hidden_ex_prediction_method"] = (
        "Bootstrap determinista de 20,000 remuestras por pregunta con semilla 2026; "
        "al intervalo y al punto local se restan 0.10 por cambio de dominio."
    )
    summary["note"] = (
        "Métricas medidas localmente en RTX 4050 Laptop. La predicción oculta y su intervalo son "
        "estimaciones conservadoras por cambio de dominio; no son mediciones del conjunto oculto."
    )
    write_json(summary_path, summary)

    run_step(
        final_status_path,
        status,
        "update_documents",
        [python, str(ROOT / "scripts" / "update_result_documents.py"), "--artifacts-root", str(artifacts)],
        logs / "update_documents.log",
        environment,
    )

    status["status"] = "experiments_complete"
    status["current"] = None
    status["finished_at"] = now()
    status["summary"] = str(summary_path)
    write_json(final_status_path, status)


if __name__ == "__main__":
    main()
