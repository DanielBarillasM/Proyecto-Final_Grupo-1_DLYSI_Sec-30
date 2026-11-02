'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Braces } from 'lucide-react'

const links = [
  ['/', 'Laboratorio'],
  ['/experimentos', 'Experimentos'],
  ['/datos', 'Datos'],
  ['/metodologia', 'Metodología'],
] as const

export function SiteHeader() {
  const pathname = usePathname()

  return (
    <header className="site-header">
      <div className="nav-shell">
        <Link className="brand" href="/" aria-label="Text-to-SQL, ir al laboratorio">
          <span><Braces aria-hidden="true" /></span>
          <span className="brand-copy"><strong>Text→SQL</strong><small>DL LAB · 03</small></span>
        </Link>
        <nav aria-label="Navegación principal">
          {links.map(([href, label]) => {
            const active = pathname === href
            return <Link href={href} key={href} className={active ? 'active' : undefined} aria-current={active ? 'page' : undefined}>{label}</Link>
          })}
        </nav>
        <span className="project-mark"><i aria-hidden="true" /> UVG · Grupo 1</span>
      </div>
    </header>
  )
}
