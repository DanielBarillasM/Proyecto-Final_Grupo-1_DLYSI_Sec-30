const backendUrl = (process.env.BACKEND_URL ?? 'http://127.0.0.1:8000').replace(/\/+$/, '')
const requestTimeoutMs = 610_000
const maxPostBytes = 64 * 1024

const allowedPaths = new Set([
  'health',
  'api/generate',
  'api/validate-sql',
  'api/results/summary',
  'api/results/dataset',
])

type ProxyContext = {
  params: Promise<{ path: string[] }>
}

export const dynamic = 'force-dynamic'
export const maxDuration = 620

function jsonError(status: number, detail: string): Response {
  return Response.json({ detail }, { status })
}

async function proxyRequest(request: Request, context: ProxyContext): Promise<Response> {
  const { path } = await context.params
  const pathname = path.join('/')
  if (!allowedPaths.has(pathname)) return jsonError(404, 'Ruta del backend no disponible.')

  const isPost = request.method === 'POST'
  if (isPost && pathname !== 'api/generate' && pathname !== 'api/validate-sql') {
    return jsonError(405, 'Método no permitido.')
  }

  const headers = new Headers({ Accept: 'application/json' })
  const requestInit: RequestInit = {
    method: request.method,
    headers,
    cache: 'no-store',
  }

  if (isPost) {
    const declaredLength = Number(request.headers.get('content-length') ?? '0')
    if (Number.isFinite(declaredLength) && declaredLength > maxPostBytes) {
      return jsonError(413, 'La solicitud excede el tamaño permitido.')
    }
    const body = await request.arrayBuffer()
    if (body.byteLength > maxPostBytes) {
      return jsonError(413, 'La solicitud excede el tamaño permitido.')
    }
    headers.set('Content-Type', 'application/json; charset=utf-8')
    requestInit.body = body
  }

  const controller = new AbortController()
  const abortFromCaller = () => controller.abort()
  request.signal.addEventListener('abort', abortFromCaller, { once: true })
  const timeout = setTimeout(() => controller.abort(), requestTimeoutMs)
  requestInit.signal = controller.signal

  try {
    const upstream = await fetch(`${backendUrl}/${pathname}`, requestInit)
    const responseHeaders = new Headers({
      'Cache-Control': 'no-store',
      'Content-Type': upstream.headers.get('content-type') ?? 'application/json; charset=utf-8',
    })
    const retryAfter = upstream.headers.get('retry-after')
    if (retryAfter) responseHeaders.set('Retry-After', retryAfter)
    return new Response(upstream.body, {
      status: upstream.status,
      headers: responseHeaders,
    })
  } catch (error) {
    if (controller.signal.aborted && !request.signal.aborted) {
      return jsonError(504, 'El backend excedió el límite de espera de 10 minutos.')
    }
    return jsonError(
      502,
      error instanceof Error && error.name === 'AbortError'
        ? 'La solicitud al backend fue cancelada.'
        : 'No se pudo conectar con el backend local.',
    )
  } finally {
    clearTimeout(timeout)
    request.signal.removeEventListener('abort', abortFromCaller)
  }
}

export function GET(request: Request, context: ProxyContext): Promise<Response> {
  return proxyRequest(request, context)
}

export function POST(request: Request, context: ProxyContext): Promise<Response> {
  return proxyRequest(request, context)
}
