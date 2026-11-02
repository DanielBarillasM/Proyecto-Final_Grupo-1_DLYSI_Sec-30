from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GenerateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    esquema: str = Field(min_length=20, max_length=50_000)
    pregunta: str = Field(min_length=3, max_length=1_000)
    variante: Literal["base", "qlora"] = "qlora"

    @field_validator("esquema")
    @classmethod
    def schema_must_contain_table(cls, value: str) -> str:
        if "CREATE TABLE" not in value.upper():
            raise ValueError("El esquema debe contener al menos una sentencia CREATE TABLE")
        return value


class ExecutionPreview(BaseModel):
    ok: bool
    columnas: list[str] = Field(default_factory=list)
    filas: list[list[Any]] = Field(default_factory=list, max_length=10)
    error: str | None = None


class GenerateResponse(BaseModel):
    sql: str
    mode: Literal["fixture", "model"]
    variante: Literal["base", "qlora"]
    latency_ms: int = Field(ge=0)
    execution: ExecutionPreview | None = None
    trace: list[str] = Field(default_factory=list)


class ValidateSqlRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    sql: str = Field(min_length=1, max_length=50_000)


class ValidateSqlResponse(BaseModel):
    valid: Literal[True] = True
    sql: str
    dialect: Literal["mysql"] = "mysql"
    read_only: Literal[True] = True


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    mode: Literal["fixture", "model"]
    adapter_ready: bool
    adapter_source: Literal["local", "huggingface", "missing"]
    active_variant: Literal["base", "qlora"] | None = None
    runtime_state: Literal["idle", "busy", "ready", "error"] = "idle"
