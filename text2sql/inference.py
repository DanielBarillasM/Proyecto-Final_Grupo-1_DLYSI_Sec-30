from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from .prompting import build_prompt, build_repair_prompt
from .sql_safety import validate_read_only_sql


class Generator(Protocol):
    def generate(self, prompt: str) -> str: ...


Executor = Callable[[str], dict[str, Any]]


def execute_safely(executor: Executor, sql: str) -> dict[str, Any]:
    try:
        result = executor(sql)
    except Exception as exc:
        return {"ok": False, "columnas": [], "filas": [], "error": str(exc)}
    return (
        result
        if isinstance(result, dict)
        else {
            "ok": False,
            "columnas": [],
            "filas": [],
            "error": "ejecutar devolvió un valor que no es dict",
        }
    )


def generate_sql(
    runtime: Generator,
    esquema: str,
    pregunta: str,
    ejecutar: Executor | None = None,
) -> str:
    first = validate_read_only_sql(runtime.generate(build_prompt(esquema, pregunta)))
    if ejecutar is None:
        return first
    first_result = execute_safely(ejecutar, first)
    if first_result.get("ok"):
        return first
    error = str(first_result.get("error") or "Error de ejecución no especificado")
    repaired = validate_read_only_sql(
        runtime.generate(build_repair_prompt(esquema, pregunta, first, error))
    )
    execute_safely(ejecutar, repaired)
    return repaired
