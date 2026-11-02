from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "resultados" / "corridas"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verifica que los documentos reflejen las métricas y recompila sus PDF."
    )
    parser.add_argument("--artifacts-root", required=True, type=Path)
    return parser.parse_args()


def assert_documented_metrics() -> None:
    summary = load(ROOT / "resultados" / "resumen.json")
    baseline = load(RUNS / "baseline.json")
    winner = load(RUNS / "ganador_direct.json")
    winner_label = "r=16" if summary["selected_adapter"] == "qlora_r16" else "r=32"

    report = (ROOT / "informe" / "main.tex").read_text(encoding="utf-8")
    slides = (ROOT / "presentacion" / "index.html").read_text(encoding="utf-8")
    expected = {
        "baseline": pct(baseline["weighted_ex"]),
        "winner": pct(winner["weighted_ex"]),
        "winner_label": winner_label,
        "hidden": pct(summary["hidden_ex_prediction"]),
    }
    missing: list[str] = []
    for name, value in expected.items():
        report_value = value.replace("%", r"\%") if "%" in value else value
        if report_value not in report:
            missing.append(f"informe:{name}={report_value}")
        if value not in slides:
            missing.append(f"presentación:{name}={value}")
    if missing:
        raise RuntimeError(
            "Los documentos no reflejan las métricas actuales: " + ", ".join(missing)
        )


def compile_documents(artifacts_root: Path) -> None:
    logs = artifacts_root / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    log_path = logs / "document_update.log"

    latex = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-jobname=informe",
        "-output-directory=output\\pdf",
        "informe\\main.tex",
    ]
    edge = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
    if not edge.is_file():
        raise FileNotFoundError(f"No se encontró Microsoft Edge en {edge}")

    profile = artifacts_root / "edge-document-profile"
    profile.mkdir(parents=True, exist_ok=True)
    presentation = ROOT / "presentacion" / "index.html"

    with log_path.open("wb") as log:
        subprocess.run(latex, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
        subprocess.run(latex, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
        subprocess.run(
            [
                str(edge),
                "--headless=new",
                "--disable-gpu",
                "--no-pdf-header-footer",
                f"--user-data-dir={profile}",
                f"--print-to-pdf={ROOT / 'presentacion.pdf'}",
                presentation.resolve().as_uri(),
            ],
            cwd=ROOT,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )


def validate_outputs() -> None:
    expected = (
        (ROOT / "output" / "pdf" / "informe.pdf", 7),
        (ROOT / "presentacion.pdf", 12),
    )
    for pdf_path, pages in expected:
        if not pdf_path.is_file():
            raise RuntimeError(f"No se generó {pdf_path}")
        actual_pages = len(PdfReader(pdf_path).pages)
        if actual_pages != pages:
            raise RuntimeError(
                f"PDF con páginas inesperadas: {pdf_path} ({actual_pages}, esperadas {pages})"
            )


def main() -> None:
    args = parse_args()
    assert_documented_metrics()
    compile_documents(args.artifacts_root.resolve())
    validate_outputs()
    print("Documentos verificados y recompilados: informe 7 páginas; presentación 12.")


if __name__ == "__main__":
    main()
