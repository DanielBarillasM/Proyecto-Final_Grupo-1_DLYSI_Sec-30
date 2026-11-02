CREATE TABLE `ciudadanos` (
  `id_ciudadano` INT PRIMARY KEY,
  `nombre` VARCHAR(120) NOT NULL,
  `zona` VARCHAR(80) NOT NULL,
  created_at DATE NOT NULL,
  INDEX idx_ciudadanos_zona (`zona`)
) ENGINE=InnoDB COMMENT='Entidad principal de servicios municipales';

CREATE TABLE `tipos_servicio` (
  `id_tipo` INT PRIMARY KEY,
  `nombre_tipo` VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB COMMENT='Clasificación del catálogo';

CREATE TABLE `servicios` (
  `id_servicio` INT PRIMARY KEY,
  `nombre_servicio` VARCHAR(140) NOT NULL,
  `tarifa` DECIMAL(12,2) NOT NULL,
  `id_tipo` INT NOT NULL,
  CONSTRAINT fk_servicios_tipos_servicio
    FOREIGN KEY (`id_tipo`) REFERENCES `tipos_servicio` (`id_tipo`),
  INDEX idx_servicios_id_tipo (`id_tipo`)
) ENGINE=InnoDB COMMENT='Catálogo de servicios';

CREATE TABLE `solicitudes` (
  `id_solicitud` INT PRIMARY KEY,
  `id_ciudadano` INT NOT NULL,
  `fecha_solicitud` DATE NOT NULL,
  `estado` VARCHAR(24) NOT NULL,
  `total` DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_solicitudes_ciudadanos
    FOREIGN KEY (`id_ciudadano`) REFERENCES `ciudadanos` (`id_ciudadano`),
  INDEX idx_solicitudes_main_date (`id_ciudadano`, `fecha_solicitud`),
  INDEX idx_solicitudes_status (`estado`)
) ENGINE=InnoDB COMMENT='Transacciones de solicituds';

CREATE TABLE `solicitud_servicios` (
  `id_solicitud` INT NOT NULL,
  `id_servicio` INT NOT NULL,
  `cantidad` INT NOT NULL,
  `tarifa_unitaria` DECIMAL(12,2) NOT NULL,
  PRIMARY KEY (`id_solicitud`, `id_servicio`),
  CONSTRAINT fk_solicitud_servicios_solicitudes
    FOREIGN KEY (`id_solicitud`) REFERENCES `solicitudes` (`id_solicitud`),
  CONSTRAINT fk_solicitud_servicios_servicios
    FOREIGN KEY (`id_servicio`) REFERENCES `servicios` (`id_servicio`),
  INDEX idx_solicitud_servicios_id_servicio (`id_servicio`)
) ENGINE=InnoDB COMMENT='Detalle de cada solicitud';
