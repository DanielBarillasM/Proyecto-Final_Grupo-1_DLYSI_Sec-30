export type GenerationRequest = {
  esquema: string
  pregunta: string
  usar_adapter: boolean
}

export type ExecutionPreview = {
  ok: boolean
  columnas: string[]
  filas: unknown[][]
  error: string | null
}

export type GenerationResult = {
  sql: string
  source: 'fixture' | 'model'
  variant: 'baseline' | 'adapter'
  adapter_loaded: boolean
  attempts: number
  latency_ms: number
  execution: ExecutionPreview | null
  trace: string[]
}

export type ApiHealth = {
  status: 'ok'
  mode: 'fixture' | 'model'
  adapter_ready: boolean
  adapter_source: 'local' | 'huggingface' | 'missing'
  active_variant: 'base' | 'qlora' | null
  runtime_state: 'idle' | 'busy' | 'ready' | 'error'
}

export type SqlValidation = {
  valid: true
  sql: string
  dialect: 'mysql'
  read_only: true
}

export type ApiErrorKind = 'aborted' | 'connection' | 'http' | 'invalid' | 'timeout'

export class ApiClientError extends Error {
  constructor(
    message: string,
    public readonly kind: ApiErrorKind,
    public readonly status?: number,
  ) {
    super(message)
    this.name = 'ApiClientError'
  }
}

export type ExperimentMetric = {
  weighted_ex: number | null
  executable_rate?: number | null
  latency_p95_ms?: number | null
  trainable_parameters?: number | null
  training_minutes?: number | null
}

export type ProjectSummary = {
  status: string
  dataset: {
    training_pairs: number
    training_schemas: number
    validation_examples: number
    validation_schemas: number
    mysql_version: string
  }
  experiments: Record<string, ExperimentMetric>
  selected_adapter: string | null
  selection_reason?: string
  hidden_ex_prediction: number | null
  hidden_ex_prediction_interval?: [number, number]
  hidden_ex_prediction_method?: string
  note: string
}

export type DatasetManifest = {
  mysql_validation_complete: boolean
  training_accepted: number
  training_schemas: number
  validation_examples: number
  validation_schemas: number
  difficulty_validation: Record<string, number>
  human_review_complete: boolean
  assisted_review_complete: boolean
  assisted_review_rows: number
  mysql_version: string
}

export const PROJECT_SUMMARY_FALLBACK: ProjectSummary = {
  status: 'experiments_complete',
  dataset: {
    training_pairs: 2592,
    training_schemas: 12,
    validation_examples: 40,
    validation_schemas: 2,
    mysql_version: '8.4.10',
  },
  experiments: {
    baseline: { weighted_ex: 0.038461538461538464, executable_rate: 0.625, latency_p95_ms: 6656.3023 },
    qlora_r16: { weighted_ex: 0.9743589743589743, executable_rate: 0.975, latency_p95_ms: 15718.6631, trainable_parameters: 18464768, training_minutes: 120.68245 },
    qlora_r32: { weighted_ex: 0.9743589743589743, executable_rate: 0.975, latency_p95_ms: 13197.0874, trainable_parameters: 36929536, training_minutes: 133.42462 },
    direct: { weighted_ex: 0.9743589743589743 },
    repair: { weighted_ex: 0.9743589743589743 },
  },
  selected_adapter: 'qlora_r32',
  selection_reason: 'menor latencia p95 tras empate en EX y ejecutabilidad',
  hidden_ex_prediction: 0.874,
  hidden_ex_prediction_interval: [0.817, 0.9],
  hidden_ex_prediction_method: 'Bootstrap determinista de 20,000 remuestras por pregunta con semilla 2026 y ajuste conservador por cambio de dominio.',
  note: 'Métricas medidas localmente en RTX 4050 Laptop. La predicción oculta es una estimación, no una medición del conjunto oculto.',
}

export const DATASET_MANIFEST_FALLBACK: DatasetManifest = {
  mysql_validation_complete: true,
  training_accepted: 2592,
  training_schemas: 12,
  validation_examples: 40,
  validation_schemas: 2,
  difficulty_validation: { facil: 14, media: 14, dificil: 12 },
  human_review_complete: true,
  assisted_review_complete: true,
  assisted_review_rows: 100,
  mysql_version: '8.4.10',
}

type ApiGenerationResponse = {
  sql: string
  mode: 'fixture' | 'model'
  variante: 'base' | 'qlora'
  latency_ms: number
  execution: ExecutionPreview | null
  trace: string[]
}

type RequestOptions = { signal?: AbortSignal }

const API_URL = process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, '')

export const apiConfigured = Boolean(API_URL)

const FIXTURE_SQL = `SELECT c.nombre,
       ROUND(SUM(p.total), 2) AS total_completado
FROM clientes AS c
JOIN pedidos AS p ON p.cliente_id = c.id
WHERE p.estado = 'completado'
  AND p.fecha >= '2024-01-01'
  AND p.fecha < '2025-01-01'
GROUP BY c.id, c.nombre
ORDER BY total_completado DESC
LIMIT 1;`

function fixtureResult(request: GenerationRequest): GenerationResult {
  return {
    sql: FIXTURE_SQL,
    source: 'fixture',
    variant: request.usar_adapter ? 'adapter' : 'baseline',
    adapter_loaded: false,
    attempts: 0,
    latency_ms: 0,
    execution: {
      ok: true,
      columnas: ['nombre', 'total_completado'],
      filas: [['Ana López', '42890.50']],
      error: null,
    },
    trace: [
      `Fixture local seleccionado (${request.usar_adapter ? 'qlora' : 'base'})`,
      'Consulta marcada explícitamente como demostración',
      'Sin llamada a modelo ni servicio externo',
    ],
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

function isFiniteNumber(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value)
}

function isAbortError(error: unknown): boolean {
  return isRecord(error) && error.name === 'AbortError'
}

function validationMessages(detail: unknown): string[] {
  if (!Array.isArray(detail)) return []
  return detail.flatMap((item) => {
    if (!isRecord(item) || typeof item.msg !== 'string') return []
    const location = Array.isArray(item.loc)
      ? item.loc.filter((part): part is string | number => typeof part === 'string' || typeof part === 'number').join('.')
      : ''
    return `${location ? `${location}: ` : ''}${item.msg}`
  })
}

async function errorDetail(response: Response): Promise<string> {
  try {
    const payload: unknown = await response.json()
    if (isRecord(payload) && 'detail' in payload) {
      if (typeof payload.detail === 'string') return payload.detail
      const messages = validationMessages(payload.detail)
      if (messages.length) return messages.join(' · ')
    }
  } catch {
    // El estado HTTP basta cuando la respuesta no contiene JSON.
  }
  return `La API respondió ${response.status} ${response.statusText}`.trim()
}

async function apiJson<T>(
  path: string,
  init: RequestInit | undefined,
  validate: (payload: unknown) => payload is T,
): Promise<T> {
  if (!API_URL) throw new ApiClientError('La API local no está configurada.', 'connection')
  let response: Response
  try {
    response = await fetch(`${API_URL}${path}`, init)
  } catch (error) {
    if (isAbortError(error)) throw new ApiClientError('Solicitud cancelada.', 'aborted')
    throw new ApiClientError('No se pudo conectar con la API local en el puerto 8000.', 'connection')
  }
  if (!response.ok) throw new ApiClientError(await errorDetail(response), 'http', response.status)
  let payload: unknown
  try {
    payload = await response.json()
  } catch {
    throw new ApiClientError('La API devolvió una respuesta que no es JSON.', 'invalid')
  }
  if (!validate(payload)) throw new ApiClientError('La API devolvió datos incompletos o inválidos.', 'invalid')
  return payload
}

function isExecutionPreview(value: unknown): value is ExecutionPreview | null {
  if (value === null) return true
  return isRecord(value)
    && typeof value.ok === 'boolean'
    && Array.isArray(value.columnas)
    && value.columnas.every((column) => typeof column === 'string')
    && Array.isArray(value.filas)
    && value.filas.length <= 10
    && value.filas.every(Array.isArray)
    && (value.error === null || typeof value.error === 'string')
}

function isGenerationResponse(value: unknown): value is ApiGenerationResponse {
  return isRecord(value)
    && typeof value.sql === 'string'
    && value.sql.trim().length > 0
    && (value.mode === 'fixture' || value.mode === 'model')
    && (value.variante === 'base' || value.variante === 'qlora')
    && isFiniteNumber(value.latency_ms)
    && value.latency_ms >= 0
    && isExecutionPreview(value.execution)
    && Array.isArray(value.trace)
    && value.trace.every((step) => typeof step === 'string')
}

function isApiHealth(value: unknown): value is ApiHealth {
  return isRecord(value)
    && value.status === 'ok'
    && (value.mode === 'fixture' || value.mode === 'model')
    && typeof value.adapter_ready === 'boolean'
    && (value.adapter_source === 'local' || value.adapter_source === 'huggingface' || value.adapter_source === 'missing')
    && (value.active_variant === null || value.active_variant === 'base' || value.active_variant === 'qlora')
    && (value.runtime_state === 'idle' || value.runtime_state === 'busy' || value.runtime_state === 'ready' || value.runtime_state === 'error')
}

function isSqlValidation(value: unknown): value is SqlValidation {
  return isRecord(value)
    && value.valid === true
    && typeof value.sql === 'string'
    && value.sql.trim().length > 0
    && value.dialect === 'mysql'
    && value.read_only === true
}

function isProjectSummary(value: unknown): value is ProjectSummary {
  if (!isRecord(value) || !isRecord(value.dataset) || !isRecord(value.experiments)) return false
  const metricValid = (metric: unknown) => isRecord(metric)
    && (metric.weighted_ex === null || isFiniteNumber(metric.weighted_ex))
    && (metric.executable_rate === undefined || metric.executable_rate === null || isFiniteNumber(metric.executable_rate))
    && (metric.latency_p95_ms === undefined || metric.latency_p95_ms === null || isFiniteNumber(metric.latency_p95_ms))
    && (metric.trainable_parameters === undefined || metric.trainable_parameters === null || isFiniteNumber(metric.trainable_parameters))
    && (metric.training_minutes === undefined || metric.training_minutes === null || isFiniteNumber(metric.training_minutes))
  const intervalValid = value.hidden_ex_prediction_interval === undefined
    || (Array.isArray(value.hidden_ex_prediction_interval)
      && value.hidden_ex_prediction_interval.length === 2
      && value.hidden_ex_prediction_interval.every(isFiniteNumber))
  return typeof value.status === 'string'
    && isFiniteNumber(value.dataset.training_pairs)
    && isFiniteNumber(value.dataset.training_schemas)
    && isFiniteNumber(value.dataset.validation_examples)
    && isFiniteNumber(value.dataset.validation_schemas)
    && typeof value.dataset.mysql_version === 'string'
    && Object.values(value.experiments).every(metricValid)
    && (value.selected_adapter === null || typeof value.selected_adapter === 'string')
    && (value.selection_reason === undefined || typeof value.selection_reason === 'string')
    && (value.hidden_ex_prediction === null || isFiniteNumber(value.hidden_ex_prediction))
    && intervalValid
    && (value.hidden_ex_prediction_method === undefined || typeof value.hidden_ex_prediction_method === 'string')
    && typeof value.note === 'string'
}

function isDatasetManifest(value: unknown): value is DatasetManifest {
  return isRecord(value)
    && typeof value.mysql_validation_complete === 'boolean'
    && isFiniteNumber(value.training_accepted)
    && isFiniteNumber(value.training_schemas)
    && isFiniteNumber(value.validation_examples)
    && isFiniteNumber(value.validation_schemas)
    && isRecord(value.difficulty_validation)
    && Object.values(value.difficulty_validation).every(isFiniteNumber)
    && typeof value.human_review_complete === 'boolean'
    && typeof value.assisted_review_complete === 'boolean'
    && isFiniteNumber(value.assisted_review_rows)
    && typeof value.mysql_version === 'string'
}

function readOptions(signal?: AbortSignal): RequestInit {
  return signal ? { cache: 'no-store', signal } : { cache: 'no-store' }
}

export async function getApiHealth(options: RequestOptions = {}): Promise<ApiHealth | null> {
  if (!API_URL) return null
  return apiJson<ApiHealth>('/health', readOptions(options.signal), isApiHealth)
}

export async function getProjectSummary(options: RequestOptions = {}): Promise<ProjectSummary | null> {
  if (!API_URL) return null
  return apiJson<ProjectSummary>('/api/results/summary', readOptions(options.signal), isProjectSummary)
}

export async function getDatasetManifest(options: RequestOptions = {}): Promise<DatasetManifest | null> {
  if (!API_URL) return null
  return apiJson<DatasetManifest>('/api/results/dataset', readOptions(options.signal), isDatasetManifest)
}

export async function validateSql(sql: string, options: RequestOptions = {}): Promise<SqlValidation> {
  if (!API_URL) throw new ApiClientError('La API local no está configurada.', 'connection')
  return apiJson<SqlValidation>('/api/validate-sql', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sql }),
    ...(options.signal ? { signal: options.signal } : {}),
  }, isSqlValidation)
}

export async function generateSql(request: GenerationRequest, options: RequestOptions = {}): Promise<GenerationResult> {
  if (!API_URL) return fixtureResult(request)

  const controller = new AbortController()
  let timedOut = false
  const abortFromCaller = () => controller.abort()
  if (options.signal?.aborted) controller.abort()
  else options.signal?.addEventListener('abort', abortFromCaller, { once: true })
  // En Windows, la primera carga cuantizada puede tardar más de cinco minutos.
  const timeout = window.setTimeout(() => {
    timedOut = true
    controller.abort()
  }, 600_000)
  try {
    const payload = await apiJson<ApiGenerationResponse>('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        esquema: request.esquema,
        pregunta: request.pregunta,
        variante: request.usar_adapter ? 'qlora' : 'base',
      }),
      signal: controller.signal,
    }, isGenerationResponse)
    return {
      sql: payload.sql,
      source: payload.mode,
      variant: payload.variante === 'qlora' ? 'adapter' : 'baseline',
      adapter_loaded: payload.mode === 'model' && payload.variante === 'qlora',
      attempts: payload.mode === 'model' ? 1 : 0,
      latency_ms: payload.latency_ms,
      execution: payload.execution,
      trace: payload.trace,
    }
  } catch (error) {
    if (error instanceof ApiClientError && error.kind === 'aborted') {
      if (timedOut) throw new ApiClientError('La generación excedió el límite de 10 minutos.', 'timeout')
      throw new ApiClientError('Solicitud cancelada.', 'aborted')
    }
    throw error
  } finally {
    window.clearTimeout(timeout)
    options.signal?.removeEventListener('abort', abortFromCaller)
  }
}
