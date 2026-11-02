from __future__ import annotations

SYSTEM_PROMPT = """Eres especialista en MySQL 8.4.10. Convierte una pregunta en español a SQL.
Responde exclusivamente con una consulta de solo lectura.
La salida debe comenzar con SELECT o WITH y contener una sola sentencia.
Usa únicamente tablas y columnas presentes en el esquema.
Respeta ONLY_FULL_GROUP_BY: toda columna no agregada debe aparecer en GROUP BY.
No incluyas Markdown, explicaciones, comentarios, DDL ni DML."""


def build_prompt(esquema: str, pregunta: str) -> str:
    return (
        f"{SYSTEM_PROMPT}\n\n"
        "<ESQUEMA_MYSQL>\n"
        f"{esquema.strip()}\n"
        "</ESQUEMA_MYSQL>\n\n"
        "<PREGUNTA>\n"
        f"{pregunta.strip()}\n"
        "</PREGUNTA>\n\n"
        "SQL:"
    )


def build_repair_prompt(esquema: str, pregunta: str, sql: str, error: str) -> str:
    return (
        f"{build_prompt(esquema, pregunta)}\n\n"
        "La consulta anterior produjo un error de MySQL. Corrígela sin cambiar la intención.\n"
        f"<SQL_ANTERIOR>\n{sql.strip()}\n</SQL_ANTERIOR>\n"
        f"<ERROR_MYSQL>\n{error.strip()[:1200]}\n</ERROR_MYSQL>\n\n"
        "SQL corregido:"
    )
