'use client'

import { useEffect, useState } from 'react'
import { DATASET_MANIFEST_FALLBACK, getDatasetManifest, type DatasetManifest } from '@/lib/client'

export function DatasetStatus() {
  const [manifest, setManifest] = useState<DatasetManifest>(DATASET_MANIFEST_FALLBACK)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()
    getDatasetManifest({ signal: controller.signal })
      .then((next) => next && setManifest(next))
      .catch(() => {
        if (!controller.signal.aborted) {
          setError('API no disponible; se muestra el manifiesto versionado del proyecto.')
        }
      })
    return () => controller.abort()
  }, [])

  return (
    <>
      {error && <p className="data-notice error-notice" role="alert">{error}</p>}
      <table className="status-table">
        <caption className="sr-only">Estado de las particiones del dataset</caption>
        <thead><tr><th>Partición</th><th>Esquemas</th><th>Ejemplos</th><th>Estado</th></tr></thead>
        <tbody>
          <tr><td>Entrenamiento</td><td>{manifest.training_schemas}</td><td>{manifest.training_accepted}</td><td>{manifest.mysql_validation_complete ? `Validado en MySQL ${manifest.mysql_version}` : 'No validado'}</td></tr>
          <tr><td>Validación propia</td><td>{manifest.validation_schemas}</td><td>{manifest.validation_examples}</td><td>Congelada</td></tr>
          <tr><td>Revisión humana</td><td>—</td><td>{manifest.assisted_review_rows}</td><td>{manifest.human_review_complete ? 'Confirmada por el equipo' : 'No confirmada'}</td></tr>
        </tbody>
      </table>
    </>
  )
}
