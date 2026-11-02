# Procedencia de datos, modelo y artefactos

## Proyecto de origen

- Repositorio: `Proyecto-3_Grupo-1_DLYSI_Sec-30`.
- Commit congelado: `df34c14c5afecddaa0d977832a56cec80c590244`.
- Fecha de la última revisión integral: 25 de octubre de 2026.
- Integrantes registrados: Wilson Alejandro Calderón Argueta y Pablo Daniel Barillas Moreno.

La migración excluye `.git`, entornos virtuales, cachés, builds y archivos temporales. Los
documentos originales relevantes se conservan con el sufijo `PROYECTO_3`.

## Dataset congelado

| Campo | Valor |
|---|---:|
| Pares de entrenamiento | 2,592 |
| Esquemas de entrenamiento | 12 |
| Preguntas de validación | 40 |
| Esquemas inéditos de validación | 2 |
| Descartes | 0 |
| MySQL | 8.4.10 |
| SHA-256 de entrenamiento | `9e28bcd7079dd7b2d41ca305b5f792055e78f3ecfdba455be1981295100049a8` |
| SHA-256 de validación | `e1af4f01758e094568aa22735b493066975346e9e6a087a90921692e19a472a9` |
| SHA-256 de aceptados | `4ec6463b6018b58d22cc54f8327bc472712b3c4ff2378e1f9ceb15486d1e2612` |

Los valores provienen de `resultados/dataset_manifest.json`. El Proyecto Final no modifica las
filas experimentales; cualquier cambio futuro exige regenerar hashes y explicar la razón.

## Modelo y adaptador

| Artefacto | Revisión o hash |
|---|---|
| Modelo base | `Qwen/Qwen2.5-Coder-1.5B-Instruct` |
| Revisión base | `2e1fd397ee46e1388853d2af2c993145b0f1098a` |
| Adaptador | `Dani0604/proyecto3-text2sql-qlora` |
| Revisión del adaptador | `24658a4efce8303165906832f0eede2b5c56de84` |
| SHA-256 de pesos | `d3126183a092521cb1feffb9424b188552d27bb8fc4b51a8d13a1348d89016f1` |

El binario `adapter_model.safetensors` mide aproximadamente 140.9 MB. No se duplica en GitHub;
el runtime lo descarga desde la revisión fijada. Una copia local puede colocarse en `adapter/`
si su hash coincide.

## Machotes reutilizados

- `informe/main.tex`: diseño y estructura editorial del informe del Proyecto 3.
- `presentacion/index.html`: diseño navegable y exportable de la presentación.
- `presentacion.pdf`: se regenerará; no se reutiliza el PDF anterior como evidencia final.

## Regla de trazabilidad

Las métricas heredadas deben poder rastrearse a `resultados/`, los datos a `datos/` y las nuevas
afirmaciones de producción a `docs/evidencias/`. No se presentará una captura, URL o log como real
si todavía no fue producido por el servicio desplegado.
