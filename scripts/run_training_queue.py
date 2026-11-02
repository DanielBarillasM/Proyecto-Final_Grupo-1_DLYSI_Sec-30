from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = (
    ("qlora_r16", ROOT / "configuraciones" / "qlora_r16.json"),
    ("qlora_r32", ROOT / "configuraciones" / "qlora_r32.json"),
)


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def write_status(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def latest_checkpoint(output: Path) -> Path | None:
    checkpoints = [
        item
        for item in output.glob("checkpoint-*")
        if item.is_dir() and item.name.removeprefix("checkpoint-").isdigit()
    ]
    return max(checkpoints, key=lambda item: int(item.name.removeprefix("checkpoint-"))) if checkpoints else None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ejecuta las dos corridas QLoRA secuencialmente y permite reanudarlas.")
    parser.add_argument("--artifacts-root", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    artifacts = args.artifacts_root.resolve()
    runs = artifacts / "runs"
    logs = artifacts / "logs"
    runs.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    status_path = artifacts / "training_status.json"
    environment = os.environ.copy()
    environment["HF_HOME"] = str(artifacts / "hf-cache")
    environment["HF_HUB_OFFLINE"] = "1"
    status = {
        "status": "running",
        "queue_started_at": now(),
        "current": None,
        "completed": [],
        "runs": {},
    }
    write_status(status_path, status)

    for name, config in EXPERIMENTS:
        output = runs / name
        metrics = output / "run_metrics.json"
        if metrics.is_file():
            status["completed"].append(name)
            status["runs"][name] = {"status": "already_complete", "metrics": str(metrics)}
            write_status(status_path, status)
            continue

        command = [
            sys.executable,
            str(ROOT / "scripts" / "train_qlora.py"),
            "--config",
            str(config),
            "--output",
            str(output),
        ]
        checkpoint = latest_checkpoint(output)
        if checkpoint is not None:
            command.extend(["--resume-from-checkpoint", str(checkpoint)])

        log_path = logs / f"{name}.log"
        status["current"] = name
        status["runs"][name] = {
            "status": "running",
            "started_at": now(),
            "output": str(output),
            "log": str(log_path),
            "resume_from": str(checkpoint) if checkpoint else None,
        }
        write_status(status_path, status)
        with log_path.open("ab") as log:
            process = subprocess.Popen(
                command,
                cwd=ROOT,
                env=environment,
                stdout=log,
                stderr=subprocess.STDOUT,
            )
            status["runs"][name]["pid"] = process.pid
            write_status(status_path, status)
            return_code = process.wait()

        status["runs"][name]["finished_at"] = now()
        status["runs"][name]["return_code"] = return_code
        if return_code != 0 or not metrics.is_file():
            status["status"] = "failed"
            status["current"] = None
            status["failed_run"] = name
            write_status(status_path, status)
            raise SystemExit(return_code or 1)
        status["runs"][name]["status"] = "complete"
        status["runs"][name]["metrics"] = str(metrics)
        status["completed"].append(name)
        write_status(status_path, status)

    status["status"] = "training_complete"
    status["current"] = None
    status["queue_finished_at"] = now()
    write_status(status_path, status)


if __name__ == "__main__":
    main()
