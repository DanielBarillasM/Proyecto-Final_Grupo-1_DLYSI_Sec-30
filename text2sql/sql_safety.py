from __future__ import annotations

import re


class UnsafeSQL(ValueError):
    """La salida no cumple el contrato de una consulta de solo lectura."""


_FENCE = re.compile(r"```(?:sql|mysql)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)
_PREFIX = re.compile(r"^\s*(?:sql\s*:|consulta\s*:)", re.IGNORECASE)
_START = re.compile(r"\b(?:SELECT|WITH)\b", re.IGNORECASE)
_FORBIDDEN = re.compile(
    r"\b(?:INSERT|UPDATE|DELETE|REPLACE|CREATE|ALTER|DROP|TRUNCATE|CALL|"
    r"GRANT|REVOKE|LOAD|HANDLER|LOCK|UNLOCK|SET|USE|INTO\s+OUTFILE|"
    r"INTO\s+DUMPFILE)\b",
    re.IGNORECASE,
)


def clean_model_output(raw: str) -> str:
    text = raw.strip()
    fenced = _FENCE.search(text)
    if fenced:
        text = fenced.group(1).strip()
    text = _PREFIX.sub("", text).strip()
    start = _START.search(text)
    if not start:
        raise UnsafeSQL("La salida no contiene SELECT ni WITH.")
    text = text[start.start() :].strip()

    # El punto y coma final es válido; cualquier contenido posterior no lo es.
    parts = [part.strip() for part in text.split(";") if part.strip()]
    if len(parts) != 1:
        raise UnsafeSQL("La salida contiene múltiples sentencias.")
    return f"{parts[0]};"


def validate_read_only_sql(sql: str) -> str:
    if _FORBIDDEN.search(sql):
        raise UnsafeSQL("La consulta contiene una operación no permitida.")
    candidate = clean_model_output(sql)

    try:
        import sqlglot
        from sqlglot import exp
    except ImportError:
        return candidate

    try:
        statements = sqlglot.parse(candidate, read="mysql")
    except Exception as exc:
        raise UnsafeSQL("La consulta no tiene sintaxis MySQL válida.") from exc
    if len(statements) != 1:
        raise UnsafeSQL("Se esperaba exactamente una sentencia SQL.")
    tree = statements[0]
    if not isinstance(tree, (exp.Select, exp.Union, exp.Intersect, exp.Except)):
        raise UnsafeSQL("La raíz de la consulta no es SELECT o WITH ... SELECT.")
    if any(not select.expressions for select in tree.find_all(exp.Select)):
        raise UnsafeSQL("Cada SELECT debe incluir al menos una columna o expresión.")

    forbidden_nodes = tuple(
        node
        for name in ("Insert", "Update", "Delete", "Create", "Drop", "Alter", "Merge", "Command")
        if (node := getattr(exp, name, None)) is not None
    )
    if forbidden_nodes and any(isinstance(node, forbidden_nodes) for node in tree.walk()):
        raise UnsafeSQL("El AST contiene una operación de escritura.")
    return candidate
