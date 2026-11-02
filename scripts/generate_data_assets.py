from __future__ import annotations

import csv
import hashlib
import json
import random
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_ROOT = ROOT / "datos" / "esquemas"
TRAIN_PATH = ROOT / "datos" / "entrenamiento" / "candidatos.jsonl"
VALIDATION_PATH = ROOT / "datos" / "validacion" / "preguntas.jsonl"
VALIDATION_CSV = ROOT / "resultados" / "validacion_propia.csv"
REVIEW_PATH = ROOT / "datos" / "revision_muestra.csv"
MANIFEST_PATH = ROOT / "resultados" / "dataset_manifest.json"


@dataclass(frozen=True, slots=True)
class Domain:
    schema_id: str
    split: str
    subject: str
    main_table: str
    main_id: str
    main_name: str
    location: str
    group_table: str
    group_id: str
    group_name: str
    product_table: str
    product_id: str
    product_name: str
    price: str
    product_group_fk: str
    event_table: str
    event_id: str
    event_main_fk: str
    event_date: str
    event_status: str
    event_total: str
    line_table: str
    line_event_fk: str
    line_product_fk: str
    quantity: str
    unit_price: str
    main_term: str
    product_term: str
    event_term: str
    statuses: tuple[str, str, str]


DOMAINS = [
    Domain("retail_en", "train", "comercio minorista", "customers", "customer_id", "customer_name", "city", "categories", "category_id", "category_name", "products", "product_id", "product_name", "price", "category_id", "orders", "order_id", "customer_id", "order_date", "status", "total", "order_items", "order_id", "product_id", "quantity", "unit_price", "cliente", "producto", "pedido", ("completed", "pending", "cancelled")),
    Domain("universidad_es", "train", "universidad", "estudiantes", "id_estudiante", "nombre", "ciudad", "departamentos", "id_departamento", "nombre_departamento", "cursos", "id_curso", "nombre_curso", "costo", "id_departamento", "matriculas", "id_matricula", "id_estudiante", "fecha_matricula", "estado", "total_pagado", "detalle_matricula", "id_matricula", "id_curso", "creditos", "costo_unitario", "estudiante", "curso", "matrícula", ("activa", "completada", "retirada")),
    Domain("clinica_es", "train", "clínica", "pacientes", "id_paciente", "nombre", "municipio", "especialidades", "id_especialidad", "nombre_especialidad", "tratamientos", "id_tratamiento", "nombre_tratamiento", "precio", "id_especialidad", "citas", "id_cita", "id_paciente", "fecha_cita", "estado", "total", "cita_tratamientos", "id_cita", "id_tratamiento", "cantidad", "precio_unitario", "paciente", "tratamiento", "cita", ("atendida", "programada", "cancelada")),
    Domain("biblioteca_es", "train", "biblioteca", "socios", "id_socio", "nombre", "zona", "generos", "id_genero", "nombre_genero", "libros", "id_libro", "titulo", "valor_reposicion", "id_genero", "prestamos", "id_prestamo", "id_socio", "fecha_prestamo", "estado", "multa_total", "prestamo_libros", "id_prestamo", "id_libro", "dias", "multa_diaria", "socio", "libro", "préstamo", ("devuelto", "activo", "vencido")),
    Domain("hotel_en", "train", "hotel", "guests", "guest_id", "guest_name", "country", "room_types", "room_type_id", "type_name", "rooms", "room_id", "room_name", "nightly_rate", "room_type_id", "reservations", "reservation_id", "guest_id", "check_in", "status", "total_amount", "reservation_rooms", "reservation_id", "room_id", "nights", "nightly_rate", "huésped", "habitación", "reservación", ("completed", "confirmed", "cancelled")),
    Domain("logistica_es", "train", "logística", "proveedores", "id_proveedor", "nombre", "region", "categorias", "id_categoria", "nombre_categoria", "articulos", "id_articulo", "nombre_articulo", "costo", "id_categoria", "envios", "id_envio", "id_proveedor", "fecha_envio", "estado", "costo_total", "detalle_envio", "id_envio", "id_articulo", "unidades", "costo_unitario", "proveedor", "artículo", "envío", ("entregado", "en_transito", "cancelado")),
    Domain("restaurante_es", "train", "restaurante", "clientes", "id_cliente", "nombre", "sector", "categorias_menu", "id_categoria", "nombre_categoria", "platillos", "id_platillo", "nombre_platillo", "precio", "id_categoria", "ordenes", "id_orden", "id_cliente", "fecha_orden", "estado", "total", "orden_detalle", "id_orden", "id_platillo", "cantidad", "precio_unitario", "cliente", "platillo", "orden", ("servida", "abierta", "cancelada")),
    Domain("cine_es", "train", "cine", "clientes", "id_cliente", "nombre", "ciudad", "generos", "id_genero", "nombre_genero", "peliculas", "id_pelicula", "titulo", "precio_base", "id_genero", "ventas", "id_venta", "id_cliente", "fecha_venta", "estado", "total", "venta_boletos", "id_venta", "id_pelicula", "cantidad", "precio_unitario", "cliente", "película", "venta", ("pagada", "reservada", "anulada")),
    Domain("seguros_es", "train", "seguros", "asegurados", "id_asegurado", "nombre", "departamento", "tipos_poliza", "id_tipo", "nombre_tipo", "polizas", "id_poliza", "nombre_poliza", "prima", "id_tipo", "reclamos", "id_reclamo", "id_asegurado", "fecha_reclamo", "estado", "monto", "reclamo_polizas", "id_reclamo", "id_poliza", "incidentes", "monto_unitario", "asegurado", "póliza", "reclamo", ("aprobado", "en_revision", "rechazado")),
    Domain("telecom_en", "train", "telecomunicaciones", "subscribers", "subscriber_id", "subscriber_name", "region", "plan_types", "plan_type_id", "type_name", "plans", "plan_id", "plan_name", "monthly_fee", "plan_type_id", "invoices", "invoice_id", "subscriber_id", "invoice_date", "status", "total_due", "invoice_lines", "invoice_id", "plan_id", "months", "unit_fee", "suscriptor", "plan", "factura", ("paid", "open", "void")),
    Domain("gimnasio_es", "train", "gimnasio", "miembros", "id_miembro", "nombre", "sede", "tipos_clase", "id_tipo", "nombre_tipo", "clases", "id_clase", "nombre_clase", "tarifa", "id_tipo", "reservas", "id_reserva", "id_miembro", "fecha_reserva", "estado", "total", "reserva_clases", "id_reserva", "id_clase", "sesiones", "tarifa_unitaria", "miembro", "clase", "reserva", ("asistida", "confirmada", "cancelada")),
    Domain("municipio_es", "train", "servicios municipales", "ciudadanos", "id_ciudadano", "nombre", "zona", "tipos_servicio", "id_tipo", "nombre_tipo", "servicios", "id_servicio", "nombre_servicio", "tarifa", "id_tipo", "solicitudes", "id_solicitud", "id_ciudadano", "fecha_solicitud", "estado", "total", "solicitud_servicios", "id_solicitud", "id_servicio", "cantidad", "tarifa_unitaria", "ciudadano", "servicio", "solicitud", ("resuelta", "abierta", "rechazada")),
    Domain("aerolinea_val", "validation", "aerolínea", "passengers", "passenger_id", "passenger_name", "country", "fare_classes", "fare_class_id", "class_name", "flights", "flight_id", "flight_code", "base_fare", "fare_class_id", "bookings", "booking_id", "passenger_id", "booking_date", "status", "total_amount", "booking_flights", "booking_id", "flight_id", "seats", "unit_fare", "pasajero", "vuelo", "reserva", ("confirmed", "pending", "cancelled")),
    Domain("eventos_val", "validation", "eventos", "asistentes", "id_asistente", "nombre", "ciudad", "tipos_evento", "id_tipo", "nombre_tipo", "eventos", "id_evento", "nombre_evento", "precio", "id_tipo", "inscripciones", "id_inscripcion", "id_asistente", "fecha_inscripcion", "estado", "total", "inscripcion_eventos", "id_inscripcion", "id_evento", "entradas", "precio_unitario", "asistente", "evento", "inscripción", ("pagada", "pendiente", "cancelada")),
]


LOCATIONS = ["Guatemala", "Mixco", "Villa Nueva", "Antigua", "Quetzaltenango"]
NAMES = ["Ana López", "Luis Pérez", "Marta García", "Carlos Díaz", "Sofía Morales", "José Ramírez", "Elena Castillo", "Diego Herrera"]
GROUPS = ["General", "Premium", "Familiar", "Profesional", "Especial"]


def _q(identifier: str) -> str:
    return f"`{identifier}`"


def schema_sql(domain: Domain) -> str:
    d = domain
    return f"""CREATE TABLE {_q(d.main_table)} (
  {_q(d.main_id)} INT PRIMARY KEY,
  {_q(d.main_name)} VARCHAR(120) NOT NULL,
  {_q(d.location)} VARCHAR(80) NOT NULL,
  created_at DATE NOT NULL,
  INDEX idx_{d.main_table}_{d.location} ({_q(d.location)})
) ENGINE=InnoDB COMMENT='Entidad principal de {d.subject}';

CREATE TABLE {_q(d.group_table)} (
  {_q(d.group_id)} INT PRIMARY KEY,
  {_q(d.group_name)} VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB COMMENT='Clasificación del catálogo';

CREATE TABLE {_q(d.product_table)} (
  {_q(d.product_id)} INT PRIMARY KEY,
  {_q(d.product_name)} VARCHAR(140) NOT NULL,
  {_q(d.price)} DECIMAL(12,2) NOT NULL,
  {_q(d.product_group_fk)} INT NOT NULL,
  CONSTRAINT fk_{d.product_table}_{d.group_table}
    FOREIGN KEY ({_q(d.product_group_fk)}) REFERENCES {_q(d.group_table)} ({_q(d.group_id)}),
  INDEX idx_{d.product_table}_{d.product_group_fk} ({_q(d.product_group_fk)})
) ENGINE=InnoDB COMMENT='Catálogo de {d.product_term}s';

CREATE TABLE {_q(d.event_table)} (
  {_q(d.event_id)} INT PRIMARY KEY,
  {_q(d.event_main_fk)} INT NOT NULL,
  {_q(d.event_date)} DATE NOT NULL,
  {_q(d.event_status)} VARCHAR(24) NOT NULL,
  {_q(d.event_total)} DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_{d.event_table}_{d.main_table}
    FOREIGN KEY ({_q(d.event_main_fk)}) REFERENCES {_q(d.main_table)} ({_q(d.main_id)}),
  INDEX idx_{d.event_table}_main_date ({_q(d.event_main_fk)}, {_q(d.event_date)}),
  INDEX idx_{d.event_table}_status ({_q(d.event_status)})
) ENGINE=InnoDB COMMENT='Transacciones de {d.event_term}s';

CREATE TABLE {_q(d.line_table)} (
  {_q(d.line_event_fk)} INT NOT NULL,
  {_q(d.line_product_fk)} INT NOT NULL,
  {_q(d.quantity)} INT NOT NULL,
  {_q(d.unit_price)} DECIMAL(12,2) NOT NULL,
  PRIMARY KEY ({_q(d.line_event_fk)}, {_q(d.line_product_fk)}),
  CONSTRAINT fk_{d.line_table}_{d.event_table}
    FOREIGN KEY ({_q(d.line_event_fk)}) REFERENCES {_q(d.event_table)} ({_q(d.event_id)}),
  CONSTRAINT fk_{d.line_table}_{d.product_table}
    FOREIGN KEY ({_q(d.line_product_fk)}) REFERENCES {_q(d.product_table)} ({_q(d.product_id)}),
  INDEX idx_{d.line_table}_{d.line_product_fk} ({_q(d.line_product_fk)})
) ENGINE=InnoDB COMMENT='Detalle de cada {d.event_term}';
"""


def _sql_string(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def seed_sql(domain: Domain) -> str:
    d = domain
    statements: list[str] = []
    main_values = []
    for index, name in enumerate(NAMES, start=1):
        created = date(2022, 1, 1) + timedelta(days=index * 47)
        main_values.append(f"({index}, {_sql_string(name)}, {_sql_string(LOCATIONS[(index - 1) % len(LOCATIONS)])}, '{created}')")
    statements.append(
        f"INSERT INTO {_q(d.main_table)} ({_q(d.main_id)}, {_q(d.main_name)}, {_q(d.location)}, created_at) VALUES\n  "
        + ",\n  ".join(main_values)
        + ";"
    )
    statements.append(
        f"INSERT INTO {_q(d.group_table)} ({_q(d.group_id)}, {_q(d.group_name)}) VALUES\n  "
        + ",\n  ".join(f"({i}, {_sql_string(name)})" for i, name in enumerate(GROUPS, 1))
        + ";"
    )
    product_values = []
    for index in range(1, 16):
        price = 12.5 + index * 7.25
        product_values.append(f"({index}, {_sql_string(f'{d.product_term.title()} {index:02d}')}, {price:.2f}, {(index - 1) % 5 + 1})")
    statements.append(
        f"INSERT INTO {_q(d.product_table)} ({_q(d.product_id)}, {_q(d.product_name)}, {_q(d.price)}, {_q(d.product_group_fk)}) VALUES\n  "
        + ",\n  ".join(product_values)
        + ";"
    )
    event_values = []
    line_values = []
    for index in range(1, 41):
        event_date = date(2023, 1, 1) + timedelta(days=index * 23)
        status = d.statuses[(index - 1) % 3]
        first_product = (index - 1) % 15 + 1
        second_product = index % 15 + 1
        first_qty = index % 4 + 1
        second_qty = (index + 1) % 3 + 1
        first_price = 12.5 + first_product * 7.25
        second_price = 12.5 + second_product * 7.25
        total = first_qty * first_price + second_qty * second_price
        event_values.append(f"({index}, {(index - 1) % 8 + 1}, '{event_date}', {_sql_string(status)}, {total:.2f})")
        line_values.append(f"({index}, {first_product}, {first_qty}, {first_price:.2f})")
        line_values.append(f"({index}, {second_product}, {second_qty}, {second_price:.2f})")
    statements.append(
        f"INSERT INTO {_q(d.event_table)} ({_q(d.event_id)}, {_q(d.event_main_fk)}, {_q(d.event_date)}, {_q(d.event_status)}, {_q(d.event_total)}) VALUES\n  "
        + ",\n  ".join(event_values)
        + ";"
    )
    statements.append(
        f"INSERT INTO {_q(d.line_table)} ({_q(d.line_event_fk)}, {_q(d.line_product_fk)}, {_q(d.quantity)}, {_q(d.unit_price)}) VALUES\n  "
        + ",\n  ".join(line_values)
        + ";"
    )
    return "\n\n".join(statements) + "\n"


def query_templates(d: Domain) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def add(difficulty: str, question: str, sql: str, order: bool = False) -> None:
        rows.append(
            {
                "dificultad": difficulty,
                "pregunta": f"{question} Escenario {variant}.",
                "sql": sql,
                "orden_importa": order,
            }
        )

    for variant in range(1, 13):
        location = LOCATIONS[(variant - 1) % len(LOCATIONS)]
        status = d.statuses[(variant - 1) % 3]
        threshold = 15 + variant * 8
        limit = variant % 5 + 1
        start = f"202{3 + variant % 2}-{variant:02d}-01"
        end = f"202{3 + variant % 2}-{variant:02d}-28"

        add("facil", f"Lista hasta {limit} {d.main_term}s de {location}, ordenados por nombre.", f"SELECT {_q(d.main_name)} FROM {_q(d.main_table)} WHERE {_q(d.location)} = {_sql_string(location)} ORDER BY {_q(d.main_name)} LIMIT {limit};", True)
        add("facil", f"Muestra los {d.product_term}s con precio mayor a {threshold} y sus precios.", f"SELECT {_q(d.product_name)}, {_q(d.price)} FROM {_q(d.product_table)} WHERE {_q(d.price)} > {threshold} ORDER BY {_q(d.price)} DESC;", True)
        add("facil", f"¿Cuántos {d.event_term}s tienen estado {status}? Variante {variant}.", f"SELECT COUNT(*) AS total_{d.event_table} FROM {_q(d.event_table)} WHERE {_q(d.event_status)} = {_sql_string(status)};")
        add("facil", f"Lista los identificadores y fechas de {d.event_term}s entre {start} y {end}.", f"SELECT {_q(d.event_id)}, {_q(d.event_date)} FROM {_q(d.event_table)} WHERE {_q(d.event_date)} BETWEEN '{start}' AND '{end}' ORDER BY {_q(d.event_date)};", True)
        add("facil", f"Indica el precio máximo de los {d.product_term}s por encima de {threshold}.", f"SELECT MAX({_q(d.price)}) AS precio_maximo FROM {_q(d.product_table)} WHERE {_q(d.price)} > {threshold};")
        add("facil", f"Lista {limit} categorías del catálogo en orden alfabético.", f"SELECT {_q(d.group_name)} FROM {_q(d.group_table)} ORDER BY {_q(d.group_name)} LIMIT {limit};", True)
        add("facil", f"¿Cuál es el total promedio de los {d.event_term}s con estado {status}? Variante {variant}.", f"SELECT ROUND(AVG({_q(d.event_total)}), 2) AS promedio_total FROM {_q(d.event_table)} WHERE {_q(d.event_status)} = {_sql_string(status)};")

        add("media", f"Muestra cada {d.main_term} y la cantidad de {d.event_term}s con estado {status}, incluyendo quienes no tienen.", f"SELECT m.{_q(d.main_name)}, COUNT(e.{_q(d.event_id)}) AS cantidad FROM {_q(d.main_table)} AS m LEFT JOIN {_q(d.event_table)} AS e ON e.{_q(d.event_main_fk)} = m.{_q(d.main_id)} AND e.{_q(d.event_status)} = {_sql_string(status)} GROUP BY m.{_q(d.main_id)}, m.{_q(d.main_name)} ORDER BY cantidad DESC;", True)
        add("media", f"Calcula el total de {d.event_term}s por ubicación desde {start} para estado {status}.", f"SELECT m.{_q(d.location)}, ROUND(SUM(e.{_q(d.event_total)}), 2) AS total FROM {_q(d.main_table)} AS m JOIN {_q(d.event_table)} AS e ON e.{_q(d.event_main_fk)} = m.{_q(d.main_id)} WHERE e.{_q(d.event_date)} >= '{start}' AND e.{_q(d.event_status)} = {_sql_string(status)} GROUP BY m.{_q(d.location)} ORDER BY total DESC;", True)
        add("media", f"Lista categorías con al menos {limit} {d.product_term}s y su precio promedio.", f"SELECT g.{_q(d.group_name)}, COUNT(p.{_q(d.product_id)}) AS cantidad, ROUND(AVG(p.{_q(d.price)}), 2) AS promedio FROM {_q(d.group_table)} AS g JOIN {_q(d.product_table)} AS p ON p.{_q(d.product_group_fk)} = g.{_q(d.group_id)} GROUP BY g.{_q(d.group_id)}, g.{_q(d.group_name)} HAVING COUNT(p.{_q(d.product_id)}) >= {limit} ORDER BY cantidad DESC;", True)
        add("media", f"Muestra los {d.product_term}s y unidades registradas en {d.event_term}s {status} desde {start}.", f"SELECT p.{_q(d.product_name)}, SUM(l.{_q(d.quantity)}) AS unidades FROM {_q(d.product_table)} AS p JOIN {_q(d.line_table)} AS l ON l.{_q(d.line_product_fk)} = p.{_q(d.product_id)} JOIN {_q(d.event_table)} AS e ON e.{_q(d.event_id)} = l.{_q(d.line_event_fk)} WHERE e.{_q(d.event_status)} = {_sql_string(status)} AND e.{_q(d.event_date)} >= '{start}' GROUP BY p.{_q(d.product_id)}, p.{_q(d.product_name)} ORDER BY unidades DESC;", True)
        add("media", f"Encuentra {d.main_term}s sin {d.event_term}s posteriores a {start}.", f"SELECT m.{_q(d.main_name)} FROM {_q(d.main_table)} AS m LEFT JOIN {_q(d.event_table)} AS e ON e.{_q(d.event_main_fk)} = m.{_q(d.main_id)} AND e.{_q(d.event_date)} > '{start}' WHERE e.{_q(d.event_id)} IS NULL ORDER BY m.{_q(d.main_name)};", True)
        add("media", f"Resume cantidad y total de {d.event_term}s por mes del año {start[:4]}.", f"SELECT MONTH({_q(d.event_date)}) AS mes, COUNT(*) AS cantidad, ROUND(SUM({_q(d.event_total)}), 2) AS total FROM {_q(d.event_table)} WHERE YEAR({_q(d.event_date)}) = {start[:4]} GROUP BY MONTH({_q(d.event_date)}) ORDER BY mes;", True)
        add("media", f"Devuelve los {limit} {d.main_term}s con mayor promedio por {d.event_term} {status}.", f"SELECT m.{_q(d.main_name)}, ROUND(AVG(e.{_q(d.event_total)}), 2) AS promedio FROM {_q(d.main_table)} AS m JOIN {_q(d.event_table)} AS e ON e.{_q(d.event_main_fk)} = m.{_q(d.main_id)} WHERE e.{_q(d.event_status)} = {_sql_string(status)} GROUP BY m.{_q(d.main_id)}, m.{_q(d.main_name)} ORDER BY promedio DESC LIMIT {limit};", True)

        add("dificil", f"Lista {d.event_term}s cuyo total supera el promedio de su mismo estado {status} desde {start}.", f"SELECT e.{_q(d.event_id)}, e.{_q(d.event_total)} FROM {_q(d.event_table)} AS e WHERE e.{_q(d.event_status)} = {_sql_string(status)} AND e.{_q(d.event_date)} >= '{start}' AND e.{_q(d.event_total)} > (SELECT AVG(e2.{_q(d.event_total)}) FROM {_q(d.event_table)} AS e2 WHERE e2.{_q(d.event_status)} = e.{_q(d.event_status)}) ORDER BY e.{_q(d.event_total)} DESC;", True)
        add("dificil", f"Obtén los {d.product_term}s dentro de los primeros {limit} precios de cada categoría.", f"WITH ranked AS (SELECT p.{_q(d.product_name)}, g.{_q(d.group_name)}, p.{_q(d.price)}, DENSE_RANK() OVER (PARTITION BY g.{_q(d.group_id)} ORDER BY p.{_q(d.price)} DESC) AS posicion FROM {_q(d.product_table)} AS p JOIN {_q(d.group_table)} AS g ON g.{_q(d.group_id)} = p.{_q(d.product_group_fk)}) SELECT {_q(d.product_name)}, {_q(d.group_name)}, {_q(d.price)}, posicion FROM ranked WHERE posicion <= {limit} ORDER BY {_q(d.group_name)}, posicion;", True)
        add("dificil", f"Muestra el {d.event_term} más reciente de cada {d.main_term} antes de {end}.", f"WITH ranked AS (SELECT m.{_q(d.main_name)}, e.{_q(d.event_id)}, e.{_q(d.event_date)}, ROW_NUMBER() OVER (PARTITION BY m.{_q(d.main_id)} ORDER BY e.{_q(d.event_date)} DESC, e.{_q(d.event_id)} DESC) AS fila FROM {_q(d.main_table)} AS m JOIN {_q(d.event_table)} AS e ON e.{_q(d.event_main_fk)} = m.{_q(d.main_id)} WHERE e.{_q(d.event_date)} <= '{end}') SELECT {_q(d.main_name)}, {_q(d.event_id)}, {_q(d.event_date)} FROM ranked WHERE fila = 1 ORDER BY {_q(d.main_name)};", True)
        add("dificil", f"Calcula la participación porcentual de cada categoría en el valor de líneas desde {start}.", f"WITH totals AS (SELECT g.{_q(d.group_name)} AS categoria, SUM(l.{_q(d.quantity)} * l.{_q(d.unit_price)}) AS total_categoria FROM {_q(d.group_table)} AS g JOIN {_q(d.product_table)} AS p ON p.{_q(d.product_group_fk)} = g.{_q(d.group_id)} JOIN {_q(d.line_table)} AS l ON l.{_q(d.line_product_fk)} = p.{_q(d.product_id)} JOIN {_q(d.event_table)} AS e ON e.{_q(d.event_id)} = l.{_q(d.line_event_fk)} WHERE e.{_q(d.event_date)} >= '{start}' GROUP BY g.{_q(d.group_id)}, g.{_q(d.group_name)}) SELECT categoria, ROUND(total_categoria, 2) AS total_categoria, ROUND(100 * total_categoria / SUM(total_categoria) OVER (), 2) AS porcentaje FROM totals ORDER BY total_categoria DESC;", True)
    return rows


def enrich(domain: Domain, row: dict[str, Any], index: int) -> dict[str, Any]:
    ddl = schema_sql(domain)
    return {
        "id": f"{domain.schema_id}-{index:04d}",
        "schema_id": domain.schema_id,
        "split": domain.split,
        "esquema": ddl,
        **row,
        "fuente": "sintetico_codex",
        "generado_por": "OpenAI Codex",
        "licencia": "MIT",
        "validado_mysql": False,
        "estado_validacion": "pendiente_mysql",
        "motivo_descarte": None,
    }


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    training: list[dict[str, Any]] = []
    validation: list[dict[str, Any]] = []
    for domain in DOMAINS:
        folder = SCHEMAS_ROOT / domain.split / domain.schema_id
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "schema.sql").write_text(schema_sql(domain), encoding="utf-8", newline="\n")
        (folder / "seed.sql").write_text(seed_sql(domain), encoding="utf-8", newline="\n")
        (folder / "metadata.json").write_text(
            json.dumps(asdict(domain), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        queries = query_templates(domain)
        if domain.split == "train":
            training.extend(enrich(domain, row, index) for index, row in enumerate(queries, 1))
        else:
            by_level = {
                level: [row for row in queries if row["dificultad"] == level]
                for level in ("facil", "media", "dificil")
            }
            selected = by_level["facil"][:7] + by_level["media"][:7] + by_level["dificil"][:6]
            validation.extend(enrich(domain, row, index) for index, row in enumerate(selected, 1))

    assert len(training) >= 2_000
    assert len({row["schema_id"] for row in training}) == 12
    assert len(validation) == 40
    assert len({row["schema_id"] for row in validation}) == 2
    assert not ({row["schema_id"] for row in training} & {row["schema_id"] for row in validation})
    assert len({(row["schema_id"], row["pregunta"], row["sql"]) for row in training}) == len(training)

    write_jsonl(TRAIN_PATH, training)
    write_jsonl(VALIDATION_PATH, validation)

    VALIDATION_CSV.parent.mkdir(parents=True, exist_ok=True)
    with VALIDATION_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id", "schema_id", "dificultad", "peso", "pregunta", "sql_referencia", "orden_importa", "sql_predicho", "correcto", "categoria_error", "latencia_ms"],
        )
        writer.writeheader()
        weights = {"facil": 1, "media": 2, "dificil": 3}
        for row in validation:
            writer.writerow({
                "id": row["id"],
                "schema_id": row["schema_id"],
                "dificultad": row["dificultad"],
                "peso": weights[row["dificultad"]],
                "pregunta": row["pregunta"],
                "sql_referencia": row["sql"],
                "orden_importa": str(row["orden_importa"]).lower(),
                "sql_predicho": "",
                "correcto": "",
                "categoria_error": "pendiente_modelo",
                "latencia_ms": "",
            })

    sample = random.Random(2026).sample(training, 100)
    with REVIEW_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "schema_id", "dificultad", "pregunta", "sql", "revisor", "decision", "observaciones"])
        writer.writeheader()
        for row in sample:
            writer.writerow({key: row.get(key, "") for key in ("id", "schema_id", "dificultad", "pregunta", "sql")} | {"revisor": "", "decision": "pendiente_revision_humana", "observaciones": ""})

    manifest = {
        "generated_at": "2026-10-17",
        "generator": "OpenAI Codex + plantillas deterministas revisables",
        "seed": 2026,
        "mysql_target": "8.4.10",
        "mysql_validation_complete": False,
        "training_candidates": len(training),
        "training_accepted": 0,
        "training_schemas": 12,
        "validation_examples": len(validation),
        "validation_schemas": 2,
        "difficulty_validation": {level: sum(row["dificultad"] == level for row in validation) for level in ("facil", "media", "dificil")},
        "training_sha256": sha256(TRAIN_PATH),
        "validation_sha256": sha256(VALIDATION_PATH),
        "human_review_complete": False,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
