CREATE TABLE `clientes` (
  `id_cliente` INT PRIMARY KEY,
  `nombre` VARCHAR(120) NOT NULL,
  `sector` VARCHAR(80) NOT NULL,
  created_at DATE NOT NULL,
  INDEX idx_clientes_sector (`sector`)
) ENGINE=InnoDB COMMENT='Entidad principal de restaurante';

CREATE TABLE `categorias_menu` (
  `id_categoria` INT PRIMARY KEY,
  `nombre_categoria` VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB COMMENT='Clasificación del catálogo';

CREATE TABLE `platillos` (
  `id_platillo` INT PRIMARY KEY,
  `nombre_platillo` VARCHAR(140) NOT NULL,
  `precio` DECIMAL(12,2) NOT NULL,
  `id_categoria` INT NOT NULL,
  CONSTRAINT fk_platillos_categorias_menu
    FOREIGN KEY (`id_categoria`) REFERENCES `categorias_menu` (`id_categoria`),
  INDEX idx_platillos_id_categoria (`id_categoria`)
) ENGINE=InnoDB COMMENT='Catálogo de platillos';

CREATE TABLE `ordenes` (
  `id_orden` INT PRIMARY KEY,
  `id_cliente` INT NOT NULL,
  `fecha_orden` DATE NOT NULL,
  `estado` VARCHAR(24) NOT NULL,
  `total` DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_ordenes_clientes
    FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`),
  INDEX idx_ordenes_main_date (`id_cliente`, `fecha_orden`),
  INDEX idx_ordenes_status (`estado`)
) ENGINE=InnoDB COMMENT='Transacciones de ordens';

CREATE TABLE `orden_detalle` (
  `id_orden` INT NOT NULL,
  `id_platillo` INT NOT NULL,
  `cantidad` INT NOT NULL,
  `precio_unitario` DECIMAL(12,2) NOT NULL,
  PRIMARY KEY (`id_orden`, `id_platillo`),
  CONSTRAINT fk_orden_detalle_ordenes
    FOREIGN KEY (`id_orden`) REFERENCES `ordenes` (`id_orden`),
  CONSTRAINT fk_orden_detalle_platillos
    FOREIGN KEY (`id_platillo`) REFERENCES `platillos` (`id_platillo`),
  INDEX idx_orden_detalle_id_platillo (`id_platillo`)
) ENGINE=InnoDB COMMENT='Detalle de cada orden';
