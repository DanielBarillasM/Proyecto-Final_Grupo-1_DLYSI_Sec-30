from __future__ import annotations

import logging
import os
from json import JSONDecodeError

from fastapi import FastAPI, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware

from text2sql.sql_safety import UnsafeSQL, validate_read_only_sql

from .schemas import (
    GenerateRequest,
    GenerateResponse,
    HealthResponse,
    ValidateSqlRequest,
    ValidateSqlResponse,
)
from .service import (
    ModelBusyError,
    active_variant,
    adapter_ready,
    adapter_source,
    generate_fixture,
    generate_with_model,
    read_result_file,
    runtime_state,
    settings,
)

logger = logging.getLogger(__name__)
UNSAFE_OUTPUT_MESSAGE = (
    "El modelo no produjo una consulta de solo lectura válida. Reformula la pregunta."
)


app = FastAPI(
    title="Proyecto 3 · Text-to-SQL local",
    version="1.0.0",
    description="API local de demostración. El contrato evaluado permanece en solucion.py.",
)
origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    current = settings()
    return HealthResponse(
        mode=current.mode,
        adapter_ready=adapter_ready(),
        adapter_source=adapter_source(),
        active_variant=active_variant() if current.mode == "model" else None,
        runtime_state=runtime_state() if current.mode == "model" else "idle",
    )


@app.post("/api/generate", response_model=GenerateResponse, tags=["text-to-sql"])
async def generate(payload: GenerateRequest) -> GenerateResponse:
    current = settings()
    if current.mode == "fixture":
        return generate_fixture(payload.variante)
    try:
        return await run_in_threadpool(
            generate_with_model,
            payload.esquema,
            payload.pregunta,
            payload.variante,
        )
    except ModelBusyError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El modelo está atendiendo otra generación. "
                "Espera unos segundos e inténtalo de nuevo."
            ),
            headers={"Retry-After": "5"},
        ) from exc
    except UnsafeSQL as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=UNSAFE_OUTPUT_MESSAGE,
        ) from exc
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se encontró el adapter local. Descárgalo o selecciona Baseline.",
        ) from exc
    except (OSError, RuntimeError, ValueError) as exc:
        logger.exception("Falló la generación local")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "El modelo local no pudo cargarse o generar. "
                "Revisa memoria GPU, caché y configuración."
            ),
        ) from exc


@app.post("/api/validate-sql", response_model=ValidateSqlResponse, tags=["text-to-sql"])
async def validate_sql(payload: ValidateSqlRequest) -> ValidateSqlResponse:
    try:
        normalized = validate_read_only_sql(payload.sql)
    except UnsafeSQL as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    return ValidateSqlResponse(sql=normalized)


@app.get("/api/results/{name}", tags=["results"])
async def results(name: str) -> dict:
    try:
        return read_result_file(name)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Resultado no disponible") from exc
    except (FileNotFoundError, JSONDecodeError, OSError) as exc:
        raise HTTPException(
            status_code=503,
            detail="Los resultados versionados no están disponibles o son inválidos.",
        ) from exc
