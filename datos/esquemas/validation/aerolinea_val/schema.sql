CREATE TABLE `passengers` (
  `passenger_id` INT PRIMARY KEY,
  `passenger_name` VARCHAR(120) NOT NULL,
  `country` VARCHAR(80) NOT NULL,
  created_at DATE NOT NULL,
  INDEX idx_passengers_country (`country`)
) ENGINE=InnoDB COMMENT='Entidad principal de aerolínea';

CREATE TABLE `fare_classes` (
  `fare_class_id` INT PRIMARY KEY,
  `class_name` VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB COMMENT='Clasificación del catálogo';

CREATE TABLE `flights` (
  `flight_id` INT PRIMARY KEY,
  `flight_code` VARCHAR(140) NOT NULL,
  `base_fare` DECIMAL(12,2) NOT NULL,
  `fare_class_id` INT NOT NULL,
  CONSTRAINT fk_flights_fare_classes
    FOREIGN KEY (`fare_class_id`) REFERENCES `fare_classes` (`fare_class_id`),
  INDEX idx_flights_fare_class_id (`fare_class_id`)
) ENGINE=InnoDB COMMENT='Catálogo de vuelos';

CREATE TABLE `bookings` (
  `booking_id` INT PRIMARY KEY,
  `passenger_id` INT NOT NULL,
  `booking_date` DATE NOT NULL,
  `status` VARCHAR(24) NOT NULL,
  `total_amount` DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_bookings_passengers
    FOREIGN KEY (`passenger_id`) REFERENCES `passengers` (`passenger_id`),
  INDEX idx_bookings_main_date (`passenger_id`, `booking_date`),
  INDEX idx_bookings_status (`status`)
) ENGINE=InnoDB COMMENT='Transacciones de reservas';

CREATE TABLE `booking_flights` (
  `booking_id` INT NOT NULL,
  `flight_id` INT NOT NULL,
  `seats` INT NOT NULL,
  `unit_fare` DECIMAL(12,2) NOT NULL,
  PRIMARY KEY (`booking_id`, `flight_id`),
  CONSTRAINT fk_booking_flights_bookings
    FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`booking_id`),
  CONSTRAINT fk_booking_flights_flights
    FOREIGN KEY (`flight_id`) REFERENCES `flights` (`flight_id`),
  INDEX idx_booking_flights_flight_id (`flight_id`)
) ENGINE=InnoDB COMMENT='Detalle de cada reserva';
