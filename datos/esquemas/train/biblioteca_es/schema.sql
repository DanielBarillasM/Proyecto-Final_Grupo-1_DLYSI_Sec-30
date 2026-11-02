CREATE TABLE `socios` (
  `id_socio` INT PRIMARY KEY,
  `nombre` VARCHAR(120) NOT NULL,
  `zona` VARCHAR(80) NOT NULL,
  created_at DATE NOT NULL,
  INDEX idx_socios_zona (`zona`)
) ENGINE=InnoDB COMMENT='Entidad principal de biblioteca';

CREATE TABLE `generos` (
  `id_genero` INT PRIMARY KEY,
  `nombre_genero` VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB COMMENT='Clasificación del catálogo';

CREATE TABLE `libros` (
  `id_libro` INT PRIMARY KEY,
  `titulo` VARCHAR(140) NOT NULL,
  `valor_reposicion` DECIMAL(12,2) NOT NULL,
  `id_genero` INT NOT NULL,
  CONSTRAINT fk_libros_generos
    FOREIGN KEY (`id_genero`) REFERENCES `generos` (`id_genero`),
  INDEX idx_libros_id_genero (`id_genero`)
) ENGINE=InnoDB COMMENT='Catálogo de libros';

CREATE TABLE `prestamos` (
  `id_prestamo` INT PRIMARY KEY,
  `id_socio` INT NOT NULL,
  `fecha_prestamo` DATE NOT NULL,
  `estado` VARCHAR(24) NOT NULL,
  `multa_total` DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_prestamos_socios
    FOREIGN KEY (`id_socio`) REFERENCES `socios` (`id_socio`),
  INDEX idx_prestamos_main_date (`id_socio`, `fecha_prestamo`),
  INDEX idx_prestamos_status (`estado`)
) ENGINE=InnoDB COMMENT='Transacciones de préstamos';

CREATE TABLE `prestamo_libros` (
  `id_prestamo` INT NOT NULL,
  `id_libro` INT NOT NULL,
  `dias` INT NOT NULL,
  `multa_diaria` DECIMAL(12,2) NOT NULL,
  PRIMARY KEY (`id_prestamo`, `id_libro`),
  CONSTRAINT fk_prestamo_libros_prestamos
    FOREIGN KEY (`id_prestamo`) REFERENCES `prestamos` (`id_prestamo`),
  CONSTRAINT fk_prestamo_libros_libros
    FOREIGN KEY (`id_libro`) REFERENCES `libros` (`id_libro`),
  INDEX idx_prestamo_libros_id_libro (`id_libro`)
) ENGINE=InnoDB COMMENT='Detalle de cada préstamo';
