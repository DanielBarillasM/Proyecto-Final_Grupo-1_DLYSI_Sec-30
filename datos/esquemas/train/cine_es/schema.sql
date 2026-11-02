CREATE TABLE `clientes` (
  `id_cliente` INT PRIMARY KEY,
  `nombre` VARCHAR(120) NOT NULL,
  `ciudad` VARCHAR(80) NOT NULL,
  created_at DATE NOT NULL,
  INDEX idx_clientes_ciudad (`ciudad`)
) ENGINE=InnoDB COMMENT='Entidad principal de cine';

CREATE TABLE `generos` (
  `id_genero` INT PRIMARY KEY,
  `nombre_genero` VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB COMMENT='Clasificación del catálogo';

CREATE TABLE `peliculas` (
  `id_pelicula` INT PRIMARY KEY,
  `titulo` VARCHAR(140) NOT NULL,
  `precio_base` DECIMAL(12,2) NOT NULL,
  `id_genero` INT NOT NULL,
  CONSTRAINT fk_peliculas_generos
    FOREIGN KEY (`id_genero`) REFERENCES `generos` (`id_genero`),
  INDEX idx_peliculas_id_genero (`id_genero`)
) ENGINE=InnoDB COMMENT='Catálogo de películas';

CREATE TABLE `ventas` (
  `id_venta` INT PRIMARY KEY,
  `id_cliente` INT NOT NULL,
  `fecha_venta` DATE NOT NULL,
  `estado` VARCHAR(24) NOT NULL,
  `total` DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_ventas_clientes
    FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`),
  INDEX idx_ventas_main_date (`id_cliente`, `fecha_venta`),
  INDEX idx_ventas_status (`estado`)
) ENGINE=InnoDB COMMENT='Transacciones de ventas';

CREATE TABLE `venta_boletos` (
  `id_venta` INT NOT NULL,
  `id_pelicula` INT NOT NULL,
  `cantidad` INT NOT NULL,
  `precio_unitario` DECIMAL(12,2) NOT NULL,
  PRIMARY KEY (`id_venta`, `id_pelicula`),
  CONSTRAINT fk_venta_boletos_ventas
    FOREIGN KEY (`id_venta`) REFERENCES `ventas` (`id_venta`),
  CONSTRAINT fk_venta_boletos_peliculas
    FOREIGN KEY (`id_pelicula`) REFERENCES `peliculas` (`id_pelicula`),
  INDEX idx_venta_boletos_id_pelicula (`id_pelicula`)
) ENGINE=InnoDB COMMENT='Detalle de cada venta';
