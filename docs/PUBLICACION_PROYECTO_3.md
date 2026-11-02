# Publicación del proyecto y del adapter

Estado verificado el 25 de octubre de 2026: el repositorio GitHub continúa accesible mediante el
remoto autenticado del equipo y el adapter de Hugging Face responde públicamente, sin token, en la
revisión de tarjeta registrada en `adapter/registry.json`.

Este procedimiento se ejecuta únicamente después de seleccionar el adapter ganador, aprobar la auditoría final y confirmar la autoría real de los cambios.

## 1. Distribución de artefactos

- GitHub privado: código, datos, resultados, documentos y el adapter ganador mediante Git LFS.
- Hugging Face público: una segunda copia descargable sin token del adapter ganador y su model card.
- No publicar el modelo base de Qwen ni checkpoints intermedios.
- No incluir `.venv-gpu/`, `web/node_modules/`, `web/.next/`, cachés ni secretos.

## 2. Verificar el adapter ganador

```powershell
Test-Path adapter\adapter_config.json
Test-Path adapter\adapter_model.safetensors
Get-FileHash adapter\adapter_model.safetensors -Algorithm SHA256
Get-Content adapter\selection.json
```

El archivo `.gitattributes` ya asigna `adapter/*.safetensors` a Git LFS. Inicializa LFS para este clon y comprueba el seguimiento:

```powershell
git lfs install --local
git check-attr filter -- adapter/adapter_model.safetensors
git lfs status
```

## 3. GitHub privado

El remoto configurado es `origin`. Antes de enviar, autentica la cuenta correcta mediante Git Credential Manager cuando `git push` abra el navegador. No uses un token dentro del repositorio.

```powershell
git status --short
git diff --check
git add .
git status --short
git commit -m "Finalizar entrenamiento e integrar adapter ganador"
git push -u origin main
```

Cada integrante debe crear sus propios commits desde su cuenta. No se deben alterar autores ni inventar evidencia de colaboración. Después del último commit sustantivo:

```powershell
git log --all --date=iso --stat | Out-File -Encoding utf8 historial_git.txt
git add historial_git.txt
git commit -m "Actualizar historial de entrega"
git push origin main
```

## 4. Hugging Face Hub público

El CLI ya está dentro de `.venv-gpu`. La autenticación requiere un token personal con permiso de escritura:

```powershell
.\.venv-gpu\Scripts\hf.exe auth login
.\.venv-gpu\Scripts\hf.exe auth whoami
```

El adapter ganador está publicado como modelo público en `Dani0604/proyecto3-text2sql-qlora`. Para actualizarlo, sube únicamente `adapter/`:

```powershell
.\.venv-gpu\Scripts\hf.exe upload Dani0604/proyecto3-text2sql-qlora adapter\ . --repo-type model --commit-message "Actualizar adapter ganador"
```

Obtén la revisión inmutable y regístrala en `adapter/registry.json` junto con el modelo base y el SHA-256 local:

```powershell
.\.venv-gpu\Scripts\python.exe -c "from huggingface_hub import HfApi; print(HfApi().model_info('Dani0604/proyecto3-text2sql-qlora').sha)"
```

La tarjeta puede recibir correcciones documentales posteriores sin cambiar los pesos. Por eso `config.json`
mantiene la revisión de pesos probada en T4; `current_card_revision` registra por separado el commit actual de
la tarjeta pública. No cambies `adapter_revision` sin repetir la prueba de recuperación y el smoke test T4.

Comprueba además el acceso anónimo. Debe devolver `HTTP: 200` y `Privado: False`:

```powershell
.\.venv-gpu\Scripts\python.exe -c "import requests; r=requests.get('https://huggingface.co/api/models/Dani0604/proyecto3-text2sql-qlora', timeout=30); print('HTTP:', r.status_code); print('Privado:', r.json().get('private'))"
```

## 5. Prueba de recuperación

Descarga la revisión publicada en una carpeta nueva fuera del repositorio y compara los hashes:

```powershell
$Revision = "SHA_COMPLETO_DEL_HUB"
$Recovered = "..\artifacts_locales\recovered_adapter"
.\.venv-gpu\Scripts\hf.exe download Dani0604/proyecto3-text2sql-qlora --revision $Revision --local-dir $Recovered
Get-FileHash adapter\adapter_model.safetensors -Algorithm SHA256
Get-FileHash "$Recovered\adapter_model.safetensors" -Algorithm SHA256
```

Los dos hashes deben ser idénticos. Finalmente, prueba que la copia recuperada carga con el modelo base antes de considerar el respaldo válido.

## 6. Acciones que requieren al equipo

- Autenticación de GitHub y Hugging Face.
- Confirmar que ambos commits reflejan trabajo auténtico.
- Autorizar el envío al repositorio privado y las actualizaciones del Hub público.
- Compartir el repositorio privado con el docente y entregar el ZIP/PDF en Canvas.
