import type { Metadata } from 'next'
import { SiteHeader } from '@/components/site-header'

export const metadata: Metadata = { title: 'Metodología' }

export default function Metodologia() {
  return (
    <>
      <a className="skip-link" href="#contenido">Saltar al contenido</a>
      <SiteHeader />
      <main id="contenido" className="shell">
        <header className="page-intro">
          <p className="eyebrow">Protocolo reproducible</p>
          <h1>Del dato al adapter.<br /><span>Sin saltos ocultos.</span></h1>
          <p className="lede">Cada etapa deja archivos verificables y comandos repetibles. La aplicación es una demostración; la evaluación oficial entra únicamente por <code>solucion.py</code>.</p>
        </header>
        <section className="content-grid" aria-label="Etapas metodológicas">
          <article className="content-card"><h2>01 · Preparar</h2><p>Generar, deduplicar y ejecutar todos los SQL. Congelar validación antes de entrenar.</p></article>
          <article className="content-card"><h2>02 · Entrenar</h2><p>Ejecutar pruebas rápidas y dos corridas QLoRA secuenciales en la GPU CUDA local con semilla 2026.</p></article>
          <article className="content-card"><h2>03 · Evaluar</h2><p>Comparar resultados normalizados y clasificar cada fallo.</p></article>
          <article className="content-card"><h2>04 · Seleccionar</h2><p>Copiar el ganador a <code>adapter/</code> y activar <code>usar_adapter</code>.</p></article>
          <article className="content-card"><h2>05 · Auditar</h2><p>Ejecutar pruebas, compilar entregables y repetir desde un entorno limpio.</p></article>
          <article className="content-card"><h2>Contrato</h2><p>Una sola sentencia <code>SELECT</code> o <code>WITH</code>; sin DDL, DML ni servicios externos.</p></article>
        </section>
      </main>
    </>
  )
}
