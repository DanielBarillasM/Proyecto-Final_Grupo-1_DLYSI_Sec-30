import type { Metadata } from 'next'
import { DatasetStatus } from '@/components/dataset-status'
import { SiteHeader } from '@/components/site-header'

export const metadata: Metadata = { title: 'Datos' }

export default function Datos() {
  return (
    <>
      <a className="skip-link" href="#contenido">Saltar al contenido</a>
      <SiteHeader />
      <main id="contenido" className="shell">
        <header className="page-intro">
          <p className="eyebrow">Dataset auditable</p>
          <h1>Separación por esquema.<br /><span>Cero fuga.</span></h1>
          <p className="lede">Los pares fueron generados de forma determinista y ejecutados contra MySQL 8.4.10. Aerolínea y eventos permanecen fuera del entrenamiento.</p>
        </header>
        <DatasetStatus />
        <section className="content-grid supporting-grid" aria-label="Controles del dataset">
          <article className="content-card"><h2>Dificultad</h2><p>14 fáciles · 14 medias · 12 difíciles.</p></article>
          <article className="content-card"><h2>Control de fuga</h2><p>Los identificadores de esquema de entrenamiento y validación son disjuntos.</p></article>
          <article className="content-card"><h2>Trazabilidad</h2><p>El manifiesto contiene hashes SHA-256, versión del motor y modo SQL.</p></article>
        </section>
      </main>
    </>
  )
}
