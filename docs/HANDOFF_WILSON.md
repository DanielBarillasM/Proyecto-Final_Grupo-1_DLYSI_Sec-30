# Handoff final para Wilson

## Alcance

El código, las pruebas, la aplicación, la automatización de demostración, la evidencia, el README,
la arquitectura y la presentación quedan cerrados por Pablo. Wilson y su agente no necesitan
implementar, corregir ni volver a desplegar código. Su único trabajo pendiente es terminar el
informe en LaTeX y compilarlo.

## Estado recibido

- Suite automatizada aprobada: 43 pruebas.
- Ruff aprobado para el código de producción y sus pruebas.
- Build de Next.js aprobado con Next.js 16.4.3.
- Bundle de Hugging Face generado con 16 archivos y sin datos, pesos ni secretos.
- Auditoría `--handoff` aprobada.
- Inferencia real local aprobada en RTX 4050.
- Presentación HTML y PDF disponibles.
- Evidencia pública documentada y auditoría final aprobada.
- Informe fuente disponible en `informe/main.tex`; su revisión y compilación final quedan delegadas.

## Única tarea: terminar y compilar el informe

Revisar `informe/main.tex` y actualizar únicamente los resultados finales:

- cambiar el conteo de pruebas a 43;
- describir FastAPI local, Gradio como puerta pública y Cloudflare Quick Tunnel como transporte;
- copiar del README y `docs/evidencias/despliegue.md` la URL, fecha, commit, latencias y capturas;
- indicar que la auditoría final aprobó todos los controles;
- mantener la declaración de uso de inteligencia artificial;
- conservar las métricas del Proyecto 3 sin recalcularlas.

Compilar hasta que no existan errores y revisar visualmente todas las páginas. El PDF final debe
quedar en la raíz como `informe.pdf`. No modificar `resultados/`, `datos/`, `adapter/registry.json`
ni `config.json`.

## Cierre del informe

Ejecutar:

```powershell
python scripts\audit_final.py --final
git status --short
```

La auditoría ya debe terminar con código 0 antes de editar el informe. Después de compilarlo, crear
un commit que contenga únicamente `informe/main.tex` e `informe.pdf`. Un mensaje sugerido es
`docs: compilar informe final`.

## Qué no debe hacer Wilson

- No reentrenar el modelo.
- No cambiar hiperparámetros ni métricas.
- No subir `adapter_model.safetensors` a GitHub.
- No registrar preguntas, DDL reales, credenciales o información personal.
- No atribuir evidencia a una prueba que no se haya ejecutado.
