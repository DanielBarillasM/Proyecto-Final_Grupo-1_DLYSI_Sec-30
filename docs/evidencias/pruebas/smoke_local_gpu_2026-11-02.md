# Prueba de humo local con GPU

## Identificación

- Fecha local: 2 de noviembre de 2026, 16:51, Guatemala.
- Entorno: Windows, Python 3.11.17.
- GPU: NVIDIA GeForce RTX 4050 Laptop GPU.
- Variante: QLoRA `r=32`.
- Adaptador SHA-256: `d3126183a092521cb1feffb9424b188552d27bb8fc4b51a8d13a1348d89016f1`.
- Request ID: `c7a534ac12da`.

## Entrada

La prueba utilizó un esquema mínimo de `clientes` con columnas `id`, `nombre` y `ciudad`. La
pregunta solicitó listar nombres y ciudades. El contenido exacto no quedó almacenado en el log de
telemetría; se describe aquí porque forma parte de un caso sintético y versionado.

## Resultado

```sql
SELECT nombre, ciudad
FROM clientes
ORDER BY nombre;
```

| Métrica | Valor |
|---|---:|
| Estado | Correcto |
| Primera carga e inferencia | 65,082 ms |
| Pico de VRAM asignada | 1,472 MB |
| Tipo de salida | `SELECT` de solo lectura |

La primera medición incluye carga del modelo base y del adaptador. No debe compararse directamente
con una solicitud caliente. El siguiente bloque de evidencia medirá latencia caliente y el servicio
público desplegado.
