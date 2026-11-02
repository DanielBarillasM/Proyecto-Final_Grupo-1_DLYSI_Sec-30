CREATE TABLE `proveedores` (
  `id_proveedor` INT PRIMARY KEY,
  `nombre` VARCHAR(120) NOT NULL,
  `region` VARCHAR(80) NOT NULL,
  created_at DATE NOT NULL,
  INDEX idx_proveedores_region (`region`)
) ENGINE=InnoDB COMMENT='Entidad principal de logística';

CREATE TABLE `categorias` (
  `id_categoria` INT PRIMARY KEY,
  `nombre_categoria` VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB COMMENT='Clasificación del catálogo';

CREATE TABLE `articulos` (
  `id_articulo` INT PRIMARY KEY,
  `nombre_articulo` VARCHAR(140) NOT NULL,
  `costo` DECIMAL(12,2) NOT NULL,
  `id_categoria` INT NOT NULL,
  CONSTRAINT fk_articulos_categorias
    FOREIGN KEY (`id_categoria`) REFERENCES `categorias` (`id_categoria`),
  INDEX idx_articulos_id_categoria (`id_categoria`)
) ENGINE=InnoDB COMMENT='Catálogo de artículos';

CREATE TABLE `envios` (
  `id_envio` INT PRIMARY KEY,
  `id_proveedor` INT NOT NULL,
  `fecha_envio` DATE NOT NULL,
  `estado` VARCHAR(24) NOT NULL,
  `costo_total` DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_envios_proveedores
    FOREIGN KEY (`id_proveedor`) REFERENCES `proveedores` (`id_proveedor`),
  INDEX idx_envios_main_date (`id_proveedor`, `fecha_envio`),
  INDEX idx_envios_status (`estado`)
) ENGINE=InnoDB COMMENT='Transacciones de envíos';

CREATE TABLE `detalle_envio` (
  `id_envio` INT NOT NULL,
  `id_articulo` INT NOT NULL,
  `unidades` INT NOT NULL,
  `costo_unitario` DECIMAL(12,2) NOT NULL,
  PRIMARY KEY (`id_envio`, `id_articulo`),
  CONSTRAINT fk_detalle_envio_envios
    FOREIGN KEY (`id_envio`) REFERENCES `envios` (`id_envio`),
  CONSTRAINT fk_detalle_envio_articulos
    FOREIGN KEY (`id_articulo`) REFERENCES `articulos` (`id_articulo`),
  INDEX idx_detalle_envio_id_articulo (`id_articulo`)
) ENGINE=InnoDB COMMENT='Detalle de cada envío';
