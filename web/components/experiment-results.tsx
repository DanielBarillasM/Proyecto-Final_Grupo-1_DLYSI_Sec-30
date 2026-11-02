'use client'

import { useEffect, useState } from 'react'
import { getProjectSummary, PROJECT_SUMMARY_FALLBACK, type ProjectSummary } from '@/lib/client'

function percent(value: number | null | undefined) {
  return value == null ? 'No disponible' : `${(value * 100).toFixed(1)}%`
}

export function ExperimentResults() {
  const [summary, setSummary] = useState<ProjectSummary>(PROJECT_SUMMARY_FALLBACK)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()
    getProjectSummary({ signal: controller.signal })
      .then((next) => next && setSummary(next))
      .catch(() => {
        if (!controller.signal.aborted) {
          setError('API no disponible; se muestran los resultados versionados del proyecto.')
        }
      })
    return () => controller.abort()
  }, [])

  const baseline = summary?.experiments.baseline
  const r16 = summary?.experiments.qlora_r16
  const r32 = summary?.experiments.qlora_r32

  return (
    <>
      {error && <p className="data-notice error-notice" role="alert">{error}</p>}
      <section className="content-grid" aria-label="Configuraciones experimentales">
        <article className="content-card"><h2>Baseline</h2><p>Qwen2.5-Coder-1.5B-Instruct sin adapter.</p><strong>{percent(baseline?.weighted_ex)} EX</strong></article>
        <article className="content-card"><h2>QLoRA r=16</h2><p>Configuración A; alpha 32 y dropout 0.05.</p><strong>{percent(r16?.weighted_ex)} EX</strong>{r16?.training_minutes != null && <p>{r16.training_minutes.toFixed(1)} min de entrenamiento.</p>}</article>
        <article className="content-card"><h2>QLoRA r=32</h2><p>Configuración B; únicamente cambia el rango.</p><strong>{percent(r32?.weighted_ex)} EX</strong>{r32?.training_minutes != null && <p>{r32.training_minutes.toFixed(1)} min de entrenamiento.</p>}</article>
        <article className="content-card wide"><h2>Criterio de selección</h2><p>EX ponderada, EX difícil, ejecutabilidad y latencia p95.</p><strong>Ganador: {summary.selected_adapter}</strong>{summary.selection_reason && <p>{summary.selection_reason}.</p>}</article>
        <article className="content-card"><h2>Inferencia</h2><p>Directa: {percent(summary?.experiments.direct?.weighted_ex)} EX.<br />Reparación: {percent(summary?.experiments.repair?.weighted_ex)} EX.</p><strong>{summary?.experiments.direct?.weighted_ex === summary?.experiments.repair?.weighted_ex ? 'Sin mejora por reparación' : 'Comparación completada'}</strong></article>
        <article className="content-card"><h2>Predicción oculta</h2><p>{percent(summary?.hidden_ex_prediction)} estimado{summary?.hidden_ex_prediction_interval ? `; intervalo ${percent(summary.hidden_ex_prediction_interval[0])} a ${percent(summary.hidden_ex_prediction_interval[1])}` : ''}.</p><strong>No es una medición</strong></article>
      </section>
    </>
  )
}
