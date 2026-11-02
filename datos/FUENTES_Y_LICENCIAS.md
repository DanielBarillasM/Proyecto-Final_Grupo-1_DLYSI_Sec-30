# Fuentes, procedencia y licencias de los datos

## Dataset incluido

El dataset es sintético. OpenAI Codex asistió en la generación de plantillas de preguntas y SQL sobre 12 esquemas propios del equipo. Los integrantes revisaron los artefactos y son responsables de su contenido. No se redistribuyen Spider, BIRD, datos personales ni bases de terceros.

Cada registro conserva:

- esquema y dificultad;
- pregunta y SQL de referencia;
- fuente y mecanismo de generación;
- licencia;
- estado de validación;
- motivo de descarte, cuando corresponde.

El código y los datos propios se distribuyen bajo la licencia MIT incluida en la raíz del repositorio. El modelo base y las dependencias conservan las licencias publicadas por sus respectivos autores.

## Validación MySQL

Las consultas pasaron de `datos/entrenamiento/candidatos.jsonl` a `datos/entrenamiento/aceptados.jsonl` únicamente después de ejecutarse sin error en MySQL 8.4.10 con `ONLY_FULL_GROUP_BY`. Se generaron 2,592 candidatos y se aceptaron los 2,592; por ello `datos/descartes/descartados.jsonl` contiene cero filas. Los conteos, hashes y configuración del motor están en `resultados/dataset_manifest.json`.

## Revisión humana

La muestra estratificada y determinista de `datos/revision_muestra.csv` contiene 100 ejemplos. La revisión quedó confirmada el 24 de octubre de 2026:

- Pablo Daniel Barillas Moreno: filas 1 a 50;
- Wilson Alejandro Calderón Argueta: filas 51 a 100.

Las 100 decisiones figuran como `aprobado_revision_humana`. El resumen auditable está en `resultados/revision_asistida.json`; la asignación y las actividades confirmadas también se documentan en `BITACORA.md` y `CONTRIBUCIONES.md`.

## Uso de inteligencia artificial

Codex apoyó la preparación de plantillas, implementación, pruebas y documentación. La aceptación de cada par dependió de ejecución en MySQL y la muestra final fue confirmada por el equipo. Ninguna API externa participa en la generación SQL durante la evaluación.
