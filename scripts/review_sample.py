from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import sqlglot
from sqlglot import expressions as exp


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "datos" / "revision_muestra.csv"
SOURCE_PATH = ROOT / "datos" / "entrenamiento" / "aceptados.jsonl"
REPORT_PATH = ROOT / "resultados" / "revision_asistida.json"
MANIFEST_PATH = ROOT / "resultados" / "dataset_manifest.json"

ASSIGNMENTS = ("Pablo", "Wilson")
DECISION = "prevalidado_codex_pendiente_confirmacion_humana"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audita la muestra de 100 filas y prepara la confirmación humana sin atribuirla falsamente."
    )
    parser.add_argument("--write", action="store_true", help="Escribe asignaciones y revisión asistida en el CSV.")
    return parser.parse_args()


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_source() -> dict[str, dict]:
    rows = [json.loads(line) for line in SOURCE_PATH.read_text(encoding="utf-8").splitlines() if line]
    return {row["id"]: row for row in rows}


def validate_sql(sql: str) -> None:
    parsed = sqlglot.parse(sql, read="mysql")
    if len(parsed) != 1 or not isinstance(parsed[0], exp.Query):
        raise ValueError("La salida no contiene exactamente una consulta SELECT/CTE.")
    forbidden = (exp.Insert, exp.Update, exp.Delete, exp.Create, exp.Drop, exp.Alter, exp.Command)
    if any(parsed[0].find(kind) for kind in forbidden):
        raise ValueError("La consulta contiene una operación no permitida.")


def review(rows: list[dict[str, str]], source: dict[str, dict]) -> dict:
    if len(rows) != 100:
        raise ValueError(f"Se esperaban 100 filas y se encontraron {len(rows)}.")
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("La muestra contiene identificadores duplicados.")

    schema_counts: Counter[str] = Counter()
    difficulty_counts: Counter[str] = Counter()
    assignment_counts: Counter[str] = Counter()
    exact_matches = 0

    for index, row in enumerate(rows):
        original = source.get(row["id"])
        if original is None:
            raise ValueError(f"{row['id']}: no existe en el dataset aceptado.")
        fields = ("schema_id", "dificultad", "pregunta", "sql")
        mismatches = [field for field in fields if row[field] != original[field]]
        if mismatches:
            raise ValueError(f"{row['id']}: difiere del dataset aceptado en {', '.join(mismatches)}.")
        validate_sql(row["sql"])
        exact_matches += 1
        schema_counts[row["schema_id"]] += 1
        difficulty_counts[row["dificultad"]] += 1
        assignee = ASSIGNMENTS[0] if index < len(rows) // 2 else ASSIGNMENTS[1]
        assignment_counts[assignee] += 1
        row["revisor"] = f"{assignee} (asignado; confirmación pendiente)"
        row["decision"] = DECISION
        row["observaciones"] = (
            "Revisión técnica asistida por Codex: fila idéntica al dataset aceptado, "
            "SQL de solo lectura parseable y referencia validada en MySQL 8.4.10. "
            "El responsable asignado debe confirmar la coherencia pregunta-SQL y la redacción."
        )

    return {
        "status": "assisted_review_complete_human_confirmation_pending",
        "rows_reviewed": len(rows),
        "exact_source_matches": exact_matches,
        "read_only_parseable": len(rows),
        "mysql_reference_validation": "inherited_from_dataset_manifest",
        "assignments": dict(sorted(assignment_counts.items())),
        "difficulty": dict(sorted(difficulty_counts.items())),
        "schemas": dict(sorted(schema_counts.items())),
        "decision_written": DECISION,
        "human_review_complete": False,
        "limitation": (
            "Codex no atribuye una revisión humana a Pablo o Wilson. Cada responsable debe leer sus 50 filas, "
            "corregir observaciones si corresponde y sustituir la asignación por su nombre confirmado."
        ),
    }


def write_csv(rows: list[dict[str, str]]) -> None:
    fieldnames = ["id", "schema_id", "dificultad", "pregunta", "sql", "revisor", "decision", "observaciones"]
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    rows = load_rows(CSV_PATH)
    report = review(rows, load_source())
    if args.write:
        write_csv(rows)
        REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        manifest["assisted_review_complete"] = True
        manifest["assisted_review_rows"] = len(rows)
        manifest["human_review_complete"] = False
        MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
