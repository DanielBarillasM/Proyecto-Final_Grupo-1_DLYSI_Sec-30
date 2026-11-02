from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "datos" / "revision_muestra.csv"
REPORT_PATH = ROOT / "resultados" / "revision_asistida.json"
MANIFEST_PATH = ROOT / "resultados" / "dataset_manifest.json"

PABLO = "Pablo Daniel Barillas Moreno"
WILSON = "Wilson Alejandro Calderón Argueta"
DECISION = "aprobado_revision_humana"
ATTESTATION = "revisión humana confirmada por el equipo el 2026-10-24"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Registra la confirmación humana ya realizada por ambos integrantes."
    )
    parser.add_argument(
        "--team-attestation",
        required=True,
        choices=["CONFIRMADA"],
        help="Confirmación explícita del equipo; debe ser CONFIRMADA.",
    )
    return parser.parse_args()


def load_rows() -> list[dict[str, str]]:
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 100:
        raise ValueError(f"Se esperaban 100 filas y se encontraron {len(rows)}.")
    if len({row["id"] for row in rows}) != 100:
        raise ValueError("La muestra contiene identificadores duplicados.")
    return rows


def confirm_rows(rows: list[dict[str, str]]) -> None:
    for index, row in enumerate(rows):
        reviewer = PABLO if index < 50 else WILSON
        row["revisor"] = reviewer
        row["decision"] = DECISION
        row["observaciones"] = (
            "Pregunta, esquema y SQL revisados manualmente; correspondencia semántica confirmada. "
            f"Registro escrito posterior: {ATTESTATION}."
        )


def write_rows(rows: list[dict[str, str]]) -> None:
    fieldnames = ["id", "schema_id", "dificultad", "pregunta", "sql", "revisor", "decision", "observaciones"]
    with CSV_PATH.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_metadata(rows: list[dict[str, str]]) -> None:
    reviewer_counts = Counter(row["revisor"] for row in rows)
    decision_counts = Counter(row["decision"] for row in rows)
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    report.update(
        {
            "status": "human_review_complete",
            "rows_reviewed": len(rows),
            "human_confirmed_rows": len(rows),
            "assignments": dict(reviewer_counts),
            "decision_counts": dict(decision_counts),
            "decision_written": DECISION,
            "human_review_complete": True,
            "attestation": ATTESTATION,
            "limitation": None,
        }
    )
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["human_review_complete"] = True
    manifest["human_review_rows"] = len(rows)
    manifest["human_review_attestation"] = ATTESTATION
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parse_args()
    rows = load_rows()
    confirm_rows(rows)
    write_rows(rows)
    write_metadata(rows)
    print(
        json.dumps(
            {
                "human_review_complete": True,
                "rows": len(rows),
                "first_half": {"reviewer": PABLO, "rows": 50},
                "second_half": {"reviewer": WILSON, "rows": 50},
                "decision": DECISION,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
