# Evidencias de producción

Esta carpeta contiene únicamente evidencia producida por el servicio final:

- `capturas/`: interfaz, resultados y estado del servicio;
- `logs/`: extractos anonimizados de telemetría;
- `pruebas/`: comandos, resultados y fechas de pruebas de humo;
- `despliegue.md`: URL, commit, revisión del modelo, proveedor y fecha.

No se deben crear evidencias simuladas. Cada artefacto debe indicar fecha, entorno y commit.

## Evidencia disponible

- Prueba de humo local con RTX 4050 del 2 de noviembre de 2026.
- Evento de telemetría anonimizado asociado al request ID `c7a534ac12da`.
- Despliegue temporal público verificado el 5 de noviembre de 2026.
- Tres inferencias sintéticas correctas con latencias de 43,039 ms, 3,014 ms y 8,030 ms.
- Rechazo de `DELETE` y sentencias múltiples con HTTP 422.
- Dos capturas revisadas: interfaz pública e interfaz conectada al modelo.

La URL de Cloudflare era temporal y se cerró después de la prueba. El procedimiento reproducible
para generar una URL nueva se conserva en `scripts/demo/`.
