from __future__ import annotations

import html
import os

import gradio as gr

from production import InputValidationError, generate_for_production

if os.getenv("SPACE_ID"):
    try:
        import spaces
    except ImportError:
        spaces = None
else:
    spaces = None


EXAMPLE_SCHEMA = """CREATE TABLE clientes (
  id INT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  ciudad VARCHAR(80) NOT NULL
);

CREATE TABLE pedidos (
  id INT PRIMARY KEY,
  cliente_id INT NOT NULL,
  fecha DATE NOT NULL,
  total DECIMAL(10,2) NOT NULL,
  estado VARCHAR(30) NOT NULL,
  FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);"""


def _run(schema: str, question: str) -> tuple[str, str]:
    try:
        result = generate_for_production(schema, question)
    except InputValidationError as exc:
        return "", f"⚠️ **Solicitud inválida:** {html.escape(str(exc))}"
    except Exception:
        return "", (
            "❌ **No fue posible generar la consulta.** "
            "El incidente quedó registrado sin guardar el esquema ni la pregunta."
        )
    return str(result["sql"]), (
        f"✅ **Consulta segura generada** · `{result['latency_ms']} ms` · "
        f"solicitud `{result['request_id']}` · variante `qlora_r32`"
    )


if spaces is not None:
    run_model = spaces.GPU(duration=60)(_run)
else:
    run_model = _run


CSS = """
:root { --ink: #102a2e; --teal: #0f766e; --paper: #f5f3ed; --rust: #c2552d; }
.gradio-container {
  max-width: 1180px !important;
  margin: auto !important;
  background: var(--paper);
}
.hero { border-left: 8px solid var(--teal); padding: 1.2rem 1.4rem; background: white; }
.hero h1 { color: var(--ink); margin-bottom: .35rem; }
.hero strong { color: var(--rust); }
.footer-note { color: #4b6265; font-size: .9rem; }
"""

with gr.Blocks(title="Text-to-SQL · Modelo en producción") as demo:
    gr.HTML(
        """<section class="hero">
        <p>PROYECTO FINAL · DEEP LEARNING Y SISTEMAS INTELIGENTES</p>
        <h1>Convierte preguntas en español a MySQL seguro</h1>
        <p>Qwen2.5-Coder-1.5B + <strong>QLoRA r=32</strong>. La salida se limita a
        una consulta de solo lectura y no se almacenan los datos introducidos.</p>
        </section>"""
    )
    with gr.Row():
        with gr.Column(scale=6):
            schema = gr.Code(
                label="Esquema MySQL",
                language="sql",
                value=EXAMPLE_SCHEMA,
                lines=18,
            )
            question = gr.Textbox(
                label="Pregunta",
                value="Muestra cada cliente y la suma de sus pedidos completados durante 2024.",
                lines=2,
            )
            generate = gr.Button("Generar SQL", variant="primary")
        with gr.Column(scale=5):
            output = gr.Code(label="SQL generado", language="sql", lines=15)
            status = gr.Markdown("Listo para generar una consulta.")
    gr.Examples(
        examples=[
            [EXAMPLE_SCHEMA, "Lista los nombres y las ciudades de todos los clientes."],
            [EXAMPLE_SCHEMA, "Muestra los clientes que no tienen ningún pedido."],
            [
                EXAMPLE_SCHEMA,
                "¿Qué cliente tuvo el mayor total de pedidos completados durante 2024?",
            ],
        ],
        inputs=[schema, question],
    )
    gr.Markdown(
        "<span class='footer-note'>Wilson Alejandro Calderón Argueta · "
        "Pablo Daniel Barillas Moreno · UVG, Sección 30, 2026</span>"
    )
    generate.click(run_model, inputs=[schema, question], outputs=[output, status])


if __name__ == "__main__":
    demo.queue(default_concurrency_limit=1).launch(css=CSS)
