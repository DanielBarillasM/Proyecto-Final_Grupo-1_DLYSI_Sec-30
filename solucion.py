from __future__ import annotations

import threading

from text2sql.config import load_config
from text2sql.inference import Executor, generate_sql
from text2sql.runtime import TextToSQLRuntime

_runtime: TextToSQLRuntime | None = None
_runtime_lock = threading.Lock()


def _get_runtime() -> TextToSQLRuntime:
    global _runtime
    if _runtime is None:
        with _runtime_lock:
            if _runtime is None:
                _runtime = TextToSQLRuntime(load_config())
    return _runtime


def generar_sql(esquema: str, pregunta: str, ejecutar: Executor | None = None) -> str:
    """Genera una única consulta MySQL SELECT o WITH ... SELECT.

    Si se proporciona ``ejecutar``, se utiliza como máximo dos veces: una para el
    primer candidato y otra para verificar una única reparación ante error SQL.
    """
    if not esquema.strip() or not pregunta.strip():
        raise ValueError("esquema y pregunta no pueden estar vacíos")

    return generate_sql(_get_runtime(), esquema, pregunta, ejecutar)
