# Plan de ejecución del Proyecto Final

## Objetivo de entrega

Poner en producción el modelo Text-to-SQL del Proyecto 3, permitir que una persona externa lo use
y presentar evidencia verificable de disponibilidad, seguridad, pruebas y observabilidad. La
versión lista para exposición debe quedar cerrada el 9 de noviembre de 2026.

## Alcance cerrado

- No entrenar un modelo nuevo.
- Mantener datos, baseline, QLoRA, prompt y métricas del Proyecto 3.
- Adaptar el runtime para descargar el adaptador fijado cuando falten pesos locales.
- Publicar una aplicación Gradio con GPU bajo demanda.
- Conservar FastAPI y Next.js como ruta local y evidencia de arquitectura.
- Registrar telemetría técnica sin almacenar pregunta ni esquema.
- Entregar README técnico, presentación PDF, código y evidencias.

## Calendario y puertas de calidad

| Fecha | Trabajo | Puerta de aceptación |
|---|---|---|
| 2 nov | Leer enunciado, auditar P3 y definir arquitectura | Matriz completa de requisitos |
| 3 nov | Migración curada, procedencia y aplicación base | Suite CPU sin regresiones |
| 4 nov | UI Gradio, seguridad, errores y telemetría | Flujo local con runtime falso y real |
| 5 nov | Despliegue y pruebas | URL pública + tres casos + capturas + cierre |
| 5 nov | README, arquitectura y evidencias | Siete secciones y ejecución reproducible |
| 5 nov | Adaptar HTML y exportar PDF | Presentación de 10 diapositivas, 10 minutos |
| 9 nov | Ensayo y release candidata | Demo desde otro dispositivo y plan B |
| 10–12 nov | Correcciones de evidencia y claridad | No introducir cambios experimentales |
| 13 nov | Segunda fecha posible de presentación | Mismo release probado |
| 14–15 nov | Auditoría final y entrega | Último commit antes de las 23:59 |

## Responsabilidades de cierre

| Área | Responsable principal | Revisión |
|---|---|---|
| Implementación, despliegue y documentación | Pablo Daniel Barillas Moreno | Auditoría independiente |
| Auditoría final en Markdown | Wilson Alejandro Calderón Argueta y su agente | Sin editar artefactos |
| Presentación oral | Ambos | Ambos |

El enunciado general indica modalidad de tríos, pero el Proyecto 3 identifica únicamente a estos dos
integrantes. No se asignó trabajo ficticio a una tercera persona.

## Evidencia mínima antes del congelamiento

1. URL pública abierta desde una sesión externa.
2. Captura del estado listo y de tres generaciones representativas.
3. Evento de telemetría anonimizado por cada caso.
4. Prueba de rechazo de `DELETE` y de sentencias múltiples.
5. Latencia de primera solicitud y solicitudes calientes.
6. Commit exacto y revisión del modelo/adaptador desplegados.
7. Resultado de pytest y build web.
8. Demostración de contingencia local o grabada.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Cola o cuota de ZeroGPU | Probar con anticipación; activar T4 durante la exposición si hace falta |
| Incompatibilidad Python/PyTorch | Fijar versiones compatibles y conservar prueba T4 del Proyecto 3 |
| Descarga lenta del modelo | Usar revisiones inmutables, caché del Space y calentamiento previo |
| SQL peligroso | Validación de sentencia única y solo lectura antes de responder |
| Fuga de datos en logs | No registrar contenido, solo tamaños y metadatos técnicos |
| Servicio inaccesible en clase | Demostración local, capturas y video corto como contingencia |
| Diferencia entre dos integrantes y modalidad de tríos | Confirmar composición antes de cerrar portada y reparto |
| Cuenta de Hugging Face menor de 30 días | Demo temporal de Gradio; ZeroGPU cuando la cuenta sea elegible |

## Criterio de terminado

El proyecto cumplió el criterio técnico el 5 de noviembre: repositorio reproducible, URL pública
verificada, evidencias reales y fechadas, README con siete secciones, presentación de diez minutos y
procedimiento de demostración reproducible. Solo queda la auditoría independiente de Wilson en MD.
