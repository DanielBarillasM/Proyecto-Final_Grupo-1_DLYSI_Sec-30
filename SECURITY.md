# Seguridad y dependencias

Última revisión: 2026-10-25.

## Controles activos

- La API acepta únicamente las variantes `base` y `qlora` y limita el tamaño de esquema y pregunta.
- La salida se analiza como una sola sentencia `SELECT` o `WITH ... SELECT`; DDL y DML se rechazan.
- Solo se atiende una inferencia GPU a la vez y un fallo de carga libera el runtime antes de reintentar.
- Qwen y el adapter se cargan desde revisiones inmutables declaradas en `config.json`.
- La carga exige `safetensors` y usa `trust_remote_code=False`.
- La interfaz valida la forma de todas las respuestas de la API y no interpreta HTML recibido.
- El editor web valida sintaxis MySQL, sentencia única y solo lectura; no ejecuta SQL arbitrario
  contra una base de datos.
- Los tokens de Hugging Face no deben guardarse en el repositorio, notebooks, capturas ni archivos `.env`.

## Auditoría de paquetes

`pnpm audit --prod` no reportó vulnerabilidades conocidas.

La auditoría del entorno Python permitió actualizar `datasets`, `filelock`, `fsspec` y parte de
`setuptools`. Permanecen avisos en Transformers 4 y en la versión de setuptools compatible con
PyTorch CUDA 2.11. Actualizarlos por completo exige migrar a Transformers 5 y setuptools 83/84,
lo que entra en conflicto con la combinación PyTorch/PEFT usada para entrenar y validar el adapter.

El riesgo residual se reduce porque los identificadores de modelo no proceden del usuario, las
revisiones están fijadas, no se ejecuta código remoto y los pesos son `safetensors`. Antes de una
migración mayor se debe repetir la prueba integral en T4 y la comparación de las 40 consultas.

## Publicación del adapter

El repositorio público de Hugging Face debe contener solamente la tarjeta del modelo, configuración
PEFT, pesos `safetensors` y metadatos de selección. No se deben publicar tokens, cachés, rutas locales
ni archivos de datos que no formen parte de la entrega autorizada.
