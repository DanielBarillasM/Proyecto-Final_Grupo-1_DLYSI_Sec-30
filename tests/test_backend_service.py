from dataclasses import dataclass
from types import SimpleNamespace

import backend.service as service


@dataclass(frozen=True)
class FakeConfig:
    usar_adapter: bool = False


class FakeRuntime:
    created: list[bool] = []

    def __init__(self, config: FakeConfig) -> None:
        self.uses_adapter = config.usar_adapter
        self.created.append(config.usar_adapter)


def test_model_switch_keeps_only_the_selected_runtime(monkeypatch) -> None:
    service._runtime = None
    service._runtime_variant = None
    FakeRuntime.created.clear()
    monkeypatch.setattr(service, "TextToSQLRuntime", FakeRuntime)
    monkeypatch.setattr(service, "load_config", lambda: FakeConfig())
    monkeypatch.setattr(service, "adapter_ready", lambda: True)
    monkeypatch.setattr(service, "generate_sql", lambda runtime, schema, question: "SELECT 1;")

    first = service.generate_with_model("CREATE TABLE t (id INT);", "Cuenta filas", "base")
    reused = service.generate_with_model("CREATE TABLE t (id INT);", "Cuenta filas", "base")
    switched = service.generate_with_model("CREATE TABLE t (id INT);", "Cuenta filas", "qlora")

    assert first.variante == "base"
    assert "Modelo reutilizado" in reused.trace
    assert switched.variante == "qlora"
    assert service.active_variant() == "qlora"
    assert service.runtime_state() == "ready"
    assert FakeRuntime.created == [False, True]

    service._runtime = None
    service._runtime_variant = None
    service._runtime_state = "idle"


def test_model_failure_releases_runtime_for_retry(monkeypatch) -> None:
    service._runtime = None
    service._runtime_variant = None
    service._runtime_state = "idle"
    monkeypatch.setattr(service, "TextToSQLRuntime", FakeRuntime)
    monkeypatch.setattr(service, "load_config", lambda: FakeConfig())
    monkeypatch.setattr(service, "adapter_ready", lambda: True)
    monkeypatch.setattr(
        service,
        "generate_sql",
        lambda runtime, schema, question: (_ for _ in ()).throw(RuntimeError("GPU error")),
    )

    try:
        service.generate_with_model("CREATE TABLE t (id INT);", "Cuenta filas", "base")
    except RuntimeError:
        pass
    else:
        raise AssertionError("La falla simulada debía propagarse")

    assert service.active_variant() is None
    assert service.runtime_state() == "error"
    assert service._runtime is None

    service._runtime_state = "idle"


def test_adapter_source_uses_public_fallback_when_local_weights_are_missing(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setattr(
        service,
        "load_config",
        lambda: SimpleNamespace(
            adapter=tmp_path / "missing-adapter",
            adapter_repo_id="Dani0604/proyecto3-text2sql-qlora",
        ),
    )
    assert service.adapter_source() == "huggingface"
    assert service.adapter_ready() is True
