from pathlib import Path

from scripts import build_space_bundle


def test_space_bundle_contains_runtime_without_weights(tmp_path: Path) -> None:
    output = tmp_path / "space"
    result = build_space_bundle.build_bundle(output, allow_outside_dist=True)

    assert (result / "app.py").is_file()
    assert (result / "production.py").is_file()
    assert (result / "text2sql/runtime.py").is_file()
    assert not tuple(result.rglob("*.safetensors"))
    requirements = (result / "requirements.txt").read_text(encoding="utf-8")
    assert "gradio>=6,<7" in requirements
    assert "-r requirements.txt" not in requirements
