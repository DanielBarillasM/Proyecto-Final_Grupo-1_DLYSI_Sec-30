# Verificación técnica local del 5 de noviembre de 2026

## Entorno

- Repositorio: `Proyecto-Final_Grupo-1_DLYSI_Sec-30`
- Rama: `main`
- Sistema: Windows
- Zona horaria del proyecto: America/Guatemala

## Resultados

| Control | Resultado |
|---|---|
| `pytest -q` | 43 pruebas aprobadas |
| Ruff sobre runtime, backend, pruebas y scripts finales | Sin errores |
| `pnpm --dir web build` | Compilación y TypeScript aprobados |
| Rutas web generadas | `/`, `/datos`, `/experimentos`, `/metodologia` y proxy dinámico |
| `scripts/build_space_bundle.py` | 16 archivos generados |
| `scripts/audit_final.py --handoff` | Aprobado |
| `scripts/audit_final.py --final` | Pendiente solo de URL/capturas y registro externo |

La verificación no abrió una URL pública ni fabricó evidencia de producción. El resultado final se
completa únicamente después de ejecutar la demostración desde otra sesión.
