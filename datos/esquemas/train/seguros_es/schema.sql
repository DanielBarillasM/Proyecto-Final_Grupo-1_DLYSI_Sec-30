CREATE TABLE `asegurados` (
  `id_asegurado` INT PRIMARY KEY,
  `nombre` VARCHAR(120) NOT NULL,
  `departamento` VARCHAR(80) NOT NULL,
  created_at DATE NOT NULL,
  INDEX idx_asegurados_departamento (`departamento`)
) ENGINE=InnoDB COMMENT='Entidad principal de seguros';

CREATE TABLE `tipos_poliza` (
  `id_tipo` INT PRIMARY KEY,
  `nombre_tipo` VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB COMMENT='Clasificación del catálogo';

CREATE TABLE `polizas` (
  `id_poliza` INT PRIMARY KEY,
  `nombre_poliza` VARCHAR(140) NOT NULL,
  `prima` DECIMAL(12,2) NOT NULL,
  `id_tipo` INT NOT NULL,
  CONSTRAINT fk_polizas_tipos_poliza
    FOREIGN KEY (`id_tipo`) REFERENCES `tipos_poliza` (`id_tipo`),
  INDEX idx_polizas_id_tipo (`id_tipo`)
) ENGINE=InnoDB COMMENT='Catálogo de pólizas';

CREATE TABLE `reclamos` (
  `id_reclamo` INT PRIMARY KEY,
  `id_asegurado` INT NOT NULL,
  `fecha_reclamo` DATE NOT NULL,
  `estado` VARCHAR(24) NOT NULL,
  `monto` DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_reclamos_asegurados
    FOREIGN KEY (`id_asegurado`) REFERENCES `asegurados` (`id_asegurado`),
  INDEX idx_reclamos_main_date (`id_asegurado`, `fecha_reclamo`),
  INDEX idx_reclamos_status (`estado`)
) ENGINE=InnoDB COMMENT='Transacciones de reclamos';

CREATE TABLE `reclamo_polizas` (
  `id_reclamo` INT NOT NULL,
  `id_poliza` INT NOT NULL,
  `incidentes` INT NOT NULL,
  `monto_unitario` DECIMAL(12,2) NOT NULL,
  PRIMARY KEY (`id_reclamo`, `id_poliza`),
  CONSTRAINT fk_reclamo_polizas_reclamos
    FOREIGN KEY (`id_reclamo`) REFERENCES `reclamos` (`id_reclamo`),
  CONSTRAINT fk_reclamo_polizas_polizas
    FOREIGN KEY (`id_poliza`) REFERENCES `polizas` (`id_poliza`),
  INDEX idx_reclamo_polizas_id_poliza (`id_poliza`)
) ENGINE=InnoDB COMMENT='Detalle de cada reclamo';
