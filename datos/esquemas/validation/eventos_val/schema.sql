CREATE TABLE `asistentes` (
  `id_asistente` INT PRIMARY KEY,
  `nombre` VARCHAR(120) NOT NULL,
  `ciudad` VARCHAR(80) NOT NULL,
  created_at DATE NOT NULL,
  INDEX idx_asistentes_ciudad (`ciudad`)
) ENGINE=InnoDB COMMENT='Entidad principal de eventos';

CREATE TABLE `tipos_evento` (
  `id_tipo` INT PRIMARY KEY,
  `nombre_tipo` VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB COMMENT='Clasificación del catálogo';

CREATE TABLE `eventos` (
  `id_evento` INT PRIMARY KEY,
  `nombre_evento` VARCHAR(140) NOT NULL,
  `precio` DECIMAL(12,2) NOT NULL,
  `id_tipo` INT NOT NULL,
  CONSTRAINT fk_eventos_tipos_evento
    FOREIGN KEY (`id_tipo`) REFERENCES `tipos_evento` (`id_tipo`),
  INDEX idx_eventos_id_tipo (`id_tipo`)
) ENGINE=InnoDB COMMENT='Catálogo de eventos';

CREATE TABLE `inscripciones` (
  `id_inscripcion` INT PRIMARY KEY,
  `id_asistente` INT NOT NULL,
  `fecha_inscripcion` DATE NOT NULL,
  `estado` VARCHAR(24) NOT NULL,
  `total` DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_inscripciones_asistentes
    FOREIGN KEY (`id_asistente`) REFERENCES `asistentes` (`id_asistente`),
  INDEX idx_inscripciones_main_date (`id_asistente`, `fecha_inscripcion`),
  INDEX idx_inscripciones_status (`estado`)
) ENGINE=InnoDB COMMENT='Transacciones de inscripcións';

CREATE TABLE `inscripcion_eventos` (
  `id_inscripcion` INT NOT NULL,
  `id_evento` INT NOT NULL,
  `entradas` INT NOT NULL,
  `precio_unitario` DECIMAL(12,2) NOT NULL,
  PRIMARY KEY (`id_inscripcion`, `id_evento`),
  CONSTRAINT fk_inscripcion_eventos_inscripciones
    FOREIGN KEY (`id_inscripcion`) REFERENCES `inscripciones` (`id_inscripcion`),
  CONSTRAINT fk_inscripcion_eventos_eventos
    FOREIGN KEY (`id_evento`) REFERENCES `eventos` (`id_evento`),
  INDEX idx_inscripcion_eventos_id_evento (`id_evento`)
) ENGINE=InnoDB COMMENT='Detalle de cada inscripción';
