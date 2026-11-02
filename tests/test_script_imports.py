import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_training_script_loads_as_a_direct_script() -> None:
    namespace = runpy.run_path(
        str(ROOT / "scripts" / "train_qlora.py"), run_name="training_import_check"
    )
    assert namespace["ROOT"] == ROOT


def test_validation_script_loads_as_a_direct_script() -> None:
    namespace = runpy.run_path(
        str(ROOT / "scripts" / "run_validation.py"), run_name="validation_import_check"
    )
    assert namespace["ROOT"] == ROOT
