---
base_model: Qwen/Qwen2.5-Coder-1.5B-Instruct
library_name: peft
license: mit
language:
  - es
tags:
  - text-to-sql
  - qlora
  - mysql
  - spanish
---

# Adapter QLoRA Text-to-SQL — Grupo 1

Adapter ganador del Proyecto 3 de Deep Learning y Sistemas Inteligentes, sección 30, Universidad del Valle de Guatemala.

## Modelo y configuración

- Base: `Qwen/Qwen2.5-Coder-1.5B-Instruct`.
- Método: QLoRA, rango 32, alpha 32 y dropout 0.05.
- Entrenamiento: NF4 de 4 bits, cómputo FP16 y semilla 2026.
- Parámetros entrenables: 36,929,536.
- Tiempo: 133.4 minutos en una RTX 4050 Laptop de 6 GB.

El modelo base no está incluido. Transformers lo descarga por separado y PEFT aplica este adapter.

## Datos y resultados

Se entrenó con 2,592 pares auditables sobre 12 esquemas propios, ejecutados en MySQL 8.4.10. La validación usa 40 preguntas sobre dos esquemas inéditos.

| Variante | EX ponderada | SQL ejecutable | Latencia p95 |
|---|---:|---:|---:|
| Modelo base | 3.8% | 62.5% | 6.66 s |
| QLoRA r=16 | 97.4% | 97.5% | 15.72 s |
| QLoRA r=32 | 97.4% | 97.5% | 13.20 s |

R16 y R32 empataron en EX y ejecutabilidad. Se eligió R32 por menor latencia p95. La reparación guiada no cambió la EX y añadió latencia.

## Integridad y revisión publicada

- Archivo: `adapter_model.safetensors`.
- SHA-256: `d3126183a092521cb1feffb9424b188552d27bb8fc4b51a8d13a1348d89016f1`.
- Revisión de Hugging Face: `24658a4efce8303165906832f0eede2b5c56de84`.
- Repositorio público: `Dani0604/proyecto3-text2sql-qlora`.

## Uso

Desde la raíz del proyecto, `config.json` debe contener `"usar_adapter": true`:

```python
from solucion import generar_sql

sql = generar_sql(esquema, pregunta)
```

La generación es determinista, local y restringida a una única consulta `SELECT` o `WITH ... SELECT`.

El adapter se puede recuperar anónimamente desde Hugging Face, sin token:

```powershell
.\.venv\Scripts\hf.exe download Dani0604/proyecto3-text2sql-qlora `
  --revision 24658a4efce8303165906832f0eede2b5c56de84 `
  --local-dir adapter
```

## Compatibilidad y limitaciones

La prueba limpia en Google Colab con Tesla T4 aprobó instalación, carga, determinismo, callback, baseline y restauración del adapter. El adapter cargó en 42.728 s y usó 1.438 GB de VRAM asignada; la evidencia completa está en `notebooks/04_prueba_integral_colab_t4.ipynb`.

- La validación propia solo contiene dos esquemas inéditos y no equivale a la evaluación oculta.
- Identificadores abreviados, mezcla de idiomas y dominios muy distintos pueden reducir la EX.
- Un caso de validación falló por una entidad inexistente.

## Autores y asistencia

Wilson Alejandro Calderón Argueta y Pablo Daniel Barillas Moreno. OpenAI Codex se utilizó como asistencia para implementación, documentación y verificación; no participa como API externa durante la generación SQL evaluada.
