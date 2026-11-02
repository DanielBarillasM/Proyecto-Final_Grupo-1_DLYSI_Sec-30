from __future__ import annotations

import gc
import os
import threading
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Literal

from text2sql.config import load_config
from text2sql.inference import generate_sql
from text2sql.runtime import TextToSQLRuntime

from .schemas import ExecutionPreview, GenerateResponse

ROOT = Path(__file__).resolve().parents[1]
_runtime: TextToSQLRuntime | None = None
_runtime_variant: Literal["base", "qlora"] | None = None
_runtime_state: Literal["idle", "busy", "ready", "error"] = "idle"
_runtime_lock = threading.Lock()


class ModelBusyError(RuntimeError):
    """Ya hay una generación usando el único runtime de GPU."""


FIXTURE_SQL = """SELECT c.nombre,
       ROUND(SUM(p.total), 2) AS total_completado
FROM clientes AS c
JOIN pedidos AS p ON p.cliente_id = c.id
WHERE p.estado = 'completado'
  AND p.fecha >= '2024-01-01'
  AND p.fecha < '2025-01-01'
GROUP BY c.id, c.nombre
ORDER BY total_completado DESC
LIMIT 1;"""


@dataclass(frozen=True, slots=True)
class ServiceSettings:
    mode: Literal["fixture", "model"]


def settings() -> ServiceSettings:
    requested = os.getenv("TEXT_TO_SQL_MODE", "fixture").strip().lower()
    return ServiceSettings(mode="model" if requested == "model" else "fixture")


def adapter_ready() -> bool:
    return adapter_source() != "missing"


def adapter_source() -> Literal["local", "huggingface", "missing"]:
    try:
        config_value = load_config()
        adapter = config_value.adapter
        config = adapter / "adapter_config.json"
        weights = tuple(adapter.glob("adapter_model.*"))
        local_ready = (
            config.is_file()
            and config.stat().st_size > 0
            and any(path.is_file() and path.stat().st_size > 0 for path in weights)
        )
        if local_ready:
            return "local"
        return "huggingface" if config_value.adapter_repo_id else "missing"
    except (OSError, ValueError):
        return "missing"


def active_variant() -> Literal["base", "qlora"] | None:
    return _runtime_variant


def runtime_state() -> Literal["idle", "busy", "ready", "error"]:
    return _runtime_state


def _release_runtime() -> None:
    global _runtime, _runtime_variant
    _runtime = None
    _runtime_variant = None
    gc.collect()
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except (ImportError, RuntimeError):
        pass


def generate_fixture(variant: Literal["base", "qlora"]) -> GenerateResponse:
    return GenerateResponse(
        sql=FIXTURE_SQL,
        mode="fixture",
        variante=variant,
        latency_ms=0,
        execution=ExecutionPreview(
            ok=True,
            columnas=["nombre", "total_completado"],
            filas=[["Ana López", "42890.50"]],
        ),
        trace=[
            f"Fixture local seleccionado ({variant})",
            "Consulta marcada explícitamente como demostración",
            "Sin llamada a modelo ni servicio externo",
        ],
    )


def generate_with_model(
    esquema: str,
    pregunta: str,
    variant: Literal["base", "qlora"],
) -> GenerateResponse:
    global _runtime, _runtime_state, _runtime_variant
    if variant == "qlora" and not adapter_ready():
        raise FileNotFoundError("No hay un adapter seleccionado en adapter/")
    if not _runtime_lock.acquire(blocking=False):
        raise ModelBusyError("Ya hay una generación en curso")
    try:
        _runtime_state = "busy"
        switched = _runtime is None or _runtime_variant != variant
        if switched:
            _release_runtime()
            _runtime = TextToSQLRuntime(replace(load_config(), usar_adapter=variant == "qlora"))
            _runtime_variant = variant
        if _runtime is None:
            raise RuntimeError("No se pudo inicializar el runtime del modelo")
        started = time.perf_counter()
        sql = generate_sql(_runtime, esquema, pregunta)
        elapsed_ms = round((time.perf_counter() - started) * 1000)
        _runtime_state = "ready"
    except (OSError, RuntimeError):
        _release_runtime()
        _runtime_state = "error"
        raise
    except ValueError:
        _runtime_state = "ready" if _runtime is not None else "error"
        raise
    except Exception:
        _runtime_state = "error"
        raise
    finally:
        _runtime_lock.release()
    return GenerateResponse(
        sql=sql,
        mode="model",
        variante=variant,
        latency_ms=elapsed_ms,
        execution=None,
        trace=[
            f"Variante activa: {variant}",
            "Modelo cambiado y cargado" if switched else "Modelo reutilizado",
            "Generación determinista",
            "Guardia SQL aplicada",
        ],
    )


def read_result_file(name: str) -> dict[str, Any]:
    import json

    allowed = {"summary": "resumen.json", "dataset": "dataset_manifest.json"}
    filename = allowed.get(name)
    if filename is None:
        raise KeyError(name)
    path = ROOT / "resultados" / filename
    return json.loads(path.read_text(encoding="utf-8"))
