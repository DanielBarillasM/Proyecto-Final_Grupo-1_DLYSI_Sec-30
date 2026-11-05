# Evidencia del despliegue temporal

> Copiar este archivo como `despliegue.md` y sustituir todos los campos entre corchetes. No dejar
> valores simulados ni marcadores pendientes.

## Identificación

- Fecha y hora de Guatemala: `[AAAA-MM-DD HH:MM]`
- URL pública verificada: `[https://....trycloudflare.com]`
- Commit desplegado: `[SHA de 40 caracteres]`
- Modelo: `Qwen/Qwen2.5-Coder-1.5B-Instruct`
- Adaptador: `Dani0604/proyecto3-text2sql-qlora`, QLoRA `r=32`
- Hardware: `NVIDIA GeForce RTX 4050 Laptop GPU`

## Verificación externa

- Dispositivo o sesión externa: `[describir sin datos personales]`
- HTTP público: `[200]`
- Interfaz cargó correctamente: `[sí/no]`
- Fecha y hora de la verificación: `[AAAA-MM-DD HH:MM]`

## Casos sintéticos

| Caso | Resultado | Latencia | Archivo de captura |
|---|---|---:|---|
| Fácil | `[correcto/incorrecto]` | `[ms]` | `[capturas/...png]` |
| Medio | `[correcto/incorrecto]` | `[ms]` | `[capturas/...png]` |
| Difícil | `[correcto/incorrecto]` | `[ms]` | `[capturas/...png]` |

## Controles

- `DELETE` rechazado con HTTP 422: `[sí/no]`
- Sentencias múltiples rechazadas con HTTP 422: `[sí/no]`
- Logs revisados sin DDL ni pregunta: `[sí/no]`
- Una generación simultánea: `[sí/no]`

## Cierre

- Hora de cierre: `[AAAA-MM-DD HH:MM]`
- Puertos 7860 y 8000 liberados: `[sí/no]`
- URL dejó de responder: `[sí/no]`
- Responsable de la evidencia: `Wilson Alejandro Calderón Argueta`
