<div align="center">

# Consola Text→SQL

**Interfaz local para inspeccionar el flujo experimental del Proyecto 3**

Next.js 16 · React 19 · TypeScript · React Bits

</div>

## Propósito

Esta aplicación presenta el contrato real del proyecto sin formar parte de la ruta oficial de evaluación. Permite introducir un esquema MySQL, escribir una pregunta en español, escoger baseline o adapter y revisar una consulta de solo lectura junto con su traza.

Si la API local no está configurada, la aplicación usa un fixture determinista y lo identifica explícitamente. Si `NEXT_PUBLIC_API_URL` sí está configurada pero la API no responde, muestra un error visible y no sustituye silenciosamente el modelo por un fixture.

## Inicio rápido

```powershell
pnpm.cmd install --frozen-lockfile
pnpm.cmd dev
```

Abre [http://localhost:3000](http://localhost:3000).

Para usar la API FastAPI del repositorio, abra una primera terminal en la raíz del proyecto:

```powershell
$env:TEXT_TO_SQL_MODE = "model"
.\.venv-gpu\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

En una segunda terminal inicie Next.js desde `web/`. `NEXT_PUBLIC_API_URL=/backend-api` hace que
Next reenvíe las solicitudes a `BACKEND_URL=http://127.0.0.1:8000`. De este modo, la misma web
funciona desde `http://localhost:3000` y desde una IP de la red local. Si la IP cambia, actualice
`NEXT_ALLOWED_DEV_ORIGINS` en `.env.local` y reinicie `pnpm.cmd dev`.

Para comprobar primero la interfaz sin cargar el modelo, use `$env:TEXT_TO_SQL_MODE = "fixture"`
en la terminal del backend. El fallback interno de la web se usa únicamente cuando
`NEXT_PUBLIC_API_URL` no está definido.

El backend admite una sola generación GPU a la vez para evitar agotar la VRAM. Si se cancela la
espera desde la interfaz, la inferencia que ya comenzó puede tardar unos segundos en finalizar antes
de que otra solicitud sea aceptada.

## Prueba manual del flujo

1. Confirme `http://127.0.0.1:8000/health`; `mode` debe ser `fixture` o `model`.
2. Abra `http://localhost:3000`. Para acceso por red, use la IP incluida en
   `NEXT_ALLOWED_DEV_ORIGINS` y reinicie Next después de cambiarla.
3. Verifique que la cabecera muestre `API fixture` o `API model`, no `API local desconectada`.
4. Elija **Baseline** o **Adapter QLoRA**, escriba la pregunta y presione **Generar SQL**.
5. En modo `model`, la primera solicitud de cada variante carga el modelo; las siguientes reutilizan
   el runtime y normalmente son más rápidas.
6. Tras generar, use **Regenerar SQL**, **Copiar SQL**, **Validar SQL** y edite/restaure el resultado.
   En accesos HTTP por IP, copiar usa una alternativa compatible si la API moderna del portapapeles
   no está disponible.

Con el esquema inicial de `clientes` y `pedidos`, pruebe:

| Nivel | Pregunta | Característica esperada |
|---|---|---|
| Fácil | `Lista los nombres y las ciudades de todos los clientes.` | selección directa |
| Fácil | `Cuenta cuántos clientes hay en cada ciudad.` | `COUNT` y agrupación |
| Media | `Muestra cada cliente y la suma de sus pedidos completados durante 2024.` | `JOIN`, suma y filtros |
| Media | `Muestra los clientes que no tienen ningún pedido.` | anti-join o `NOT EXISTS` |
| Difícil | `¿Qué cliente tuvo el mayor total de pedidos completados durante 2024?` | agregación, orden y límite |
| Difícil | `Para cada ciudad, muestra el cliente con mayor total de pedidos completados durante 2024.` | máximo por grupo |

Para comprobar la defensa del editor, **Validar SQL** debe aceptar
`SELECT nombre FROM clientes;` y rechazar `SELECT FROM clientes;`, `DELETE FROM clientes;` y
`SELECT * FROM clientes; DROP TABLE clientes;`.

La aplicación genera e inspecciona SQL; **Validar SQL** comprueba sintaxis MySQL, sentencia única y
solo lectura. No modifica la base ni ejecuta la consulta contra datos reales. En modo fixture muestra
una vista previa simulada claramente identificada.

## Rutas

| Ruta | Función |
|---|---|
| `/` | Laboratorio interactivo de esquema, pregunta y SQL |
| `/experimentos` | Protocolo baseline frente a QLoRA `r=16` y `r=32` |
| `/datos` | Estado verificable del dataset y control de fuga |
| `/metodologia` | Etapas reproducibles y contrato de entrega |

## Sistema visual

La interfaz usa una dirección de “instrumento de laboratorio de datos”: fondo técnico claro, tinta azul mineral, acentos cian/coral y panel de salida oscuro. El efecto interactivo del resultado se basa en el componente fuente [Spotlight Card de React Bits](https://reactbits.dev/components/spotlight-card), instalado dentro de `components/`; no llama un servicio externo ni participa en la generación de SQL.

Se incluyeron navegación activa, enlaces de salto, labels reales, feedback con `aria-live`, foco visible, diseño desde 360 px y soporte para `prefers-reduced-motion`.

## Archivos principales

```text
app/
├── page.tsx                 laboratorio y estados interactivos
├── experimentos/page.tsx   diseño experimental
├── datos/page.tsx           estado del dataset
├── metodologia/page.tsx    protocolo
└── globals.css              tokens, layout y responsive
components/
├── site-header.tsx          navegación accesible y estado activo
├── SpotlightCard.tsx        componente fuente de React Bits
└── SpotlightCard.css
lib/client.ts                cliente HTTP con fallback local
```

## Verificación

```powershell
pnpm typecheck
pnpm build
```

La última revisión también recorrió las cuatro rutas y el flujo generar/copiar en Chromium, tanto a `1440 × 1000` como a `390 × 844`, sin errores de consola.

## Frontera de seguridad

- La aplicación no modifica ni reemplaza `solucion.py`.
- No usa APIs externas de IA ni bases de datos administradas.
- La salida se describe como fixture o modelo local según corresponda.
- La página de experimentos y la de datos leen los JSON versionados mediante FastAPI.
- El adapter final se habilita únicamente si existen configuración y pesos no vacíos en `adapter/`.
