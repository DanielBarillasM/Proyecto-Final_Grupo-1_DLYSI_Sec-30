from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

WEIGHTS = {"facil": 1, "media": 2, "dificil": 3}


def _normalized(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (int, float, Decimal)):
        try:
            return Decimal(str(value)).quantize(Decimal("0.01"))
        except InvalidOperation:
            return str(value)
    return str(value).strip()


def _project_rows(
    result: Mapping[str, Any],
    expected_columns: Sequence[str],
) -> list[tuple[Any, ...]] | None:
    columns = [str(column) for column in result.get("columnas", [])]
    if not set(expected_columns).issubset(columns):
        return None
    positions = [columns.index(column) for column in expected_columns]
    projected: list[tuple[Any, ...]] = []
    for row in result.get("filas", []):
        projected.append(tuple(_normalized(row[index]) for index in positions))
    return projected


def execution_match(
    expected: Mapping[str, Any],
    predicted: Mapping[str, Any],
    *,
    order_matters: bool = False,
) -> bool:
    if not expected.get("ok") or not predicted.get("ok"):
        return False
    expected_columns = [str(column) for column in expected.get("columnas", [])]
    expected_rows = _project_rows(expected, expected_columns)
    predicted_rows = _project_rows(predicted, expected_columns)
    if expected_rows is None or predicted_rows is None:
        return False
    if order_matters:
        return expected_rows == predicted_rows
    return sorted(expected_rows, key=repr) == sorted(predicted_rows, key=repr)


@dataclass(frozen=True, slots=True)
class ScoredExample:
    difficulty: str
    correct: bool


def weighted_execution_accuracy(examples: Iterable[ScoredExample]) -> float:
    earned = 0
    possible = 0
    for example in examples:
        weight = WEIGHTS[example.difficulty]
        possible += weight
        earned += weight if example.correct else 0
    return earned / possible if possible else 0.0


def categorize_error(sql: str, execution: Mapping[str, Any], matched: bool) -> str:
    if matched:
        return "correcto"
    message = str(execution.get("error") or "").lower()
    if not execution.get("ok"):
        if "syntax" in message or "sintaxis" in message:
            return "sintaxis"
        if "unknown column" in message or "doesn't exist" in message or "no existe" in message:
            return "entidad_inexistente"
        return "ejecucion"
    upper = sql.upper()
    if " JOIN " in upper:
        return "join"
    if any(token in upper for token in ("GROUP BY", "COUNT(", "SUM(", "AVG(")):
        return "agregacion"
    if " WHERE " in upper:
        return "filtro"
    return "resultado_distinto"
