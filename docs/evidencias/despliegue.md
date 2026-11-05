# Evidencia del despliegue temporal

## Identificación

- Fecha: 5 de noviembre de 2026.
- Ventana de operación en Guatemala: 16:13:10 a 16:17:26.
- URL pública verificada: https://bytes-aside-abraham-troy.trycloudflare.com
- Commit desplegado: `0e304a20f41ed216ae66bc4e535d4a75366cf3a8`.
- Frontend: Next.js 16.4.3 en `127.0.0.1:3000`.
- Puerta pública: Cloudflare Quick Tunnel 2026.10.7.
- Backend: FastAPI en `127.0.0.1:8000`.
- Modelo: `Qwen/Qwen2.5-Coder-1.5B-Instruct` con QLoRA `r=32`.
- Hardware: NVIDIA GeForce RTX 4050 Laptop GPU.

La URL era temporal y se cerró después de reunir la evidencia. El script reproducible
`scripts/demo/start_demo.ps1` genera una URL nueva para la presentación.

## Verificación

| Control | Resultado |
|---|---|
| Página pública | HTTP 200 |
| Backend | `mode=model`, adaptador local listo |
| Caso fácil | Correcto, 43,039 ms con carga fría |
| Caso medio | Correcto, 3,014 ms |
| Caso difícil | Correcto, 8,030 ms |
| `DELETE` | Rechazado con HTTP 422 |
| Sentencias múltiples | Rechazadas con HTTP 422 |
| Cierre | Procesos detenidos y puertos 3000, 7860, 8000 y 20241 libres |

Los tres casos usaron únicamente el esquema sintético de clientes y pedidos incluido en la
aplicación. El reporte estructurado se conserva en
`docs/evidencias/pruebas/verificacion_publica_2026-11-05.json`.

## Capturas

- `capturas/interfaz_publica_2026-11-05.png`: página cargada mediante la URL pública.
- `capturas/interfaz_conectada_local_2026-11-05.png`: misma versión con la API en modo modelo,
  variante QLoRA y adaptador local.

## Cierre y privacidad

La prueba no utilizó credenciales, datos personales ni esquemas reales. El registro estructurado
contiene identificadores de caso, SQL sintético y latencias, pero no conserva las preguntas ni el
DDL. El túnel quedó cerrado a las 16:17:26, hora de Guatemala.
