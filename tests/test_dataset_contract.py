import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_dataset_volume_split_and_hashes() -> None:
    manifest = json.loads((ROOT / "resultados/dataset_manifest.json").read_text(encoding="utf-8"))
    training = ROOT / "datos/entrenamiento/aceptados.jsonl"
    validation = ROOT / "datos/validacion/preguntas.jsonl"
    train_rows = [json.loads(line) for line in training.read_text(encoding="utf-8").splitlines()]
    val_rows = [json.loads(line) for line in validation.read_text(encoding="utf-8").splitlines()]
    train_schemas = {row["schema_id"] for row in train_rows}
    val_schemas = {row["schema_id"] for row in val_rows}
    assert len(train_rows) == manifest["training_accepted"] >= 2_000
    assert len(train_schemas) == manifest["training_schemas"] >= 10
    assert len(val_rows) == manifest["validation_examples"] == 40
    assert len(val_schemas) == manifest["validation_schemas"] >= 2
    assert train_schemas.isdisjoint(val_schemas)
    assert sha256(training) == manifest["accepted_sha256"]
    assert sha256(validation) == manifest["validation_sha256"]


def test_every_validated_query_executed_successfully() -> None:
    validation = ROOT / "datos/validacion/preguntas.jsonl"
    rows = [json.loads(line) for line in validation.read_text(encoding="utf-8").splitlines()]
    assert all(row["validado_mysql"] is True for row in rows)
