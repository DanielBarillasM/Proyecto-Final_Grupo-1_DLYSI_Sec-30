import type { Metadata } from 'next'
import { ExperimentResults } from '@/components/experiment-results'
import { SiteHeader } from '@/components/site-header'

export const metadata: Metadata = { title: 'Experimentos' }

export default function Experimentos() {
  return (
    <>
      <a className="skip-link" href="#contenido">Saltar al contenido</a>
      <SiteHeader />
      <main id="contenido" className="shell">
        <header className="page-intro">
          <p className="eyebrow">Diseño experimental</p>
          <h1>Dos rangos LoRA.<br /><span>Una sola variable.</span></h1>
          <p className="lede">El baseline y ambas configuraciones usan el mismo prompt, semilla y conjunto de validación. Los valores se leen del backend local y la selección se realiza por exactitud de ejecución ponderada.</p>
        </header>
        <ExperimentResults />
      </main>
    </>
  )
}
