CREATE TABLE `estudiantes` (
  `id_estudiante` INT PRIMARY KEY,
  `nombre` VARCHAR(120) NOT NULL,
  `ciudad` VARCHAR(80) NOT NULL,
  created_at DATE NOT NULL,
  INDEX idx_estudiantes_ciudad (`ciudad`)
) ENGINE=InnoDB COMMENT='Entidad principal de universidad';

CREATE TABLE `departamentos` (
  `id_departamento` INT PRIMARY KEY,
  `nombre_departamento` VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB COMMENT='Clasificación del catálogo';

CREATE TABLE `cursos` (
  `id_curso` INT PRIMARY KEY,
  `nombre_curso` VARCHAR(140) NOT NULL,
  `costo` DECIMAL(12,2) NOT NULL,
  `id_departamento` INT NOT NULL,
  CONSTRAINT fk_cursos_departamentos
    FOREIGN KEY (`id_departamento`) REFERENCES `departamentos` (`id_departamento`),
  INDEX idx_cursos_id_departamento (`id_departamento`)
) ENGINE=InnoDB COMMENT='Catálogo de cursos';

CREATE TABLE `matriculas` (
  `id_matricula` INT PRIMARY KEY,
  `id_estudiante` INT NOT NULL,
  `fecha_matricula` DATE NOT NULL,
  `estado` VARCHAR(24) NOT NULL,
  `total_pagado` DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_matriculas_estudiantes
    FOREIGN KEY (`id_estudiante`) REFERENCES `estudiantes` (`id_estudiante`),
  INDEX idx_matriculas_main_date (`id_estudiante`, `fecha_matricula`),
  INDEX idx_matriculas_status (`estado`)
) ENGINE=InnoDB COMMENT='Transacciones de matrículas';

CREATE TABLE `detalle_matricula` (
  `id_matricula` INT NOT NULL,
  `id_curso` INT NOT NULL,
  `creditos` INT NOT NULL,
  `costo_unitario` DECIMAL(12,2) NOT NULL,
  PRIMARY KEY (`id_matricula`, `id_curso`),
  CONSTRAINT fk_detalle_matricula_matriculas
    FOREIGN KEY (`id_matricula`) REFERENCES `matriculas` (`id_matricula`),
  CONSTRAINT fk_detalle_matricula_cursos
    FOREIGN KEY (`id_curso`) REFERENCES `cursos` (`id_curso`),
  INDEX idx_detalle_matricula_id_curso (`id_curso`)
) ENGINE=InnoDB COMMENT='Detalle de cada matrícula';
