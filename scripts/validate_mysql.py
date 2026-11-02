from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def statements(sql: str) -> list[str]:
    return [part.strip() for part in sql.split(";") if part.strip()]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def connect():
    import mysql.connector

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3307")),
        user=os.getenv("MYSQL_ADMIN_USER", "root"),
        password=os.getenv("MYSQL_ROOT_PASSWORD", "proyecto3_root"),
        autocommit=True,
    )


def setup_schema(connection, schema_id: str, split: str) -> None:
    folder = ROOT / "datos" / "esquemas" / split / schema_id
    cursor = connection.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS `{schema_id}`")
    cursor.execute(
        f"CREATE DATABASE `{schema_id}` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci"
    )
    cursor.execute(f"USE `{schema_id}`")
    for filename in ("schema.sql", "seed.sql"):
        for statement in statements((folder / filename).read_text(encoding="utf-8")):
            cursor.execute(statement)
    cursor.close()


def validate_rows(
    connection, rows: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    accepted: list[dict[str, Any]] = []
    discarded: list[dict[str, Any]] = []
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["schema_id"]].append(row)
    for schema_id, examples in groups.items():
        cursor = connection.cursor()
        cursor.execute(f"USE `{schema_id}`")
        for row in examples:
            candidate = dict(row)
            try:
                cursor.execute(row["sql"])
                cursor.fetchall()
                candidate["validado_mysql"] = True
                candidate["estado_validacion"] = "aceptado"
                accepted.append(candidate)
            except Exception as exc:
                candidate["validado_mysql"] = False
                candidate["estado_validacion"] = "descartado"
                candidate["motivo_descarte"] = f"ejecucion_mysql: {exc}"
                discarded.append(candidate)
        cursor.close()
    return accepted, discarded


def update_validation_csv(validated: list[dict[str, Any]]) -> None:
    valid_ids = {row["id"] for row in validated}
    path = ROOT / "resultados" / "validacion_propia.csv"
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
        fieldnames = list(rows[0].keys()) if rows else []
    for row in rows:
        if row["id"] not in valid_ids:
            raise RuntimeError(f"La consulta de referencia {row['id']} no ejecutó correctamente")
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Valida el dataset en MySQL 8.4.10.")
    parser.add_argument(
        "--keep-databases", action="store_true", help="No elimina las bases después de validar."
    )
    args = parser.parse_args()
    train_candidates = load_jsonl(ROOT / "datos" / "entrenamiento" / "candidatos.jsonl")
    validation = load_jsonl(ROOT / "datos" / "validacion" / "preguntas.jsonl")
    connection = connect()
    try:
        version_cursor = connection.cursor()
        version_cursor.execute("SELECT VERSION(), @@sql_mode")
        version, sql_mode = version_cursor.fetchone()
        version_cursor.close()
        if not str(version).startswith("8.4.10"):
            raise RuntimeError(f"Se requiere MySQL 8.4.10; versión detectada: {version}")
        if "ONLY_FULL_GROUP_BY" not in str(sql_mode):
            raise RuntimeError("ONLY_FULL_GROUP_BY no está habilitado")

        for schema_id in {row["schema_id"] for row in train_candidates}:
            setup_schema(connection, schema_id, "train")
        for schema_id in {row["schema_id"] for row in validation}:
            setup_schema(connection, schema_id, "validation")

        accepted, discarded = validate_rows(connection, train_candidates)
        valid_validation, invalid_validation = validate_rows(connection, validation)
        if invalid_validation:
            raise RuntimeError(
                f"Fallaron {len(invalid_validation)} consultas del conjunto de validación"
            )
        write_jsonl(ROOT / "datos" / "entrenamiento" / "aceptados.jsonl", accepted)
        write_jsonl(ROOT / "datos" / "descartes" / "descartados.jsonl", discarded)
        validation_path = ROOT / "datos" / "validacion" / "preguntas.jsonl"
        write_jsonl(validation_path, valid_validation)
        update_validation_csv(valid_validation)

        accepted_path = ROOT / "datos" / "entrenamiento" / "aceptados.jsonl"
        manifest_path = ROOT / "resultados" / "dataset_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest.update(
            {
                "mysql_version": version,
                "sql_mode": sql_mode,
                "mysql_validation_complete": True,
                "mysql_validated_at": datetime.now(timezone.utc).isoformat(),
                "training_accepted": len(accepted),
                "training_discarded": len(discarded),
                "validation_accepted": len(valid_validation),
                "validation_discarded": len(invalid_validation),
                "accepted_sha256": hashlib.sha256(accepted_path.read_bytes()).hexdigest(),
                "validation_sha256": hashlib.sha256(validation_path.read_bytes()).hexdigest(),
            }
        )
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        if len(accepted) < 2_000:
            raise RuntimeError("El dataset aceptado quedó por debajo de 2,000 pares")
    finally:
        if not args.keep_databases:
            cursor = connection.cursor()
            for schema_id in {row["schema_id"] for row in train_candidates + validation}:
                cursor.execute(f"DROP DATABASE IF EXISTS `{schema_id}`")
            cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
