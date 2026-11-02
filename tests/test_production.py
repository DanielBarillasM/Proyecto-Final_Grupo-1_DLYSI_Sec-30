from __future__ import annotations

import json

import pytest

from production import InputValidationError, generate_for_production, validate_inputs
from text2sql.sql_safety import UnsafeSQL


class FakeRuntime:
    def __init__(self, output: str) -> None:
        self.output = output

    def generate(self, prompt: str) -> str:
        assert "CREATE TABLE" in prompt
        return self.output


SCHEMA = "CREATE TABLE clientes (id INT PRIMARY KEY, nombre VARCHAR(100));"


def test_validate_inputs_requires_create_table() -> None:
    with pytest.raises(InputValidationError):
        validate_inputs("SELECT 1", "Lista clientes")


def test_production_response_and_private_telemetry(tmp_path, monkeypatch) -> None:
    log_path = tmp_path / "usage.jsonl"
    monkeypatch.setenv("TEXT_TO_SQL_LOG_PATH", str(log_path))
    question = "Lista los nombres de los clientes"

    result = generate_for_production(
        SCHEMA,
        question,
        runtime=FakeRuntime("SELECT nombre FROM clientes;"),
    )

    assert result["sql"] == "SELECT nombre FROM clientes;"
    event = json.loads(log_path.read_text(encoding="utf-8"))
    assert event["status"] == "ok"
    assert event["schema_chars"] == len(SCHEMA)
    assert event["question_chars"] == len(question)
    assert SCHEMA not in log_path.read_text(encoding="utf-8")
    assert question not in log_path.read_text(encoding="utf-8")


def test_unsafe_model_output_is_rejected_and_logged(tmp_path, monkeypatch) -> None:
    log_path = tmp_path / "usage.jsonl"
    monkeypatch.setenv("TEXT_TO_SQL_LOG_PATH", str(log_path))

    with pytest.raises(UnsafeSQL):
        generate_for_production(
            SCHEMA,
            "Elimina los clientes",
            runtime=FakeRuntime("DELETE FROM clientes;"),
        )

    event = json.loads(log_path.read_text(encoding="utf-8"))
    assert event["status"] == "error"
    assert event["error_category"] == "UnsafeSQL"
