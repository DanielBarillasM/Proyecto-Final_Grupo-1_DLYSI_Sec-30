import Link from 'next/link'

export default function NotFound() {
  return (
    <main className="shell error-page">
      <p className="eyebrow">404 · Ruta inexistente</p>
      <h1>Esta página no forma parte del laboratorio.</h1>
      <p className="lede">Vuelve a la consola para generar o inspeccionar una consulta SQL.</p>
      <Link className="primary-link" href="/">Volver al laboratorio</Link>
    </main>
  )
}
