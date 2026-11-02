'use client'

import { useEffect } from 'react'
import { CircleAlert, RotateCcw } from 'lucide-react'

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('Error no controlado en la interfaz:', error)
  }, [error])

  return (
    <main className="shell error-page">
      <CircleAlert aria-hidden="true" />
      <p className="eyebrow">Error de interfaz</p>
      <h1>No se pudo mostrar esta sección.</h1>
      <p className="lede">Los datos del proyecto no fueron modificados. Puedes intentar reconstruir la vista.</p>
      <button className="primary" type="button" onClick={reset}>
        <RotateCcw aria-hidden="true" /> Reintentar
      </button>
    </main>
  )
}
