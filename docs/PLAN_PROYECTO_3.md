# Plan de ejecución del Proyecto 3

> **Actualización final del 25 de octubre de 2026:** las dos corridas completas finalizaron. R16 y R32 alcanzaron 97.4% de EX ponderada (39/40); R32 fue seleccionado por menor latencia p95. El adapter está integrado, activado y publicado con acceso anónimo. La muestra humana, la bitácora y la prueba limpia en Colab/T4 quedaron documentadas. También se repitió la ejecución completa en MySQL 8.4.10: 2,592/2,592 pares de entrenamiento y 40/40 consultas de validación se aceptaron sin error.

## 1. Resultado esperado

El entrenamiento se ejecutó en la estación local verificada: Intel Core i7-12650H (10 núcleos, 16 procesadores lógicos), 31.7 GB de RAM y NVIDIA GeForce RTX 4050 Laptop con 6 GB de VRAM. El smoke test confirmó que QLoRA cabía antes de las corridas completas. Al 25 de octubre de 2026, el repositorio permite que el docente instale `requirements.txt` en Google Colab con GPU T4, cargue el modelo en menos de cinco minutos y llame:

```python
generar_sql(esquema: str, pregunta: str, ejecutar=None) -> str
```

La función devolverá, en menos de 30 segundos, una sola consulta determinista `SELECT` o `WITH ... SELECT` compatible con MySQL 8.4.10. El mismo archivo deberá operar con y sin adapter según `config.json`.

El éxito se decidirá principalmente por dos cifras:

- EX ponderada con adapter: meta `>= 0.70`.
- Mejora absoluta sobre el baseline: meta `>= 0.15`.

## 2. Decisiones cerradas

### Modelo y entrenamiento

- Base: `Qwen/Qwen2.5-Coder-1.5B-Instruct`.
- Técnica: QLoRA con cuantización de 4 bits NF4, double quantization y cómputo FP16.
- Configuración A: `r=16`.
- Configuración B: `r=32`.
- Constantes entre A y B: `lora_alpha=32`, `lora_dropout=0.05`, módulos objetivo, dataset, orden de ejemplos, semilla, épocas, learning rate, scheduler, batch efectivo, prompt y evaluación.
- Módulos objetivo iniciales: `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`.
- Semilla: `2026` para Python, NumPy, PyTorch, partición y generación.
- Punto de partida: 2 épocas, learning rate `2e-4`, batch por dispositivo 1, acumulación 16, gradient checkpointing y secuencia máxima 2,048 tokens. Las dos corridas se ejecutan secuencialmente en la GPU local.
- Los adapters experimentales y checkpoints se guardan fuera de Git; sólo el ganador se copia a `adapter/`.
- Regla de longitud: medir truncamiento antes de entrenar; ampliar contexto o filtrar de forma documentada si más de 1% de los ejemplos pierde SQL o partes críticas del esquema.

La hipótesis registrada antes del entrenamiento será: **aumentar el rango de 16 a 32 mejora consultas de dificultad media y difícil al aportar capacidad para relaciones y composición SQL, a costa de más parámetros y tiempo; la mejora puede ser nula si el límite real es calidad de datos**.

### Datos

- Resultado congelado: 2,592 candidatos y 2,592 pares válidos.
- Fuente utilizada: generación sintética determinista sobre 12 esquemas propios, con plantillas auditables y licencia MIT. Spider y BIRD se excluyeron para evitar mezclar licencias y conversiones no verificadas.
- Una unidad de ejemplo contendrá como mínimo: `schema_id`, DDL completo, pregunta en español, SQL MySQL, dificultad, fuente, estado de validación y motivo de descarte.
- Todo par aceptado debe ejecutar sin error contra una instancia poblada de MySQL 8.4.10.
- Se conservarán las licencias y la procedencia de cada fuente; los datos que no permitan redistribución se reconstruirán mediante scripts o se excluirán del repositorio.
- La deduplicación se hará antes de la partición.

### Validación

- Dos esquemas propios inéditos, congelados antes del entrenamiento.
- 40 preguntas escritas por el equipo: 14 fáciles, 14 medias y 12 difíciles.
- Partición por `schema_id`; una aserción automática fallará si existe intersección entre esquemas de entrenamiento y validación.
- Pesos: fácil 1, media 2, difícil 3.
- Comparación por resultados: tolerancia de redondeo a dos decimales; el orden solo se compara cuando la pregunta lo exige.
- Reportar EX total y por nivel, latencia p50/p95, tasa de SQL ejecutable y errores por categoría.

### Inferencia

El prompt será idéntico con y sin adapter e incluirá:

1. rol de experto en MySQL 8.4;
2. esquema completo delimitado;
3. pregunta y columnas solicitadas;
4. reglas de una sola consulta, solo lectura, SQL sin Markdown;
5. recordatorio de `ONLY_FULL_GROUP_BY`.

La salida pasará por un saneamiento mínimo y determinista: remover cercas Markdown, extraer una única sentencia, analizar el AST y rechazar cualquier nodo de escritura. No se "arreglará" silenciosamente la semántica con reglas manuales que favorezcan la validación.

El experimento de inferencia comparará:

- **Control:** generación directa, sin llamar `ejecutar`.
- **Tratamiento:** ejecutar el primer candidato y, únicamente si MySQL devuelve error, pedir una reparación al mismo modelo con el mensaje de error. Máximo dos generaciones y dos llamadas a `ejecutar`, dejando margen bajo el límite oficial de tres.

## 3. Plan de datos paso a paso

1. Crear los 12 esquemas de entrenamiento y los 2 de validación con DDL, claves, comentarios y datos semilla realistas.
2. Elegir y documentar las fuentes públicas y sus licencias.
3. Traducir preguntas sin traducir identificadores del esquema.
4. Convertir sintaxis a MySQL con reglas explícitas; no confiar solamente en un transpiler.
5. Levantar `mysql:8.4.10`, cargar cada esquema y ejecutar cada consulta.
6. Registrar cada descarte con una taxonomía: sintaxis, dialecto, esquema incompleto, ejecución, duplicado, traducción ambigua o respuesta vacía.
7. Revisar manualmente una muestra estratificada de al menos 100 pares.
8. Congelar manifiestos con conteos y hashes antes del entrenamiento.

## 4. Protocolo experimental

| Corrida | Modelo | Adapter | Diferencia | Propósito |
|---|---|---|---|---|
| B0 | Qwen 1.5B | No | - | Baseline con el prompt final |
| A | Qwen 1.5B | QLoRA `r=16` | Rango | Configuración de menor capacidad |
| B | Qwen 1.5B | QLoRA `r=32` | Rango | Configuración de mayor capacidad |
| I0 | Ganador A/B | Sí | Sin ejecución | Control de inferencia |
| I1 | Ganador A/B | Sí | Una reparación | Efecto de feedback de MySQL |

Para cada corrida guardar:

- configuración serializada;
- commit y hash del dataset;
- parámetros totales y entrenables;
- GPU y versiones de librerías;
- tiempo de entrenamiento y pico de memoria;
- curvas train/eval loss;
- predicciones crudas y SQL saneado;
- métricas y matriz de categorías de error.

## 5. Reparto de responsabilidad

| Área obligatoria | Responsable | Revisión cruzada | Evidencia esperada |
|---|---|---|---|
| Datos y ejecución MySQL | Wilson | Pablo | scripts, manifiestos, descartes, commits |
| Entrenamiento QLoRA | Pablo | Wilson | notebooks, configs, logs, adapter, commits |
| Validación y errores | Ambos | Ambos | 40 preguntas, CSV, etiquetado y discusión |
| Interfaz React | Pablo | Wilson | rama/PR de v0, pruebas de UI |
| Informe y presentación | Ambos | Ambos | historial de cambios y revisión final |

La tabla describe propiedad, no exclusividad. Cada cambio deberá salir de la cuenta de quien lo realizó.

## 6. Calendario hasta la entrega

| Fecha | Resultado que debe quedar cerrado |
|---|---|
| Vie 16 oct | Enunciado, arquitectura, repositorio, roles, plan, handoff v0 |
| Sáb 17 oct | MySQL 8.4.10 reproducible, formato de datos y primeros esquemas |
| Dom 18 oct | Conversión/traducción y 2,500+ candidatos con log de descartes |
| Lun 19 oct | Dataset final, validación congelada, evaluador y baseline B0 |
| Mar 20 oct | Hipótesis firmada y entrenamiento local QLoRA A |
| Mié 21 oct | Entrenamiento local QLoRA B y comparación controlada |
| Jue 22 oct | Experimento I0/I1, análisis de errores y selección de adapter |
| Vie 23 oct | Ensayo completo en Colab T4, pruebas de contrato y tiempos |
| Sáb 24 oct | Informe, UI, presentación HTML y exportación PDF |
| Dom 25 oct, antes de 18:00 | Congelamiento, auditoría, historial Git, ZIP y entrega |

Las últimas seis horas quedan como reserva; no se planifican entrenamientos nuevos el día de entrega.

## 7. Aplicación React

La app vive en `web/` y consume resultados estáticos o un backend local opcional. Nunca debe importar pesos ni librerías Python en el build de Next.js.

Rutas previstas:

- `/`: banco de pruebas con editor de esquema, pregunta, SQL, estado, latencia y traza de reparación.
- `/experimentos`: baseline vs. QLoRA A/B, curvas de loss y EX por dificultad.
- `/datos`: cobertura de esquemas, distribución y descartes.
- `/metodologia`: contrato, arquitectura, equipo y límites del proyecto.

La UI ya está implementada en `web/` con fixtures explícitamente identificados y una interfaz tipada. La integración real usa el backend FastAPI opcional y se activa al definir `NEXT_PUBLIC_API_URL`; si la variable no existe, el fixture se identifica explícitamente. El build de Next.js no importa Python ni los pesos.

## 8. Informe y presentación

El informe se mantendrá en `informe/main.tex` y será la fuente narrativa completa. Cada afirmación experimental deberá poder rastrearse a un archivo en `resultados/`.

La presentación se mantiene como HTML autocontenido en `presentacion/index.html` y tendrá un máximo de 12 diapositivas. La entrega final será `presentacion.pdf`, exportado desde Chromium con tamaño 16:9 y revisado visualmente página por página.

## 9. Riesgos y mitigaciones

| Riesgo | Señal temprana | Mitigación |
|---|---|---|
| Fuga de esquemas | IDs o DDL repetidos entre splits | Hash estructural y test automático de intersección |
| SQL válido pero semánticamente pobre | Loss baja y EX estancada | Auditar datos, balancear dificultad y revisar joins/agregaciones |
| Incompatibilidad de dialecto | Alta tasa de error en MySQL | Ejecutar cada par; reglas explícitas para fechas, límites y funciones |
| OOM en GPU local | Fallo al iniciar o secuencias largas | Cerrar otros procesos, QLoRA 4-bit, batch 1, checkpointing y análisis de longitudes; aplicar cualquier cambio a ambas corridas |
| Inferencia >30 s | p95 cercano al límite | Limitar tokens, máximo una reparación y medir con T4 real |
| Dependencias rotas | Instalación no reproducible | Fijar versiones después de la prueba limpia, no antes |
| Adapter ausente en ZIP | Puntero LFS o ruta incorrecta | Inspección del ZIP y carga offline antes de enviar |
| UI invade la entrega | `solucion.py` importa web/backend | Test de aislamiento y dependencias separadas |
| Evidencia desigual | Commits concentrados en una cuenta | Revisión diaria de bitácora, PRs y tabla de contribuciones |

## 10. Puertas de calidad

### Datos

- [x] Hay al menos 2,000 pares aceptados y un conteo reproducible.
- [x] Cada par aceptado tiene evidencia de ejecución en MySQL 8.4.10.
- [x] Cada descarte tiene motivo.
- [x] Hay al menos 10 esquemas propios en entrenamiento.
- [x] La validación contiene 2 esquemas inéditos y 40 preguntas propias.

### Modelo

- [x] Baseline y adapters usan el mismo prompt.
- [x] A y B difieren solo en `r` y sus hipótesis existen antes del entrenamiento.
- [x] Parámetros entrenables, duración y curvas están reportados.
- [x] `usar_adapter` verdadero y falso pasan el mismo test de contrato.

### Entrega

- [x] La función devuelve solo `SELECT` o `WITH ... SELECT`.
- [x] Generación repetida produce exactamente la misma salida.
- [x] Carga <5 min e inferencia p95 <30 s en T4.
- [x] `requirements.txt` se instala desde cero.
- [x] `presentacion.pdf` tiene 12 páginas o menos y ninguna se corta.
- [x] README cubre ejecución, licencias y uso de IA.
- [x] Hay 8+ entradas reales de bitácora, contribuciones e historial Git.
- [x] El ZIP contiene pesos reales del adapter, no solo punteros.

## 11. Predicción de EX

No se fijará una cifra final antes de medir. La predicción se construirá con:

1. EX por nivel sobre validación inédita;
2. intervalo bootstrap por esquema/pregunta;
3. diferencia entre fuentes y complejidad de esquemas;
4. penalización conservadora por cambio de dominio oculto.

La presentación reportará un valor puntual y un rango, además de explicar por qué el conjunto oculto podría ser más difícil que la validación propia.
