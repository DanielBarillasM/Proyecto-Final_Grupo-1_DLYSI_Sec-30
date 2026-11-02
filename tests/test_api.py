import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app
from backend.schemas import GenerateResponse


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as http:
        yield http


@pytest.mark.asyncio
async def test_health(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["mode"] == "fixture"
    assert response.json()["active_variant"] is None
    assert response.json()["runtime_state"] == "idle"
    assert response.json()["adapter_source"] in {"local", "huggingface", "missing"}


@pytest.mark.asyncio
async def test_cors_accepts_both_local_frontend_hosts(client: AsyncClient) -> None:
    for origin in ("http://localhost:3000", "http://127.0.0.1:3000"):
        response = await client.options(
            "/api/generate",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == origin


@pytest.mark.asyncio
async def test_fixture_generation_is_honest_and_bounded(client: AsyncClient) -> None:
    response = await client.post(
        "/api/generate",
        json={
            "esquema": "CREATE TABLE customers (customer_id INT PRIMARY KEY);",
            "pregunta": "¿Qué ciudad generó más ingresos?",
            "variante": "base",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "fixture"
    assert payload["variante"] == "base"
    assert "clientes" in payload["sql"]
    assert payload["sql"].startswith("SELECT")
    assert len(payload["execution"]["filas"]) <= 10


@pytest.mark.asyncio
async def test_validate_sql_accepts_read_only_mysql(client: AsyncClient) -> None:
    response = await client.post(
        "/api/validate-sql",
        json={"sql": "SELECT nombre FROM clientes WHERE ciudad = 'Guatemala'"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "valid": True,
        "sql": "SELECT nombre FROM clientes WHERE ciudad = 'Guatemala';",
        "dialect": "mysql",
        "read_only": True,
    }


@pytest.mark.asyncio
async def test_validate_sql_rejects_writes_and_invalid_syntax(client: AsyncClient) -> None:
    for sql in ("DELETE FROM clientes;", "SELECT FROM clientes;"):
        response = await client.post("/api/validate-sql", json={"sql": sql})
        assert response.status_code == 422
        assert response.json()["detail"]


@pytest.mark.asyncio
async def test_model_mode_reports_missing_adapter(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEXT_TO_SQL_MODE", "model")
    monkeypatch.setattr("backend.service.adapter_ready", lambda: False)
    response = await client.post(
        "/api/generate",
        json={
            "esquema": "CREATE TABLE clientes (id INT PRIMARY KEY);",
            "pregunta": "¿Cuántos clientes existen?",
            "variante": "qlora",
        },
    )
    assert response.status_code == 503
    assert "adapter" in response.json()["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.parametrize("variant", ["base", "qlora"])
async def test_model_mode_forwards_selected_variant(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    variant: str,
) -> None:
    monkeypatch.setenv("TEXT_TO_SQL_MODE", "model")

    def fake_generate(esquema: str, pregunta: str, selected: str) -> GenerateResponse:
        assert "CREATE TABLE" in esquema
        assert pregunta
        assert selected == variant
        return GenerateResponse(
            sql="SELECT 1;",
            mode="model",
            variante=selected,
            latency_ms=1,
            trace=[f"Variante activa: {selected}"],
        )

    monkeypatch.setattr("backend.main.generate_with_model", fake_generate)
    response = await client.post(
        "/api/generate",
        json={
            "esquema": "CREATE TABLE clientes (id INT PRIMARY KEY);",
            "pregunta": "¿Cuántos clientes existen?",
            "variante": variant,
        },
    )
    assert response.status_code == 200
    assert response.json()["variante"] == variant


@pytest.mark.asyncio
async def test_model_mode_reports_busy_runtime(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from backend.service import ModelBusyError

    monkeypatch.setenv("TEXT_TO_SQL_MODE", "model")
    monkeypatch.setattr(
        "backend.main.generate_with_model",
        lambda *args: (_ for _ in ()).throw(ModelBusyError("busy")),
    )
    response = await client.post(
        "/api/generate",
        json={
            "esquema": "CREATE TABLE clientes (id INT PRIMARY KEY);",
            "pregunta": "¿Cuántos clientes existen?",
            "variante": "base",
        },
    )
    assert response.status_code == 409
    assert response.headers["retry-after"] == "5"
