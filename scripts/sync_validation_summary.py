from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sincroniza validacion_propia.csv con una corrida evaluada."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=ROOT / "resultados" / "corridas" / "ganador_direct.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = args.source if args.source.is_absolute() else ROOT / args.source
    target = ROOT / "resultados" / "validacion_propia.csv"

    with target.open(encoding="utf-8-sig", newline="") as handle:
        reference_rows = list(csv.DictReader(handle))
    with source.open(encoding="utf-8-sig", newline="") as handle:
        predictions = {row["id"]: row for row in csv.DictReader(handle)}

    if len(reference_rows) != 40 or set(predictions) != {row["id"] for row in reference_rows}:
        raise ValueError("La corrida y validacion_propia.csv no contienen los mismos 40 identificadores.")

    fields = [
        "id",
        "schema_id",
        "dificultad",
        "peso",
        "pregunta",
        "sql_referencia",
        "orden_importa",
        "sql_predicho",
        "error_generacion",
        "ejecutable",
        "correcto",
        "categoria_error",
        "latencia_ms",
    ]
    output_rows = []
    for reference in reference_rows:
        prediction = predictions[reference["id"]]
        output_rows.append(
            {
                **{key: reference.get(key, "") for key in fields},
                "sql_predicho": prediction["sql_predicho"],
                "error_generacion": prediction["error_generacion"],
                "ejecutable": prediction["ejecutable"].lower(),
                "correcto": prediction["correcto"].lower(),
                "categoria_error": prediction["categoria_error"],
                "latencia_ms": prediction["latencia_ms"],
            }
        )

    with target.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"Sincronizadas {len(output_rows)} filas desde {source} hacia {target}.")


if __name__ == "__main__":
    main()
