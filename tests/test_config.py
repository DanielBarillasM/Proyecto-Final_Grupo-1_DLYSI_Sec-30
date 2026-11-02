from pathlib import Path

from text2sql.config import load_config


def test_config_has_allowed_model() -> None:
    config = load_config()
    assert config.modelo_base == "Qwen/Qwen2.5-Coder-1.5B-Instruct"
    assert config.modelo_revision == "2e1fd397ee46e1388853d2af2c993145b0f1098a"
    assert config.semilla == 2026
    assert config.adapter == (Path.cwd() / "adapter").resolve()
    assert config.adapter_repo_id == "Dani0604/proyecto3-text2sql-qlora"
    assert config.adapter_revision == "24658a4efce8303165906832f0eede2b5c56de84"
