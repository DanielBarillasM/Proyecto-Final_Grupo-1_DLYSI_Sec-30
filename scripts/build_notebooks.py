from __future__ import annotations

from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook


ROOT = Path(__file__).resolve().parents[1]


SETUP = """from pathlib import Path
import json
import os
import subprocess
import sys

ROOT = Path.cwd()
if ROOT.name == "notebooks":
    ROOT = ROOT.parent
assert (ROOT / "config.json").exists(), "Ejecuta el notebook desde la raíz o notebooks/."
ARTIFACTS = Path(os.environ.get("PROJECT3_ARTIFACTS", ROOT.parent / "artifacts_locales"))
SEED = 2026
print({"root": str(ROOT), "artifacts": str(ARTIFACTS), "seed": SEED})"""


def save(name: str, cells: list) -> None:
    notebook = new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.11"},
        },
    )
    nbformat.write(notebook, ROOT / "notebooks" / name)


def data_notebook() -> list:
    return [
        new_markdown_cell(
            "# Preparación y validación de datos\n\n"
            "Proyecto 3 · Deep Learning y Sistemas Inteligentes · Sección 30"
        ),
        new_markdown_cell(
            "## Objetivo y criterio de éxito\n\n"
            "Construir al menos 2,000 pares sobre 10 o más esquemas propios, separar la validación por esquema y aceptar únicamente consultas ejecutables en MySQL 8.4.10."
        ),
        new_code_cell(SETUP),
        new_markdown_cell(
            "## 1. Reconstrucción opcional\n\n"
            "La entrega conserva los datos y manifiestos ya validados. Active estas banderas únicamente para reconstruirlos con Docker disponible."
        ),
        new_code_cell(
            "RUN_DATA_BUILD = False\n"
            "RUN_MYSQL_VALIDATION = False\n\n"
            "if RUN_DATA_BUILD:\n"
            "    subprocess.run([sys.executable, str(ROOT / 'scripts/generate_data_assets.py')], check=True)\n"
            "else:\n"
            "    print('Se usan los datos versionados; no se regeneraron archivos.')\n\n"
            "if RUN_MYSQL_VALIDATION:\n"
            "    subprocess.run([sys.executable, str(ROOT / 'scripts/validate_mysql.py')], check=True)\n"
            "else:\n"
            "    print('Se usa el manifiesto MySQL versionado; no se requiere Docker para leer este notebook.')"
        ),
        new_markdown_cell("## 2. Volumen, motor y separación por esquema"),
        new_code_cell(
            "manifest = json.loads((ROOT / 'resultados/dataset_manifest.json').read_text(encoding='utf-8'))\n"
            "assert manifest['training_accepted'] >= 2000\n"
            "assert manifest['training_schemas'] >= 10\n"
            "assert manifest['validation_examples'] == 40\n"
            "assert manifest['validation_schemas'] == 2\n"
            "assert manifest['mysql_version'] == '8.4.10'\n"
            "assert manifest['difficulty_validation'] == {'facil': 14, 'media': 14, 'dificil': 12}\n"
            "{key: manifest[key] for key in ('training_candidates', 'training_accepted', 'training_discarded', 'training_schemas', 'validation_examples', 'validation_schemas', 'mysql_version', 'sql_mode')}"
        ),
        new_markdown_cell("## 3. Revisión humana"),
        new_code_cell(
            "import pandas as pd\n\n"
            "review = pd.read_csv(ROOT / 'datos/revision_muestra.csv')\n"
            "assert len(review) == 100\n"
            "assert review['revisor'].notna().all()\n"
            "assert manifest['human_review_complete'] is True\n"
            "review.groupby(['revisor', 'decision']).size().rename('filas').reset_index()"
        ),
        new_markdown_cell(
            "## Resultado\n\n"
            "El dataset quedó congelado con 2,592 pares aceptados, 0 descartes, 12 esquemas de entrenamiento, 2 esquemas inéditos y 100 filas confirmadas por revisión humana."
        ),
    ]


def training_notebook() -> list:
    return [
        new_markdown_cell(
            "# Entrenamiento QLoRA controlado\n\n"
            "Proyecto 3 · Deep Learning y Sistemas Inteligentes · Sección 30"
        ),
        new_markdown_cell(
            "## Hipótesis registradas antes de entrenar\n\n"
            "QLoRA `r=16` debía reducir el costo manteniendo capacidad suficiente. QLoRA `r=32` podía mejorar la composición de consultas medias y difíciles, a cambio de más parámetros y tiempo. La ganancia podía ser nula si la calidad de los datos era el límite."
        ),
        new_code_cell(SETUP),
        new_markdown_cell("## 1. Hardware disponible para reproducir"),
        new_code_cell(
            "import torch\n\n"
            "hardware = {'cuda': torch.cuda.is_available()}\n"
            "if torch.cuda.is_available():\n"
            "    properties = torch.cuda.get_device_properties(0)\n"
            "    hardware.update({'gpu': torch.cuda.get_device_name(0), 'vram_gib': round(properties.total_memory / 1024**3, 2)})\n"
            "hardware"
        ),
        new_markdown_cell("## 2. Comparación controlada"),
        new_code_cell(
            "a = json.loads((ROOT / 'configuraciones/qlora_r16.json').read_text(encoding='utf-8'))\n"
            "b = json.loads((ROOT / 'configuraciones/qlora_r32.json').read_text(encoding='utf-8'))\n"
            "differences = {key: (a.get(key), b.get(key)) for key in sorted(a | b) if a.get(key) != b.get(key)}\n"
            "assert set(differences) <= {'nombre', 'r'}\n"
            "differences"
        ),
        new_markdown_cell(
            "## 3. Entrenamiento opcional\n\n"
            "Las corridas reales ya finalizaron. La bandera evita reentrenar al ejecutar este notebook como evidencia."
        ),
        new_code_cell(
            "RUN_FULL_TRAINING = False\n"
            "if RUN_FULL_TRAINING:\n"
            "    for name in ('qlora_r16', 'qlora_r32'):\n"
            "        output = ARTIFACTS / 'runs' / name\n"
            "        subprocess.run([sys.executable, str(ROOT / 'scripts/train_qlora.py'), '--config', str(ROOT / f'configuraciones/{name}.json'), '--output', str(output)], check=True)\n"
            "else:\n"
            "    print('No se reentrenó: se muestran los resultados y curvas versionados.')"
        ),
        new_markdown_cell("## 4. Parámetros, tiempo y selección"),
        new_code_cell(
            "import pandas as pd\n\n"
            "summary = json.loads((ROOT / 'resultados/resumen.json').read_text(encoding='utf-8'))\n"
            "pd.DataFrame([\n"
            "    {'corrida': name, **summary['experiments'][name]}\n"
            "    for name in ('qlora_r16', 'qlora_r32')\n"
            "])[['corrida', 'trainable_parameters', 'training_minutes', 'weighted_ex', 'executable_rate', 'latency_p95_ms']]"
        ),
        new_markdown_cell("## 5. Curvas reales de loss"),
        new_code_cell(
            "from IPython.display import Image, display\n\n"
            "curves = pd.read_csv(ROOT / 'resultados/curvas_loss.csv')\n"
            "metadata = json.loads((ROOT / 'resultados/curvas_loss.json').read_text(encoding='utf-8'))\n"
            "assert set(curves['run']) == {'qlora_r16', 'qlora_r32'}\n"
            "assert set(curves['series']) == {'train', 'validation'}\n"
            "display(Image(filename=str(ROOT / 'resultados/curvas_loss.png')))\n"
            "metadata"
        ),
        new_markdown_cell(
            "## Resultado\n\n"
            "`r=16` entrenó 18,464,768 parámetros durante 120.7 minutos. `r=32` entrenó 36,929,536 durante 133.4 minutos. Ambas corridas alcanzaron 97.4% de EX; `r=32` ganó por menor latencia p95."
        ),
    ]


def evaluation_notebook() -> list:
    return [
        new_markdown_cell(
            "# Evaluación por ejecución y análisis de errores\n\n"
            "Proyecto 3 · Deep Learning y Sistemas Inteligentes · Sección 30"
        ),
        new_markdown_cell(
            "## Objetivo\n\n"
            "Comparar baseline, QLoRA `r=16`, QLoRA `r=32` y el experimento de reparación sobre los mismos 2 esquemas inéditos y 40 ejemplos."
        ),
        new_code_cell(SETUP),
        new_markdown_cell(
            "## 1. Evaluación opcional\n\n"
            "Las cinco corridas ya están versionadas. Active la bandera solo si desea repetir inferencia completa con los adapters locales."
        ),
        new_code_cell(
            "RUN_EVALUATION = False\n"
            "if RUN_EVALUATION:\n"
            "    raise RuntimeError('Use scripts/run_validation.py con las rutas de adapters descritas en README.md.')\n"
            "print('Se usan las predicciones CSV/JSON versionadas; no se repitió inferencia.')"
        ),
        new_markdown_cell("## 2. Comparación de corridas"),
        new_code_cell(
            "import pandas as pd\n\n"
            "run_names = ('baseline', 'qlora_r16', 'qlora_r32', 'ganador_direct', 'ganador_repair')\n"
            "runs = {name: json.loads((ROOT / f'resultados/corridas/{name}.json').read_text(encoding='utf-8')) for name in run_names}\n"
            "pd.DataFrame([\n"
            "    {'corrida': name, 'EX ponderada': runs[name]['weighted_ex'], 'ejecutable': runs[name]['executable_rate'], 'p50 ms': runs[name]['latency_p50_ms'], 'p95 ms': runs[name]['latency_p95_ms']}\n"
            "    for name in run_names\n"
            "])"
        ),
        new_markdown_cell("## 3. Error del ganador y efecto de reparación"),
        new_code_cell(
            "direct = runs['ganador_direct']\n"
            "repair = runs['ganador_repair']\n"
            "{\n"
            "    'EX_directa': direct['weighted_ex'],\n"
            "    'EX_reparacion': repair['weighted_ex'],\n"
            "    'delta_EX_pp': round(100 * (repair['weighted_ex'] - direct['weighted_ex']), 1),\n"
            "    'errores_directos': {k: v for k, v in direct['error_counts'].items() if k != 'correcto'},\n"
            "}"
        ),
        new_markdown_cell("## 4. Predicción de la evaluación oculta"),
        new_code_cell(
            "summary = json.loads((ROOT / 'resultados/resumen.json').read_text(encoding='utf-8'))\n"
            "{\n"
            "    'adapter': summary['selected_adapter'],\n"
            "    'EX_oculta_estimada': summary['hidden_ex_prediction'],\n"
            "    'intervalo_estimado': summary['hidden_ex_prediction_interval'],\n"
            "    'metodo': summary['hidden_ex_prediction_method'],\n"
            "}"
        ),
        new_markdown_cell(
            "## Resultado\n\n"
            "El baseline obtuvo 3.8% de EX. Ambos adapters obtuvieron 97.4% (39/40). `r=32` ganó por menor p95. La reparación mantuvo la EX y añadió latencia; el único fallo del ganador fue una entidad inexistente."
        ),
    ]


def main() -> None:
    save("01_datos.ipynb", data_notebook())
    save("02_entrenamiento.ipynb", training_notebook())
    save("03_evaluacion.ipynb", evaluation_notebook())
    print("Notebooks 01-03 reconstruidos con rutas de lectura y reproducción opcional.")


if __name__ == "__main__":
    main()
