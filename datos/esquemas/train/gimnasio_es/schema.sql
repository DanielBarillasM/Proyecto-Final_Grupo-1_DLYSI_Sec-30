CREATE TABLE `miembros` (
  `id_miembro` INT PRIMARY KEY,
  `nombre` VARCHAR(120) NOT NULL,
  `sede` VARCHAR(80) NOT NULL,
  created_at DATE NOT NULL,
  INDEX idx_miembros_sede (`sede`)
) ENGINE=InnoDB COMMENT='Entidad principal de gimnasio';

CREATE TABLE `tipos_clase` (
  `id_tipo` INT PRIMARY KEY,
  `nombre_tipo` VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB COMMENT='Clasificación del catálogo';

CREATE TABLE `clases` (
  `id_clase` INT PRIMARY KEY,
  `nombre_clase` VARCHAR(140) NOT NULL,
  `tarifa` DECIMAL(12,2) NOT NULL,
  `id_tipo` INT NOT NULL,
  CONSTRAINT fk_clases_tipos_clase
    FOREIGN KEY (`id_tipo`) REFERENCES `tipos_clase` (`id_tipo`),
  INDEX idx_clases_id_tipo (`id_tipo`)
) ENGINE=InnoDB COMMENT='Catálogo de clases';

CREATE TABLE `reservas` (
  `id_reserva` INT PRIMARY KEY,
  `id_miembro` INT NOT NULL,
  `fecha_reserva` DATE NOT NULL,
  `estado` VARCHAR(24) NOT NULL,
  `total` DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_reservas_miembros
    FOREIGN KEY (`id_miembro`) REFERENCES `miembros` (`id_miembro`),
  INDEX idx_reservas_main_date (`id_miembro`, `fecha_reserva`),
  INDEX idx_reservas_status (`estado`)
) ENGINE=InnoDB COMMENT='Transacciones de reservas';

CREATE TABLE `reserva_clases` (
  `id_reserva` INT NOT NULL,
  `id_clase` INT NOT NULL,
  `sesiones` INT NOT NULL,
  `tarifa_unitaria` DECIMAL(12,2) NOT NULL,
  PRIMARY KEY (`id_reserva`, `id_clase`),
  CONSTRAINT fk_reserva_clases_reservas
    FOREIGN KEY (`id_reserva`) REFERENCES `reservas` (`id_reserva`),
  CONSTRAINT fk_reserva_clases_clases
    FOREIGN KEY (`id_clase`) REFERENCES `clases` (`id_clase`),
  INDEX idx_reserva_clases_id_clase (`id_clase`)
) ENGINE=InnoDB COMMENT='Detalle de cada reserva';
