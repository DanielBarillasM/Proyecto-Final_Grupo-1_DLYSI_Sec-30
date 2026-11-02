---
title: Text-to-SQL con QLoRA
emoji: 🗃️
colorFrom: teal
colorTo: orange
sdk: gradio
sdk_version: 6.31.0
app_file: app.py
pinned: false
python_version: "3.12"
---

# Text-to-SQL con QLoRA

Aplicación del Proyecto Final de Deep Learning y Sistemas Inteligentes. Convierte un esquema MySQL
y una pregunta en español en una única consulta de solo lectura.

- Modelo base: `Qwen/Qwen2.5-Coder-1.5B-Instruct`.
- Adaptador: `Dani0604/proyecto3-text2sql-qlora`, revisión inmutable en `config.json`.
- Variante seleccionada: QLoRA `r=32`.
- Privacidad: la telemetría no almacena el esquema ni la pregunta.

El código fuente, las pruebas, los datos y la documentación técnica están en el repositorio GitHub
del Proyecto Final.
