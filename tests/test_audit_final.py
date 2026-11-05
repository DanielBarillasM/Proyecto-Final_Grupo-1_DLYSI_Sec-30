from pathlib import Path

from scripts.audit_final import collect_checks

ROOT = Path(__file__).resolve().parents[1]


def test_preparation_artifacts_are_complete() -> None:
    checks = collect_checks(ROOT)
    assert checks["required_files_present"]
    assert checks["readme_has_seven_sections"]
    assert checks["readme_declares_ai_use"]
    assert checks["dataset_is_frozen"]
    assert checks["adapter_is_pinned"]
    assert checks["adapter_is_enabled"]
    assert checks["presentation_is_pdf"]


def test_public_evidence_remains_pending_until_real_deployment() -> None:
    checks = collect_checks(ROOT)
    assert not checks["deployment_recorded"]
    assert not checks["screenshots_recorded"]
    assert checks["logs_recorded"]
    assert checks["smoke_tests_recorded"]


def test_handoff_package_is_ready() -> None:
    checks = collect_checks(ROOT)
    assert checks["handoff_ready"]
    assert checks["demo_scripts_ready"]
