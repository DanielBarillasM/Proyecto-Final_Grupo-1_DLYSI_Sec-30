CREATE TABLE `customers` (
  `customer_id` INT PRIMARY KEY,
  `customer_name` VARCHAR(120) NOT NULL,
  `city` VARCHAR(80) NOT NULL,
  created_at DATE NOT NULL,
  INDEX idx_customers_city (`city`)
) ENGINE=InnoDB COMMENT='Entidad principal de comercio minorista';

CREATE TABLE `categories` (
  `category_id` INT PRIMARY KEY,
  `category_name` VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB COMMENT='Clasificación del catálogo';

CREATE TABLE `products` (
  `product_id` INT PRIMARY KEY,
  `product_name` VARCHAR(140) NOT NULL,
  `price` DECIMAL(12,2) NOT NULL,
  `category_id` INT NOT NULL,
  CONSTRAINT fk_products_categories
    FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`),
  INDEX idx_products_category_id (`category_id`)
) ENGINE=InnoDB COMMENT='Catálogo de productos';

CREATE TABLE `orders` (
  `order_id` INT PRIMARY KEY,
  `customer_id` INT NOT NULL,
  `order_date` DATE NOT NULL,
  `status` VARCHAR(24) NOT NULL,
  `total` DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_orders_customers
    FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`),
  INDEX idx_orders_main_date (`customer_id`, `order_date`),
  INDEX idx_orders_status (`status`)
) ENGINE=InnoDB COMMENT='Transacciones de pedidos';

CREATE TABLE `order_items` (
  `order_id` INT NOT NULL,
  `product_id` INT NOT NULL,
  `quantity` INT NOT NULL,
  `unit_price` DECIMAL(12,2) NOT NULL,
  PRIMARY KEY (`order_id`, `product_id`),
  CONSTRAINT fk_order_items_orders
    FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`),
  CONSTRAINT fk_order_items_products
    FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`),
  INDEX idx_order_items_product_id (`product_id`)
) ENGINE=InnoDB COMMENT='Detalle de cada pedido';
