CREATE TABLE `guests` (
  `guest_id` INT PRIMARY KEY,
  `guest_name` VARCHAR(120) NOT NULL,
  `country` VARCHAR(80) NOT NULL,
  created_at DATE NOT NULL,
  INDEX idx_guests_country (`country`)
) ENGINE=InnoDB COMMENT='Entidad principal de hotel';

CREATE TABLE `room_types` (
  `room_type_id` INT PRIMARY KEY,
  `type_name` VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB COMMENT='Clasificación del catálogo';

CREATE TABLE `rooms` (
  `room_id` INT PRIMARY KEY,
  `room_name` VARCHAR(140) NOT NULL,
  `nightly_rate` DECIMAL(12,2) NOT NULL,
  `room_type_id` INT NOT NULL,
  CONSTRAINT fk_rooms_room_types
    FOREIGN KEY (`room_type_id`) REFERENCES `room_types` (`room_type_id`),
  INDEX idx_rooms_room_type_id (`room_type_id`)
) ENGINE=InnoDB COMMENT='Catálogo de habitacións';

CREATE TABLE `reservations` (
  `reservation_id` INT PRIMARY KEY,
  `guest_id` INT NOT NULL,
  `check_in` DATE NOT NULL,
  `status` VARCHAR(24) NOT NULL,
  `total_amount` DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_reservations_guests
    FOREIGN KEY (`guest_id`) REFERENCES `guests` (`guest_id`),
  INDEX idx_reservations_main_date (`guest_id`, `check_in`),
  INDEX idx_reservations_status (`status`)
) ENGINE=InnoDB COMMENT='Transacciones de reservacións';

CREATE TABLE `reservation_rooms` (
  `reservation_id` INT NOT NULL,
  `room_id` INT NOT NULL,
  `nights` INT NOT NULL,
  `nightly_rate` DECIMAL(12,2) NOT NULL,
  PRIMARY KEY (`reservation_id`, `room_id`),
  CONSTRAINT fk_reservation_rooms_reservations
    FOREIGN KEY (`reservation_id`) REFERENCES `reservations` (`reservation_id`),
  CONSTRAINT fk_reservation_rooms_rooms
    FOREIGN KEY (`room_id`) REFERENCES `rooms` (`room_id`),
  INDEX idx_reservation_rooms_room_id (`room_id`)
) ENGINE=InnoDB COMMENT='Detalle de cada reservación';
