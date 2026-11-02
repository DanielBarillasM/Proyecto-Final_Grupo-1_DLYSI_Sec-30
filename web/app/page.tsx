'use client'

import Link from 'next/link'
import { useEffect, useRef, useState } from 'react'
import {
  ArrowRight,
  Check,
  CircleAlert,
  Clipboard,
  Code2,
  Database,
  LoaderCircle,
  Play,
  RotateCcw,
  ShieldCheck,
  Workflow,
  X,
} from 'lucide-react'
import SpotlightCard from '@/components/SpotlightCard'
import { SiteHeader } from '@/components/site-header'
import {
  apiConfigured,
  ApiClientError,
  generateSql,
  getApiHealth,
  getProjectSummary,
  PROJECT_SUMMARY_FALLBACK,
  validateSql,
  type ApiHealth,
  type GenerationResult,
  type ProjectSummary,
} from '@/lib/client'

const initialSchema = `CREATE TABLE clientes (
  id INT PRIMARY KEY,
  nombre VARCHAR(120),
  ciudad VARCHAR(80)
);

CREATE TABLE pedidos (
  id INT PRIMARY KEY,
  cliente_id INT,
  total DECIMAL(10,2),
  estado VARCHAR(20),
  fecha DATE,
  FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);`

const initialQuestion = '¿Qué cliente tuvo el mayor total de pedidos completados durante 2024?'

export default function Page() {
  const [schema, setSchema] = useState(initialSchema)
  const [question, setQuestion] = useState(initialQuestion)
  const [variant, setVariant] = useState<'baseline' | 'adapter'>('baseline')
  const [result, setResult] = useState<GenerationResult | null>(null)
  const [sqlDraft, setSqlDraft] = useState('')
  const [draftValidated, setDraftValidated] = useState(false)
  const [busy, setBusy] = useState(false)
  const [validating, setValidating] = useState(false)
  const [message, setMessage] = useState('Listo para generar.')
  const [messageKind, setMessageKind] = useState<'error' | 'info' | 'success'>('info')
  const [health, setHealth] = useState<ApiHealth | null>(null)
  const [summary, setSummary] = useState<ProjectSummary>(PROJECT_SUMMARY_FALLBACK)
  const [apiError, setApiError] = useState(false)
  const requestRef = useRef<AbortController | null>(null)
  const requestSequence = useRef(0)
  const sqlRef = useRef<HTMLTextAreaElement | null>(null)

  useEffect(() => {
    if (!apiConfigured) return
    const controller = new AbortController()
    Promise.allSettled([
      getApiHealth({ signal: controller.signal }),
      getProjectSummary({ signal: controller.signal }),
    ]).then(([healthResult, summaryResult]) => {
      if (controller.signal.aborted) return
      if (healthResult.status === 'fulfilled') setHealth(healthResult.value)
      else setApiError(true)
      if (summaryResult.status === 'fulfilled' && summaryResult.value) setSummary(summaryResult.value)
    })
    return () => controller.abort()
  }, [])

  useEffect(() => () => {
    requestSequence.current += 1
    requestRef.current?.abort()
    requestRef.current = null
  }, [])

  function refreshHealth(expectedSequence = requestSequence.current) {
    if (!apiConfigured) return
    void getApiHealth()
      .then((nextHealth) => {
        if (requestSequence.current === expectedSequence) {
          setHealth(nextHealth)
          setApiError(false)
        }
      })
      .catch(() => {
        if (requestSequence.current === expectedSequence) setApiError(true)
      })
  }

  async function run() {
    const cleanSchema = schema.trim()
    const cleanQuestion = question.trim()
    if (cleanSchema.length < 20 || !cleanSchema.toUpperCase().includes('CREATE TABLE')) {
      setMessageKind('error')
      setMessage('Incluye un esquema válido con al menos una sentencia CREATE TABLE.')
      return
    }
    if (cleanQuestion.length < 3) {
      setMessageKind('error')
      setMessage('Escribe una pregunta de al menos 3 caracteres.')
      return
    }

    requestRef.current?.abort()
    const controller = new AbortController()
    requestRef.current = controller
    const requestId = ++requestSequence.current
    setBusy(true)
    if (health?.mode === 'model') {
      setHealth({
        ...health,
        active_variant: variant === 'adapter' ? 'qlora' : 'base',
        runtime_state: 'busy',
      })
    }
    setMessageKind('info')
    setMessage('Cargando la variante y generando… La primera ejecución puede tardar varios minutos.')
    try {
      const next = await generateSql({
        esquema: cleanSchema,
        pregunta: cleanQuestion,
        usar_adapter: variant === 'adapter',
      }, { signal: controller.signal })
      if (requestSequence.current !== requestId) return
      setResult(next)
      setSqlDraft(next.sql)
      setDraftValidated(true)
      setApiError(false)
      setMessageKind('success')
      setMessage(
        next.source === 'fixture'
          ? 'Fixture local generado. Conecta la API para usar el modelo.'
          : 'Consulta generada por la API local.',
      )
    } catch (error) {
      if (requestSequence.current !== requestId) return
      if (error instanceof ApiClientError && error.kind === 'aborted') {
        setMessageKind('info')
        setMessage('Solicitud cancelada. El backend puede terminar de liberar la generación actual.')
        return
      }
      if (error instanceof ApiClientError && error.kind === 'connection') setApiError(true)
      setMessageKind('error')
      setMessage(error instanceof Error ? error.message : 'No fue posible generar la consulta.')
    } finally {
      if (requestSequence.current === requestId) {
        requestRef.current = null
        setBusy(false)
        refreshHealth(requestId)
      }
    }
  }

  function cancelGeneration() {
    if (!requestRef.current) return
    requestSequence.current += 1
    requestRef.current.abort()
    requestRef.current = null
    setBusy(false)
    setMessageKind('info')
    setMessage('Espera cancelada. El backend puede completar la operación antes de aceptar otra.')
    refreshHealth(requestSequence.current)
  }

  function reset() {
    cancelGeneration()
    setSchema(initialSchema)
    setQuestion(initialQuestion)
    setVariant('baseline')
    setResult(null)
    setSqlDraft('')
    setDraftValidated(false)
    setMessageKind('info')
    setMessage('Formulario restablecido.')
  }

  async function copySql() {
    if (!sqlDraft) return
    let copied = false
    try {
      if (window.isSecureContext && navigator.clipboard) {
        await navigator.clipboard.writeText(sqlDraft)
        copied = true
      }
    } catch {
      copied = false
    }
    if (!copied && sqlRef.current) {
      const field = sqlRef.current
      const selectionStart = field.selectionStart
      const selectionEnd = field.selectionEnd
      field.focus()
      field.select()
      try {
        copied = document.execCommand('copy')
      } catch {
        copied = false
      }
      if (copied) field.setSelectionRange(selectionStart, selectionEnd)
    }
    if (copied) {
      setMessageKind('success')
      setMessage('SQL copiado al portapapeles.')
    } else {
      setMessageKind('error')
      setMessage('El navegador bloqueó el portapapeles. El SQL quedó seleccionado para copiarlo con Ctrl+C.')
    }
  }

  async function validateDraft() {
    const candidate = sqlDraft.trim()
    if (!candidate || validating) return
    setValidating(true)
    setMessageKind('info')
    setMessage('Validando sintaxis MySQL y operaciones de solo lectura…')
    try {
      const validation = await validateSql(candidate)
      setSqlDraft(validation.sql)
      setDraftValidated(true)
      setApiError(false)
      setMessageKind('success')
      setMessage('SQL válido para MySQL y restringido a solo lectura.')
    } catch (error) {
      setDraftValidated(false)
      if (error instanceof ApiClientError && error.kind === 'connection') setApiError(true)
      setMessageKind('error')
      setMessage(error instanceof Error ? error.message : 'No fue posible validar el SQL.')
    } finally {
      setValidating(false)
    }
  }

  return (
    <>
      <a className="skip-link" href="#contenido">Saltar al contenido</a>
      <SiteHeader />
      <main id="contenido" className="shell">
        <section className="hero" aria-labelledby="hero-title">
          <div className="hero-copy">
            <p className="context-line"><span aria-hidden="true" /> Laboratorio reproducible · MySQL 8.4</p>
            <h1 id="hero-title">Pregunta en español.<br /><span>SQL verificable.</span></h1>
            <p className="lede">Una mesa de trabajo para inspeccionar el esquema, comparar el baseline con QLoRA y auditar cada consulta antes de ejecutarla.</p>
            <div className="hero-actions">
              <a className="primary-link" href="#laboratorio">Abrir laboratorio <ArrowRight aria-hidden="true" /></a>
              <Link className="text-link" href="/metodologia">Revisar metodología</Link>
            </div>
          </div>

          <aside className="pipeline" aria-label="Flujo del sistema de Texto a SQL">
            <div className="pipeline-bar"><span>pipeline_03</span><span className="run-state"><i aria-hidden="true" /> READY</span></div>
            <div className="pipeline-inputs">
              <div><Database aria-hidden="true" /><span>Schema</span><strong>2 tablas</strong></div>
              <div><Workflow aria-hidden="true" /><span>Pregunta</span><strong>ES natural</strong></div>
            </div>
            <div className="pipeline-route" aria-hidden="true"><span /><i>modelo</i><span /></div>
            <div className="pipeline-code">
              <p><span>SELECT</span> c.nombre, <span>SUM</span>(p.total)</p>
              <p><span>FROM</span> clientes c <span>JOIN</span> pedidos p</p>
              <p><span>ORDER BY</span> 2 <span>DESC LIMIT</span> 1;</p>
            </div>
            <div className="pipeline-foot"><ShieldCheck aria-hidden="true" /> Lectura segura · salida inspeccionable</div>
          </aside>
        </section>

        <section id="laboratorio" className="workspace" aria-labelledby="lab-title">
          <header className="workspace-header">
            <div>
              <p className="section-kicker">Consola interactiva</p>
              <h2 id="lab-title">Banco de pruebas</h2>
            </div>
            <span className={`system-status ${apiError ? 'status-error' : ''}`}>
              <i aria-hidden="true" />
              {!apiConfigured ? 'Modo demostración · API no configurada' : apiError ? 'API local desconectada' : health ? `API ${health.mode} · ${health.runtime_state === 'busy' ? 'modelo ocupado' : health.runtime_state === 'error' ? 'modelo con error' : health.active_variant ? `activo ${health.active_variant}` : 'modelo en espera'} · adapter ${health.adapter_source === 'local' ? 'local' : health.adapter_source === 'huggingface' ? 'Hugging Face' : 'no disponible'}` : 'Conectando con la API…'}
            </span>
          </header>

          <div className="workspace-grid">
            <section className="input-panel" aria-labelledby="input-title">
              <div className="panel-heading"><span>01</span><div><p>Entrada</p><h3 id="input-title">Define el contexto</h3></div></div>

              <label htmlFor="schema">Esquema MySQL <small>DDL de referencia</small></label>
              <textarea id="schema" name="schema" minLength={20} maxLength={50000} spellCheck={false} value={schema} onChange={(event) => setSchema(event.target.value)} aria-describedby="schema-count" />
              <small id="schema-count" className="field-count">{schema.length.toLocaleString('es-GT')} / 50,000</small>

              <label htmlFor="question">Pregunta <small>Lenguaje natural</small></label>
              <textarea id="question" name="question" className="question" minLength={3} maxLength={1000} value={question} onChange={(event) => setQuestion(event.target.value)} onKeyDown={(event) => { if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') { event.preventDefault(); void run() } }} aria-describedby="question-count question-shortcut" />
              <span className="field-meta"><small id="question-shortcut">Ctrl/⌘ + Enter para generar</small><small id="question-count">{question.length.toLocaleString('es-GT')} / 1,000</small></span>

              <fieldset>
                <legend>Variante del modelo</legend>
                <div className="segment-control" role="group" aria-label="Variante del modelo">
                  <button type="button" aria-pressed={variant === 'baseline'} disabled={busy} className={variant === 'baseline' ? 'selected' : ''} onClick={() => { setVariant('baseline'); setMessageKind('info'); setMessage('Baseline seleccionado.') }}>
                    Baseline
                  </button>
                  <button type="button" aria-pressed={variant === 'adapter'} disabled={busy} className={variant === 'adapter' ? 'selected' : ''} onClick={() => { setVariant('adapter'); setMessageKind('info'); setMessage('Adapter QLoRA seleccionado.') }}>
                    Adapter QLoRA
                  </button>
                </div>
              </fieldset>

              <div className="actions">
                <button className="primary" type="button" onClick={() => void run()} disabled={busy}>
                  {busy ? <LoaderCircle className="spin" aria-hidden="true" /> : <Play aria-hidden="true" />} {busy ? 'Generando…' : result ? 'Regenerar SQL' : 'Generar SQL'}
                </button>
                {busy && <button className="secondary" type="button" onClick={cancelGeneration}><X aria-hidden="true" /> Cancelar espera</button>}
                <button className="secondary" type="button" onClick={reset}><RotateCcw aria-hidden="true" /> Reiniciar</button>
              </div>
            </section>

            <SpotlightCard
              className="result-card"
              theme="dark"
              spotlightColor="#78dce8"
              intensity={0.2}
              spotlightSize={380}
              softness={0.8}
              borderGlow={0.75}
              smoothing={0.2}
              flare={false}
              grain={0.025}
              aria-labelledby="output-title"
              aria-busy={busy}
            >
              <div className="panel-heading output-heading"><span>02</span><div><p>Resultado</p><h3 id="output-title">SQL inspeccionable</h3></div></div>
              <div className="output-meta"><span className={`safe-pill ${sqlDraft && !draftValidated ? 'edited-pill' : ''}`}><ShieldCheck aria-hidden="true" /> {!sqlDraft ? 'Sin generar' : draftValidated ? 'Solo lectura validada' : 'Editada · sin validar'}</span><span>Editor habilitado · MySQL 8.4.10</span></div>
              <label className="sr-only" htmlFor="sql-result">Consulta SQL generada y editable</label>
              <textarea ref={sqlRef} id="sql-result" className="sql-output sql-editor" maxLength={50000} spellCheck={false} value={sqlDraft} placeholder="-- Genera una consulta para ver y editar el resultado." onChange={(event) => { setSqlDraft(event.target.value); setDraftValidated(false) }} />
              <div className="output-actions">
                <button className="copy" type="button" disabled={!sqlDraft} onClick={() => void copySql()}><Clipboard aria-hidden="true" /> Copiar SQL</button>
                <button className="copy" type="button" disabled={!sqlDraft || validating} onClick={() => void validateDraft()}>{validating ? <LoaderCircle className="spin" aria-hidden="true" /> : <ShieldCheck aria-hidden="true" />} {validating ? 'Validando…' : 'Validar SQL'}</button>
                <button className="copy" type="button" disabled={!result || sqlDraft === result.sql} onClick={() => { if (!result) return; setSqlDraft(result.sql); setDraftValidated(true); setMessageKind('info'); setMessage('Se restauró la consulta generada.') }}><RotateCcw aria-hidden="true" /> Restaurar generado</button>
              </div>

              <div className="trace">
                <h4>Traza de ejecución</h4>
                <dl>
                  <div><dt>Fuente</dt><dd>{result?.source ?? '—'}</dd></div>
                  <div><dt>Variante</dt><dd>{result ? (result.variant === 'adapter' ? 'QLoRA' : 'Baseline') : '—'}</dd></div>
                  <div><dt>Intentos</dt><dd className="numeric">{result?.attempts ?? '—'}</dd></div>
                  <div><dt>Latencia</dt><dd className="numeric">{result ? `${result.latency_ms} ms` : '—'}</dd></div>
                </dl>
                {result?.trace.length ? <ol className="trace-steps">{result.trace.map((step) => <li key={step}>{step}</li>)}</ol> : null}
              </div>
              {result?.execution && (
                <div className="execution-preview">
                  <h4>Vista previa de ejecución</h4>
                  {result.execution.error ? <p role="alert">{result.execution.error}</p> : (
                    <div className="table-scroll"><table><thead><tr>{result.execution.columnas.map((column) => <th key={column}>{column}</th>)}</tr></thead><tbody>{result.execution.filas.map((row, rowIndex) => <tr key={rowIndex}>{row.map((value, cellIndex) => <td key={`${rowIndex}-${cellIndex}`}>{String(value ?? 'NULL')}</td>)}</tr>)}</tbody></table></div>
                  )}
                </div>
              )}
              <p className={`live live-${messageKind}`} role={messageKind === 'error' ? 'alert' : 'status'} aria-live={messageKind === 'error' ? 'assertive' : 'polite'}>
                {messageKind === 'error' ? <CircleAlert aria-hidden="true" /> : busy ? <LoaderCircle className="spin" aria-hidden="true" /> : <Check aria-hidden="true" />} {message}
              </p>
            </SpotlightCard>
          </div>
        </section>

        <section className="facts" aria-labelledby="facts-title">
          <div className="facts-intro"><p className="section-kicker">Base experimental</p><h2 id="facts-title">Evidencia antes que promesas.</h2><p>Los números publicados se leen de artefactos versionados y corresponden a las corridas locales completadas.</p></div>
          <dl>
            <div><dt>Pares aceptados</dt><dd>2,592</dd><span>Entrenamiento</span></div>
            <div><dt>Esquemas</dt><dd>12</dd><span>Sin fuga</span></div>
            <div><dt>Validación</dt><dd>40</dd><span>Casos congelados</span></div>
            <div><dt>EX del modelo</dt><dd>{`${((summary.experiments.direct?.weighted_ex ?? 0) * 100).toFixed(1)}%`}</dd><span>{summary.selected_adapter}</span></div>
          </dl>
        </section>

        <section className="principle-band" aria-label="Principios del proyecto">
          <Code2 aria-hidden="true" />
          <p><strong>Un contrato simple:</strong> una pregunta, una sentencia <code>SELECT</code> o <code>WITH</code>, y evidencia suficiente para repetir el resultado.</p>
          <Link href="/datos">Explorar los datos <ArrowRight aria-hidden="true" /></Link>
        </section>
      </main>
    </>
  )
}
