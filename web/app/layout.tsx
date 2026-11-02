import type { Metadata, Viewport } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: { default: 'Text-to-SQL · Grupo 1', template: '%s · Text-to-SQL' },
  description: 'Laboratorio reproducible para traducir preguntas en español a SQL de MySQL.',
  icons: { icon: '/icon.svg' },
}

export const viewport: Viewport = { colorScheme: 'light', themeColor: '#eaf0f3' }

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="es" data-scroll-behavior="smooth"><body>{children}</body></html>
}
