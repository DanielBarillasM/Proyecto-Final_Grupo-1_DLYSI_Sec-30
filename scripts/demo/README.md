# Demostración reproducible

Estos scripts abren la arquitectura temporal verificada para la exposición:

```text
Internet -> Cloudflare Quick Tunnel -> Next.js 127.0.0.1:3000
                                       -> FastAPI 127.0.0.1:8000
                                       -> RTX 4050 + QLoRA r=32
```

## Preparación única

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-demo.txt
pnpm.cmd --dir web install --frozen-lockfile
```

`cloudflared.exe` debe estar en `PATH`, en
`%USERPROFILE%\.cache\cloudflared\cloudflared.exe` o indicarse mediante `-CloudflaredPath`.

## Abrir, verificar y cerrar

```powershell
.\scripts\demo\start_demo.ps1
.\scripts\demo\verify_demo.ps1 -RunInference
.\scripts\demo\stop_demo.ps1
```

Los procesos se abren sin ventanas adicionales. El estado, los PID y los logs temporales se guardan
en `.demo-run/`, que Git ignora. El script de cierre solo detiene procesos cuyo PID, nombre y hora de
inicio coinciden con el estado registrado.

El lanzador recompila Next.js con el proxy `/backend-api` antes de abrir la demostración. Gradio se
conserva como interfaz del bundle para Hugging Face Spaces, pero no participa en el túnel local.

Para probar sin publicar una URL:

```powershell
.\scripts\demo\start_demo.ps1 -LocalOnly
```

La URL de Cloudflare es temporal. Solo deben usarse los esquemas sintéticos incluidos en la
interfaz. Cooler Boost es recomendable mientras se ejecutan las tres inferencias, no durante la
documentación.
