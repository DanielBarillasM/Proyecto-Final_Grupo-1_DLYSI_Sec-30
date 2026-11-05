# Decisiones de despliegue

## Objetivo

Publicar una interfaz que permita a una persona externa utilizar el modelo QLoRA con una GPU
compatible, sin subir datos de entrenamiento, esquemas de usuarios, logs ni credenciales.

## Intento de Hugging Face Spaces

El 2 de noviembre de 2026 se intentó crear el Space público
`Dani0604/proyecto-final-text2sql` con Gradio y ZeroGPU. Hugging Face respondió HTTP 402 y no creó
el repositorio. La cuenta autenticada tiene menos de 30 días, mientras que ZeroGPU gratuito exige
una cuenta verificada con al menos 30 días de antigüedad.

No se subió ningún archivo. Tampoco se creó un Space estático para cambiarlo después, porque ese
flujo no resolvería la restricción de cómputo y podría interpretarse como un intento de rodear la
política de la plataforma.

## Alternativas evaluadas

| Alternativa | Costo | GPU | Permanencia | Decisión |
|---|---:|---:|---|---|
| Hugging Face ZeroGPU | Gratis al cumplir 30 días | Sí | Estable | Bloqueado temporalmente |
| Hugging Face PRO | USD 9/mes | ZeroGPU con mayor cuota | Estable | Requiere decisión de pago |
| Gradio `share=True` | Gratis | RTX 4050 local | Solo mientras corre | Bloqueado por inspección HTTPS local |
| Cloudflare Quick Tunnel | Gratis | RTX 4050 local | Solo mientras corre | Seleccionado y verificado |
| Proveedor GPU serverless | Variable | Sí | Estable | Requiere método de pago |

## Demostración pública verificada

El 5 de noviembre de 2026 se desplegó el commit
`0e304a20f41ed216ae66bc4e535d4a75366cf3a8` mediante Next.js, FastAPI y Cloudflare. La URL temporal
respondió HTTP 200 y se cerró al terminar la prueba.

```powershell
.\scripts\demo\start_demo.ps1
.\scripts\demo\verify_demo.ps1 -RunInference
.\scripts\demo\stop_demo.ps1
```

El frontend público escucha solo en `127.0.0.1:3000`; FastAPI permanece en `127.0.0.1:8000` y nunca
se publica directamente. Durante cada demostración se aplican estas condiciones:

- usar únicamente esquemas sintéticos;
- no pegar credenciales, datos personales ni DDL confidencial;
- mantener una sola generación simultánea;
- registrar request ID y latencia de los casos demostrados;
- cerrar el proceso y verificar que el enlace deje de responder al finalizar.

No se añadió una exclusión a Kaspersky. El equipo descartó el túnel nativo de Gradio después de dos
fallos de conexión y conservó intacta la inspección HTTPS. `cloudflared.exe` tenía firma válida y la
huella SHA-256 registrada durante la prueba fue
`2493dbc168923bb3e59e5e7716f71deced92992eea9acd6e9d74f84ac7751343`.

## Ruta permanente

Cuando la cuenta cumpla 30 días o el equipo autorice PRO, se publicará el contenido de
`dist/huggingface-space/`. El bundle contiene 16 archivos y aproximadamente 28 KB. Excluye pesos,
datasets, notebooks, logs, capturas, secretos y entornos virtuales.
