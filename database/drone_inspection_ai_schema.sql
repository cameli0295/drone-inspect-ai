-- MySQL dump 10.13  Distrib 9.5.0, for Win64 (x86_64)
--
-- Host: localhost    Database: drone_inspection_ai
-- ------------------------------------------------------
-- Server version	9.5.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `datasets`
--

DROP TABLE IF EXISTS `datasets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `datasets` (
  `dataset_id` int NOT NULL AUTO_INCREMENT,
  `dataset_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `total_images` int DEFAULT NULL,
  `source` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`dataset_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `defect_classes`
--

DROP TABLE IF EXISTS `defect_classes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `defect_classes` (
  `class_id` int NOT NULL AUTO_INCREMENT,
  `class_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `severity` enum('Faible','Moyenne','Élevée','Critique') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`class_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `drones`
--

DROP TABLE IF EXISTS `drones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `drones` (
  `drone_id` int NOT NULL AUTO_INCREMENT,
  `drone_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `drone_model` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `camera_resolution` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `max_flight_time` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`drone_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inspection_images`
--

DROP TABLE IF EXISTS `inspection_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inspection_images` (
  `image_id` int NOT NULL AUTO_INCREMENT,
  `inspection_id` int DEFAULT NULL,
  `dataset_id` int DEFAULT NULL,
  `image_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `image_path` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `upload_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`image_id`),
  KEY `dataset_id` (`dataset_id`),
  KEY `fk_images_inspection` (`inspection_id`),
  CONSTRAINT `fk_images_inspection` FOREIGN KEY (`inspection_id`) REFERENCES `inspections` (`inspection_id`),
  CONSTRAINT `inspection_images_ibfk_1` FOREIGN KEY (`dataset_id`) REFERENCES `datasets` (`dataset_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inspection_reports`
--

DROP TABLE IF EXISTS `inspection_reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inspection_reports` (
  `report_id` int NOT NULL AUTO_INCREMENT,
  `prediction_id` int DEFAULT NULL,
  `intervention_priority` enum('Faible','Moyenne','Élevée','Critique') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `recommendation` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`report_id`),
  KEY `prediction_id` (`prediction_id`),
  CONSTRAINT `inspection_reports_ibfk_1` FOREIGN KEY (`prediction_id`) REFERENCES `predictions` (`prediction_id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inspections`
--

DROP TABLE IF EXISTS `inspections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inspections` (
  `inspection_id` int NOT NULL AUTO_INCREMENT,
  `drone_id` int DEFAULT NULL,
  `inspection_date` date NOT NULL,
  `location` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `infrastructure_type` enum('Pont','Toiture','Pylône','Bâtiment','Autre') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `inspector_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `weather_conditions` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` enum('Planifiée','En cours','Terminée','Annulée') COLLATE utf8mb4_unicode_ci DEFAULT 'Planifiée',
  `description` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`inspection_id`),
  KEY `drone_id` (`drone_id`),
  CONSTRAINT `inspections_ibfk_1` FOREIGN KEY (`drone_id`) REFERENCES `drones` (`drone_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `logs`
--

DROP TABLE IF EXISTS `logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `logs` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `action_type` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_description` text COLLATE utf8mb4_unicode_ci,
  `action_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `models`
--

DROP TABLE IF EXISTS `models`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `models` (
  `model_id` int NOT NULL AUTO_INCREMENT,
  `model_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model_type` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `dataset_id` int DEFAULT NULL,
  `task_type` enum('Classification binaire','Classification multiclasses') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `input_size` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `classes_count` int DEFAULT NULL,
  `model_path` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `accuracy` decimal(5,2) DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`model_id`),
  KEY `dataset_id` (`dataset_id`),
  CONSTRAINT `models_ibfk_1` FOREIGN KEY (`dataset_id`) REFERENCES `datasets` (`dataset_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `predictions`
--

DROP TABLE IF EXISTS `predictions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `predictions` (
  `prediction_id` int NOT NULL AUTO_INCREMENT,
  `image_id` int DEFAULT NULL,
  `model_id` int DEFAULT NULL,
  `predicted_class` int DEFAULT NULL,
  `confidence` decimal(5,2) DEFAULT NULL,
  `prediction_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`prediction_id`),
  KEY `image_id` (`image_id`),
  KEY `predicted_class` (`predicted_class`),
  KEY `fk_predictions_model` (`model_id`),
  CONSTRAINT `fk_predictions_model` FOREIGN KEY (`model_id`) REFERENCES `models` (`model_id`),
  CONSTRAINT `predictions_ibfk_1` FOREIGN KEY (`image_id`) REFERENCES `inspection_images` (`image_id`),
  CONSTRAINT `predictions_ibfk_2` FOREIGN KEY (`predicted_class`) REFERENCES `defect_classes` (`class_id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `role` enum('Administrateur','Inspecteur','Observateur') COLLATE utf8mb4_unicode_ci DEFAULT 'Inspecteur',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-01  9:57:16
