from __future__ import annotations

import json
import os
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from text2sql.config import load_config
from text2sql.inference import generate_sql
from text2sql.runtime import TextToSQLRuntime
from text2sql.sql_safety import validate_read_only_sql

ROOT = Path(__file__).resolve().parent
DEFAULT_LOG_PATH = ROOT / "logs" / "usage.jsonl"
MAX_SCHEMA_CHARS = 50_000
MAX_QUESTION_CHARS = 1_000


class Generator(Protocol):
    def generate(self, prompt: str) -> str: ...


class InputValidationError(ValueError):
    """La solicitud no cumple el contrato público del servicio."""


class BackendUnavailableError(RuntimeError):
    """La puerta pública no pudo comunicarse con la API local."""


_runtime: TextToSQLRuntime | None = None
_runtime_lock = threading.Lock()


def validate_inputs(schema: str, question: str) -> tuple[str, str]:
    schema = schema.strip()
    question = question.strip()
    if len(schema) < 20 or "CREATE TABLE" not in schema.upper():
        raise InputValidationError(
            "El esquema debe incluir al menos una sentencia CREATE TABLE válida."
        )
    if len(schema) > MAX_SCHEMA_CHARS:
        raise InputValidationError(f"El esquema excede {MAX_SCHEMA_CHARS:,} caracteres.")
    if len(question) < 3:
        raise InputValidationError("La pregunta debe contener al menos 3 caracteres.")
    if len(question) > MAX_QUESTION_CHARS:
        raise InputValidationError(f"La pregunta excede {MAX_QUESTION_CHARS:,} caracteres.")
    return schema, question


def get_runtime() -> TextToSQLRuntime:
    global _runtime
    if _runtime is None:
        with _runtime_lock:
            if _runtime is None:
                _runtime = TextToSQLRuntime(load_config())
    return _runtime


def _log_path() -> Path:
    configured = os.getenv("TEXT_TO_SQL_LOG_PATH", "").strip()
    return Path(configured).expanduser() if configured else DEFAULT_LOG_PATH


def record_event(event: dict[str, object]) -> None:
    """Guarda telemetría técnica; nunca registra el esquema ni la pregunta."""

    path = _log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def generate_for_production(
    schema: str,
    question: str,
    *,
    runtime: Generator | None = None,
) -> dict[str, object]:
    request_id = uuid.uuid4().hex[:12]
    started = time.perf_counter()
    schema_chars = len(schema)
    question_chars = len(question)
    status = "error"
    error_category: str | None = None
    try:
        schema, question = validate_inputs(schema, question)
        sql = generate_sql(runtime or get_runtime(), schema, question)
        status = "ok"
        return {
            "request_id": request_id,
            "sql": sql,
            "latency_ms": round((time.perf_counter() - started) * 1_000),
            "model_variant": "qlora_r32",
        }
    except Exception as exc:
        error_category = type(exc).__name__
        raise
    finally:
        record_event(
            {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "request_id": request_id,
                "status": status,
                "error_category": error_category,
                "latency_ms": round((time.perf_counter() - started) * 1_000),
                "schema_chars": schema_chars,
                "question_chars": question_chars,
                "model_variant": "qlora_r32",
            }
        )


def generate_via_backend(
    schema: str,
    question: str,
    backend_url: str,
    *,
    timeout_seconds: int = 180,
) -> dict[str, object]:
    request_id = uuid.uuid4().hex[:12]
    started = time.perf_counter()
    schema_chars = len(schema)
    question_chars = len(question)
    status = "error"
    error_category: str | None = None
    try:
        schema, question = validate_inputs(schema, question)
        payload = json.dumps(
            {"esquema": schema, "pregunta": question, "variante": "qlora"}
        ).encode("utf-8")
        request = Request(
            f"{backend_url.rstrip('/')}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=timeout_seconds) as response:
            body = json.loads(response.read().decode("utf-8"))
        sql = validate_read_only_sql(str(body["sql"]))
        status = "ok"
        return {
            "request_id": request_id,
            "sql": sql,
            "latency_ms": round((time.perf_counter() - started) * 1_000),
            "model_variant": "qlora_r32",
            "backend_latency_ms": int(body.get("latency_ms", 0)),
        }
    except InputValidationError:
        error_category = "InputValidationError"
        raise
    except (HTTPError, URLError, TimeoutError, KeyError, TypeError, ValueError) as exc:
        error_category = type(exc).__name__
        raise BackendUnavailableError(
            "La API local no respondió con una consulta válida."
        ) from exc
    finally:
        record_event(
            {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "request_id": request_id,
                "status": status,
                "error_category": error_category,
                "latency_ms": round((time.perf_counter() - started) * 1_000),
                "schema_chars": schema_chars,
                "question_chars": question_chars,
                "model_variant": "qlora_r32",
                "transport": "local_fastapi",
            }
        )
