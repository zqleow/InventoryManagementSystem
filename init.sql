CREATE DATABASE IF NOT EXISTS `inventory`;
USE `inventory`;

CREATE TABLE IF NOT EXISTS `items` (
  `id` binary(16) NOT NULL,
  `name` varchar(255) NOT NULL,
  `category` varchar(255) NOT NULL,
  `price` varchar(10) NOT NULL,
  `last_updated_dt` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
