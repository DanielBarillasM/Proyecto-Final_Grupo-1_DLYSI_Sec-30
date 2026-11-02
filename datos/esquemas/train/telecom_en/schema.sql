CREATE TABLE `subscribers` (
  `subscriber_id` INT PRIMARY KEY,
  `subscriber_name` VARCHAR(120) NOT NULL,
  `region` VARCHAR(80) NOT NULL,
  created_at DATE NOT NULL,
  INDEX idx_subscribers_region (`region`)
) ENGINE=InnoDB COMMENT='Entidad principal de telecomunicaciones';

CREATE TABLE `plan_types` (
  `plan_type_id` INT PRIMARY KEY,
  `type_name` VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB COMMENT='Clasificación del catálogo';

CREATE TABLE `plans` (
  `plan_id` INT PRIMARY KEY,
  `plan_name` VARCHAR(140) NOT NULL,
  `monthly_fee` DECIMAL(12,2) NOT NULL,
  `plan_type_id` INT NOT NULL,
  CONSTRAINT fk_plans_plan_types
    FOREIGN KEY (`plan_type_id`) REFERENCES `plan_types` (`plan_type_id`),
  INDEX idx_plans_plan_type_id (`plan_type_id`)
) ENGINE=InnoDB COMMENT='Catálogo de plans';

CREATE TABLE `invoices` (
  `invoice_id` INT PRIMARY KEY,
  `subscriber_id` INT NOT NULL,
  `invoice_date` DATE NOT NULL,
  `status` VARCHAR(24) NOT NULL,
  `total_due` DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_invoices_subscribers
    FOREIGN KEY (`subscriber_id`) REFERENCES `subscribers` (`subscriber_id`),
  INDEX idx_invoices_main_date (`subscriber_id`, `invoice_date`),
  INDEX idx_invoices_status (`status`)
) ENGINE=InnoDB COMMENT='Transacciones de facturas';

CREATE TABLE `invoice_lines` (
  `invoice_id` INT NOT NULL,
  `plan_id` INT NOT NULL,
  `months` INT NOT NULL,
  `unit_fee` DECIMAL(12,2) NOT NULL,
  PRIMARY KEY (`invoice_id`, `plan_id`),
  CONSTRAINT fk_invoice_lines_invoices
    FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`invoice_id`),
  CONSTRAINT fk_invoice_lines_plans
    FOREIGN KEY (`plan_id`) REFERENCES `plans` (`plan_id`),
  INDEX idx_invoice_lines_plan_id (`plan_id`)
) ENGINE=InnoDB COMMENT='Detalle de cada factura';
