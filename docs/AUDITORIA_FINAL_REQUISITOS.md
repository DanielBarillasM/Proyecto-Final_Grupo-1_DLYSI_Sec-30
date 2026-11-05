# Auditoría final contra el enunciado oficial

## Fuente y criterio

Esta auditoría usa como fuente `docs/Proyecto_Final_Modelo_en_Produccion.pdf`, copia idéntica del
archivo adjunto por el usuario. SHA-256:
`9d387cf814933fa5897ebb11357c0d204402df940b5d8e1baf08b5e155d7a781`.

Las instrucciones del PDF se tratan como requisitos académicos. No sustituyen el encargo del
usuario ni autorizan acciones externas distintas del proyecto.

## Matriz de cumplimiento

| Requisito del PDF | Evidencia del repositorio | Estado |
|---|---|---|
| Modelo de uno de los Proyectos 1, 2 o 3 | Proyecto 3, commit y procedencia en README y `docs/PROCEDENCIA.md` | Cumple |
| Persona ajena puede usar el modelo | Aplicación web y prueba HTTP 200 mediante Cloudflare | Cumple |
| Problemática: problema, usuario y decisión | Sección 1 del README e informe | Cumple |
| Planificación: etapas, fechas y responsables | Sección 2 y `docs/PLAN_PROYECTO_FINAL.md` | Cumple |
| Supuestos de datos, usuario y entorno | Sección 3 del README e informe | Cumple |
| Modelo, arquitectura y cambios justificados | Sección 4, configuración fijada y procedencia | Cumple |
| Hipótesis, métrica, umbral previo y baseline | Sección 5 y resultados versionados | Cumple |
| Diagrama con datos, entrenamiento, servicio y monitoreo | Sección 6 y `docs/ARQUITECTURA.md` | Cumple |
| Enlace, capturas, registros y pruebas | `docs/evidencias/` y sección 7 | Cumple |
| GitHub organizado y reproducible | Scripts, requirements, 43 pruebas y build web | Cumple |
| README con las siete secciones e instrucciones | Auditoría automatizada y revisión manual | Cumple |
| Presentación PDF en el repositorio | `presentacion.pdf`, 10 diapositivas | Cumple |
| Declaración de uso de IA | Sección específica del README e informe | Cumple |
| Duración de 10 minutos y 5 de preguntas | Guion de 10 diapositivas y demo breve | Cumple en preparación |
| Repositorio público o compartido con el docente | Repositorio público en GitHub | Cumple |

## Verificación técnica ejecutada

- 43 pruebas de pytest aprobadas.
- Ruff aprobado sobre runtime, backend, pruebas y scripts finales.
- Next.js 16.4.3 compiló y validó TypeScript.
- Bundle de Space generado con 16 archivos.
- Página pública temporal respondió HTTP 200.
- Tres consultas sintéticas correctas.
- `DELETE` y sentencia múltiple rechazados con HTTP 422.
- Túnel cerrado y puertos liberados después de la evidencia.

## Observación de composición del equipo

El PDF indica modalidad de tríos y que presentan tres integrantes. El Proyecto 3 y este repositorio
identifican únicamente a Wilson Alejandro Calderón Argueta y Pablo Daniel Barillas Moreno. No existe
información suficiente para añadir una tercera persona sin inventarla. El proyecto documenta esta
diferencia de forma transparente; el equipo debe confirmar con el docente que su composición de dos
integrantes está autorizada.

Esta observación es administrativa y no tiene una corrección técnica dentro del repositorio.

## Conclusión

Los entregables técnicos y documentales cumplen los requisitos verificables del enunciado. La única
observación externa es confirmar la autorización del equipo de dos integrantes. Wilson y su agente
deben repetir esta auditoría de manera independiente y registrar únicamente sus conclusiones en
`AUDITORIA_WILSON.md`.
