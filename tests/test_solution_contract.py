from collections.abc import Iterator

import pytest

import solucion

SCHEMA = "CREATE TABLE users (user_id INT PRIMARY KEY, name VARCHAR(50));"


class FakeRuntime:
    def __init__(self, outputs: list[str]) -> None:
        self.outputs: Iterator[str] = iter(outputs)

    def generate(self, prompt: str) -> str:
        assert SCHEMA in prompt
        return next(self.outputs)


def test_returns_one_select_without_executor(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(solucion, "_get_runtime", lambda: FakeRuntime(["SELECT name FROM users;"]))
    assert solucion.generar_sql(SCHEMA, "Lista los nombres") == "SELECT name FROM users;"


def test_repairs_once_after_execution_error(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime = FakeRuntime(["SELECT bad FROM users;", "SELECT name FROM users;"])
    monkeypatch.setattr(solucion, "_get_runtime", lambda: runtime)
    calls: list[str] = []

    def execute(sql: str) -> dict:
        calls.append(sql)
        if "bad" in sql:
            return {"ok": False, "columnas": [], "filas": [], "error": "Unknown column bad"}
        return {"ok": True, "columnas": ["name"], "filas": [["Ana"]], "error": None}

    assert solucion.generar_sql(SCHEMA, "Lista los nombres", execute) == "SELECT name FROM users;"
    assert len(calls) == 2


def test_rejects_empty_inputs() -> None:
    with pytest.raises(ValueError):
        solucion.generar_sql("", "pregunta")
