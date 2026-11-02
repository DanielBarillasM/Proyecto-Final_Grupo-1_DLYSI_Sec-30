# Bitácora del proyecto

## 2 de noviembre de 2026 — inicio del Proyecto Final

- Se leyó el enunciado de puesta en producción y se mapearon sus siete secciones obligatorias.
- Se eligió el Proyecto 3 Text-to-SQL como modelo de origen, sin reentrenamiento inicial.
- Se migraron código, datos, resultados, notebooks, pruebas, informe y presentación desde el commit
  `df34c14c5afecddaa0d977832a56cec80c590244`.
- Se excluyeron `.git`, entornos virtuales, cachés, builds y el binario del adaptador.
- Se creó una aplicación Gradio, validación de entradas, telemetría privada y pruebas de producción.
- Se documentó que la modalidad de tríos no coincide aún con los dos integrantes del Proyecto 3.

Las siguientes entradas documentan retrospectivamente trabajo y revisiones que el equipo confirmó como realizados. Se registran el 24 de octubre de 2026 para no atribuir fechas históricas que no quedaron documentadas en su momento. Cada entrada enlaza evidencia existente en el repositorio.

## 2026-10-24 - Pablo Daniel Barillas Moreno

**Objetivo:** establecer la planificación técnica, el contrato de entrega y la primera versión de la aplicación web.

**Trabajo realizado:** organización inicial del repositorio, definición de la ruta de ejecución y construcción de la interfaz React inicial, posteriormente renovada con los componentes visuales del proyecto.

**Resultado:** estructura reproducible y aplicación inicial documentadas en `docs/PLAN_PROYECTO.md` y `web/`; evidencia en los commits `8a340e1` y `287170a`.

**Siguiente paso:** integrar la aplicación con el pipeline Text-to-SQL y su API.

## 2026-10-24 - Pablo Daniel Barillas Moreno

**Objetivo:** completar el contrato de inferencia y el pipeline principal de Texto a SQL.

**Trabajo realizado:** revisión de `solucion.py`, del prompt común, de la validación de consultas de solo lectura y de la integración con el backend.

**Resultado:** función `generar_sql` utilizable por el evaluador y módulos versionados en `text2sql/`, `solucion.py` y `backend/`; evidencia en el commit `fb18960`.

**Siguiente paso:** preparar las configuraciones QLoRA y ejecutar los experimentos comparables.

## 2026-10-24 - Pablo Daniel Barillas Moreno

**Objetivo:** trasladar y ejecutar el entrenamiento QLoRA en la GPU CUDA local.

**Trabajo realizado:** preparación de los notebooks y scripts para la RTX 4050, ejecución de las configuraciones `r=16` y `r=32`, y seguimiento de métricas y tiempos.

**Resultado:** dos corridas completas y comparables registradas en `resultados/corridas/` y `resultados/resumen.json`; evidencia del traslado local en el commit `6c80bf8`.

**Siguiente paso:** seleccionar el adapter ganador e integrarlo en la entrega.

## 2026-10-24 - Pablo Daniel Barillas Moreno

**Objetivo:** integrar el adapter ganador y confirmar la primera mitad de la muestra humana.

**Trabajo realizado:** selección de QLoRA `r=32`, integración de sus pesos, comprobación de API y web, publicación privada y revisión humana de las filas 1 a 50 de `datos/revision_muestra.csv`.

**Resultado:** adapter activado con SHA-256 `d3126183a092521cb1feffb9424b188552d27bb8fc4b51a8d13a1348d89016f1`, repositorio de respaldo registrado en `adapter/registry.json` y 50 filas confirmadas; evidencia principal en `0aa2ed4`.

**Siguiente paso:** comprobar la entrega limpia en Google Colab con GPU T4.

## 2026-10-24 - Wilson Alejandro Calderón Argueta

**Objetivo:** revisar la estructura de los esquemas y la coherencia del conjunto de entrenamiento.

**Trabajo realizado:** revisión de tablas, relaciones, claves y cobertura temática de los doce esquemas de entrenamiento, junto con los pares aceptados asociados.

**Resultado:** evidencia revisada en `datos/esquemas/train/`, `datos/entrenamiento/aceptados.jsonl` y `resultados/dataset_manifest.json`.

**Siguiente paso:** comprobar la ejecución y las condiciones de MySQL usadas para aceptar los pares.

## 2026-10-24 - Wilson Alejandro Calderón Argueta

**Objetivo:** revisar la validación de los pares en MySQL 8.4.10.

**Trabajo realizado:** comprobación del flujo de carga de esquemas, semillas y consultas, incluyendo la configuración `ONLY_FULL_GROUP_BY` y el registro de descartes.

**Resultado:** 2,592 pares de entrenamiento aceptados y referencias de validación documentadas en `scripts/validate_mysql.py`, `docker-compose.yml` y `resultados/dataset_manifest.json`.

**Siguiente paso:** revisar la evaluación propia y las categorías de error.

## 2026-10-24 - Wilson Alejandro Calderón Argueta

**Objetivo:** revisar la validación propia, el experimento de inferencia y el análisis de errores.

**Trabajo realizado:** contraste de las salidas baseline, QLoRA `r=16`, QLoRA `r=32`, generación directa y reparación guiada, además del único fallo registrado.

**Resultado:** revisión de las cinco corridas en `resultados/corridas/`, con EX ponderada de 97.4% para ambos adapters y selección de `r=32` por menor latencia p95.

**Siguiente paso:** confirmar la segunda mitad de la muestra y revisar los documentos finales.

## 2026-10-24 - Wilson Alejandro Calderón Argueta

**Objetivo:** confirmar la segunda mitad de la muestra humana y revisar los documentos de entrega.

**Trabajo realizado:** revisión humana de las filas 51 a 100 de `datos/revision_muestra.csv` y comprobación de que informe y presentación reflejaran las métricas reales.

**Resultado:** 50 filas confirmadas, informe de cinco páginas en `output/pdf/informe.pdf` y presentación de doce diapositivas en `presentacion.pdf`.

**Siguiente paso:** incorporar al repositorio la evidencia de la prueba limpia en Google Colab con GPU T4 y regenerar los documentos finales.
