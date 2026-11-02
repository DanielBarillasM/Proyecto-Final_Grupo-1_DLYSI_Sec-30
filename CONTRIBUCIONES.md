# Contribuciones

## Proyecto Final — asignación provisional

| Área | Responsable principal | Revisor | Evidencia prevista |
|---|---|---|---|
| Procedencia de datos, hashes y modelo | Wilson Alejandro Calderón Argueta | Pablo Daniel Barillas Moreno | `docs/PROCEDENCIA.md`, manifiestos y pruebas |
| Runtime, interfaz Gradio y despliegue | Pablo Daniel Barillas Moreno | Wilson Alejandro Calderón Argueta | `production.py`, `app.py`, bundle del Space |
| Seguridad y telemetría | Ambos | Ambos | `text2sql/sql_safety.py`, logs anonimizados y pruebas |
| README y arquitectura | Ambos | Ambos | `README.md`, `docs/ARQUITECTURA.md` |
| Evidencias, presentación y preguntas | Ambos | Ambos | `docs/evidencias/`, `presentacion/`, PDF final |

Esta asignación conserva los responsables del Proyecto 3 y debe actualizarse con evidencia real.
El enunciado indica modalidad de tríos; no se añadirá un tercer integrante ni se le atribuirá trabajo
hasta que el equipo confirme su identidad y participación.

## Proyecto 3 — evidencia heredada

Esta tabla representa la asignación actual. La columna de evidencia debe completarse únicamente con archivos, pull requests, commits o resultados reales.

| Tarea | Responsable principal | Revisor | Estado | Evidencia |
|---|---|---|---|---|
| Diseño y validación de esquemas de entrenamiento | Wilson Alejandro Calderón Argueta | Pablo Daniel Barillas Moreno | Implementado y revisado por el equipo | `scripts/generate_data_assets.py`, `datos/esquemas/`, `BITACORA.md` |
| Conversión, traducción y ejecución de pares en MySQL | Wilson Alejandro Calderón Argueta | Pablo Daniel Barillas Moreno | Implementado y revisado por el equipo | `scripts/validate_mysql.py`, `resultados/dataset_manifest.json`, `BITACORA.md` |
| Baseline y prompt común | Pablo Daniel Barillas Moreno | Wilson Alejandro Calderón Argueta | Implementado, medido y revisado | `text2sql/`, `solucion.py`, `resultados/corridas/baseline.json` |
| Entrenamiento QLoRA A y B | Pablo Daniel Barillas Moreno | Wilson Alejandro Calderón Argueta | Corridas locales completas, revisadas y documentadas | `resultados/resumen.json`, `resultados/corridas/`, `adapter/selection.json` |
| Validación propia de 40 preguntas | Ambos | Ambos | Referencias y cinco corridas de predicción completas | `datos/validacion/preguntas.jsonl`, `resultados/corridas/` |
| Experimento de inferencia y análisis de errores | Ambos | Ambos | Directo/reparación completos; un fallo de entidad inexistente | `resultados/corridas/ganador_direct.json`, `resultados/corridas/ganador_repair.json` |
| Aplicación React | Pablo Daniel Barillas Moreno | Wilson Alejandro Calderón Argueta | Integrada con FastAPI y adapter real; revisión del equipo confirmada | `web/`, `backend/`, build de producción |
| Informe y presentación | Ambos | Ambos | Métricas reales incorporadas y PDFs revisados por el equipo | `informe/main.tex`, `output/pdf/informe.pdf`, `presentacion.pdf`, `BITACORA.md` |
| Compatibilidad final en Colab/T4 | Ambos | Ambos | Prueba limpia completada y documentada | `notebooks/04_prueba_integral_colab_t4.ipynb`, `README.md` |

## Evidencia aceptable

- Hash o enlace a un commit con cambios sustantivos.
- Pull request revisado por la otra persona.
- Ruta a notebook, script, dataset, adapter, tabla, figura o sección escrita.
- Registro de ejecución que permita reproducir el resultado.
- Log de entrenamiento con configuración, hardware, métricas y checksum.

La autoría debe actualizarse si el reparto real cambia; la evidencia prevalece sobre esta planificación. Los commits vacíos no sustituyen trabajo demostrable.
