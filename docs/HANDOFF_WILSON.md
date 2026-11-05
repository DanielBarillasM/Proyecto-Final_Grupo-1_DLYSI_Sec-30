# Auditoría independiente para Wilson y su agente

## Única tarea

El proyecto ya está implementado, documentado, compilado y probado. Wilson y su agente deben hacer
una última revisión independiente sin modificar código, datos, documentos ni artefactos.

El único archivo que deben crear es `AUDITORIA_WILSON.md` en la raíz del repositorio.

El PDF oficial de instrucciones se adjunta en
`docs/Proyecto_Final_Modelo_en_Produccion.pdf`. La revisión debe contrastar el repositorio contra
ese documento, no solo contra esta lista. Como referencia adicional, Pablo dejó su propia matriz en
`docs/AUDITORIA_FINAL_REQUISITOS.md`.

## Contenido del Markdown

El informe de auditoría debe incluir:

1. fecha, nombre del auditor y commit revisado;
2. lista breve de elementos correctos;
3. lista de problemas encontrados, si existe alguno;
4. comandos ejecutados y su resultado;
5. conclusión: `aprobado`, `aprobado con observaciones` o `requiere corrección`.

Si no encuentran problemas, deben indicarlo explícitamente. No deben inventar observaciones para
llenar la sección.

## Comandos mínimos

```powershell
python -m pytest -q
python -m ruff check production.py app.py backend text2sql tests scripts\audit_final.py scripts\build_space_bundle.py
pnpm.cmd --dir web build
python scripts\audit_final.py --final
git status --short
```

También deben abrir y revisar visualmente `README.md`, `informe.pdf` y `presentacion.pdf`, y comprobar
que los enlaces locales a evidencia existen.

## Límites

- No editar archivos existentes.
- No reentrenar ni volver a desplegar el modelo.
- No actualizar dependencias.
- No corregir directamente un hallazgo; documentarlo en `AUDITORIA_WILSON.md`.
- No subir pesos, cachés, logs privados o archivos de `.demo-run/`.
