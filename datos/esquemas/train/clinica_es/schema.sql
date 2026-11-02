CREATE TABLE `pacientes` (
  `id_paciente` INT PRIMARY KEY,
  `nombre` VARCHAR(120) NOT NULL,
  `municipio` VARCHAR(80) NOT NULL,
  created_at DATE NOT NULL,
  INDEX idx_pacientes_municipio (`municipio`)
) ENGINE=InnoDB COMMENT='Entidad principal de clínica';

CREATE TABLE `especialidades` (
  `id_especialidad` INT PRIMARY KEY,
  `nombre_especialidad` VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB COMMENT='Clasificación del catálogo';

CREATE TABLE `tratamientos` (
  `id_tratamiento` INT PRIMARY KEY,
  `nombre_tratamiento` VARCHAR(140) NOT NULL,
  `precio` DECIMAL(12,2) NOT NULL,
  `id_especialidad` INT NOT NULL,
  CONSTRAINT fk_tratamientos_especialidades
    FOREIGN KEY (`id_especialidad`) REFERENCES `especialidades` (`id_especialidad`),
  INDEX idx_tratamientos_id_especialidad (`id_especialidad`)
) ENGINE=InnoDB COMMENT='Catálogo de tratamientos';

CREATE TABLE `citas` (
  `id_cita` INT PRIMARY KEY,
  `id_paciente` INT NOT NULL,
  `fecha_cita` DATE NOT NULL,
  `estado` VARCHAR(24) NOT NULL,
  `total` DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_citas_pacientes
    FOREIGN KEY (`id_paciente`) REFERENCES `pacientes` (`id_paciente`),
  INDEX idx_citas_main_date (`id_paciente`, `fecha_cita`),
  INDEX idx_citas_status (`estado`)
) ENGINE=InnoDB COMMENT='Transacciones de citas';

CREATE TABLE `cita_tratamientos` (
  `id_cita` INT NOT NULL,
  `id_tratamiento` INT NOT NULL,
  `cantidad` INT NOT NULL,
  `precio_unitario` DECIMAL(12,2) NOT NULL,
  PRIMARY KEY (`id_cita`, `id_tratamiento`),
  CONSTRAINT fk_cita_tratamientos_citas
    FOREIGN KEY (`id_cita`) REFERENCES `citas` (`id_cita`),
  CONSTRAINT fk_cita_tratamientos_tratamientos
    FOREIGN KEY (`id_tratamiento`) REFERENCES `tratamientos` (`id_tratamiento`),
  INDEX idx_cita_tratamientos_id_tratamiento (`id_tratamiento`)
) ENGINE=InnoDB COMMENT='Detalle de cada cita';
