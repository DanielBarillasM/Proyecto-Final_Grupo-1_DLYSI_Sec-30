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
| Gradio `share=True` | Gratis | RTX 4050 local | Solo mientras corre | Recomendado para demo inmediata |
| Cloudflare Quick Tunnel | Gratis | RTX 4050 local | Solo mientras corre | Alternativa de contingencia |
| Proveedor GPU serverless | Variable | Sí | Estable | Requiere método de pago |

## Modo de demostración pública temporal

La aplicación solo solicita un enlace público cuando se establece explícitamente:

```powershell
$env:GRADIO_SHARE = "true"
.\.venv\Scripts\python.exe app.py
```

Sin esa variable, la aplicación permanece únicamente en `127.0.0.1`. El enlace temporal termina
al cerrar el proceso. Durante la demostración se deben aplicar estas condiciones:

- usar únicamente esquemas sintéticos;
- no pegar credenciales, datos personales ni DDL confidencial;
- mantener una sola generación simultánea;
- registrar request ID y latencia de los casos demostrados;
- cerrar el proceso y verificar que el enlace deje de responder al finalizar.

## Ruta permanente

Cuando la cuenta cumpla 30 días o el equipo autorice PRO, se publicará el contenido de
`dist/huggingface-space/`. El bundle contiene 16 archivos y aproximadamente 28 KB. Excluye pesos,
datasets, notebooks, logs, capturas, secretos y entornos virtuales.
