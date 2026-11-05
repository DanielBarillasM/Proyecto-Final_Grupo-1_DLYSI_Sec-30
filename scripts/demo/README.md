# Demostración reproducible

Estos scripts abren la arquitectura temporal verificada para la exposición:

```text
Internet -> Cloudflare Quick Tunnel -> Gradio 127.0.0.1:7860
                                      -> FastAPI 127.0.0.1:8000
                                      -> RTX 4050 + QLoRA r=32
```

## Preparación única

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-demo.txt
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

Si el entorno GPU no contiene Gradio, el lanzador usa `uv` para crear una interfaz aislada. El
backend conserva el entorno CUDA original y no se alteran sus dependencias.

Para probar sin publicar una URL:

```powershell
.\scripts\demo\start_demo.ps1 -LocalOnly
```

La URL de Cloudflare es temporal. Solo deben usarse los esquemas sintéticos incluidos en la
interfaz. Cooler Boost es recomendable mientras se ejecutan las tres inferencias, no durante la
documentación.
