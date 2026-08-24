-- MySQL dump 10.13  Distrib 9.5.0, for Win64 (x86_64)
--
-- Host: localhost    Database: drone_inspection_ai_demo_build
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
  `dataset_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `total_images` int DEFAULT NULL,
  `source` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`dataset_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `datasets`
--

LOCK TABLES `datasets` WRITE;
/*!40000 ALTER TABLE `datasets` DISABLE KEYS */;
INSERT INTO `datasets` VALUES (1,'Surface Crack Detection','Dataset de classification binaire des fissures',40000,'https://www.kaggle.com/datasets/arunrk7/surface-crack-detection','2026-07-06 14:15:09'),(2,'CODEBRIM','Dataset de classification multiclasses des défauts de béton',1590,'https://zenodo.org/record/2620293','2026-07-06 14:15:09');
/*!40000 ALTER TABLE `datasets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `defect_classes`
--

DROP TABLE IF EXISTS `defect_classes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `defect_classes` (
  `class_id` int NOT NULL AUTO_INCREMENT,
  `class_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `severity` enum('Faible','Moyenne','Élevée','Critique') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`class_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `defect_classes`
--

LOCK TABLES `defect_classes` WRITE;
/*!40000 ALTER TABLE `defect_classes` DISABLE KEYS */;
INSERT INTO `defect_classes` VALUES (1,'No Crack','Faible','Aucune fissure détectée'),(2,'Crack','Moyenne','Présence de fissures sur la surface'),(3,'Corrosion','Élevée','Corrosion des éléments métalliques'),(4,'Efflorescence','Faible','Dépôts blanchâtres dus aux sels minéraux'),(5,'Spallation','Critique','Éclatement ou détachement du béton'),(6,'Exposed Rebar','Critique','Armatures métalliques visibles'),(7,'Honeycombing','Élevée','Présence de nids de gravier dans le béton');
/*!40000 ALTER TABLE `defect_classes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `drones`
--

DROP TABLE IF EXISTS `drones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `drones` (
  `drone_id` int NOT NULL AUTO_INCREMENT,
  `drone_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `drone_model` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `camera_resolution` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `max_flight_time` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`drone_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `drones`
--

LOCK TABLES `drones` WRITE;
/*!40000 ALTER TABLE `drones` DISABLE KEYS */;
INSERT INTO `drones` VALUES (1,'DroneInspect-01','DJI Matrice 300 RTK','20 MP','55 minutes','Drone professionnel utilisé pour les inspections visuelles des infrastructures.','2026-07-06 15:10:34');
/*!40000 ALTER TABLE `drones` ENABLE KEYS */;
UNLOCK TABLES;

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
  `image_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `image_path` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `upload_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`image_id`),
  KEY `dataset_id` (`dataset_id`),
  KEY `fk_images_inspection` (`inspection_id`),
  CONSTRAINT `fk_images_inspection` FOREIGN KEY (`inspection_id`) REFERENCES `inspections` (`inspection_id`),
  CONSTRAINT `inspection_images_ibfk_1` FOREIGN KEY (`dataset_id`) REFERENCES `datasets` (`dataset_id`)
) ENGINE=InnoDB AUTO_INCREMENT=20021 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inspection_images`
--

LOCK TABLES `inspection_images` WRITE;
/*!40000 ALTER TABLE `inspection_images` DISABLE KEYS */;
INSERT INTO `inspection_images` VALUES (1,1,1,'crack_001.jpg','datasets/SurfaceCrackDetection/Positive/crack_001.jpg','2026-07-06 15:20:16'),(2,1,1,'no_crack_001.jpg','datasets/SurfaceCrackDetection/Negative/no_crack_001.jpg','2026-07-06 15:20:16'),(3,1,2,'bridge_001.jpg','datasets/CODEBRIM/bridge_001.jpg','2026-07-06 15:20:16'),(4,1,2,'bridge_002.jpg','datasets/CODEBRIM/bridge_002.jpg','2026-07-06 15:20:16'),(5,1,2,'bridge_003.jpg','datasets/CODEBRIM/bridge_003.jpg','2026-07-06 15:20:16'),(6,2,1,'inspection_2_20260714_090300_678081.png','uploads\\inspection_2_20260714_090300_678081.png','2026-07-14 07:03:00'),(7,2,1,'inspection_2_20260714_090302_291566.png','uploads\\inspection_2_20260714_090302_291566.png','2026-07-14 07:03:02'),(8,1,1,'inspection_1_20260714_094458_612133.png','uploads\\inspection_1_20260714_094458_612133.png','2026-07-14 07:45:05'),(9,1,2,'inspection_1_20260714_094915_716330.png','uploads\\inspection_1_20260714_094915_716330.png','2026-07-14 07:49:33'),(10,2,1,'inspection_2_20260714_095227_385826.png','uploads\\inspection_2_20260714_095227_385826.png','2026-07-14 07:52:29'),(11,2,2,'inspection_2_20260714_095251_806617.png','uploads\\inspection_2_20260714_095251_806617.png','2026-07-14 07:52:55'),(12,2,1,'inspection_2_20260714_095328_561170.png','uploads\\inspection_2_20260714_095328_561170.png','2026-07-14 07:53:30'),(13,2,2,'inspection_2_20260714_095400_209767.png','uploads\\inspection_2_20260714_095400_209767.png','2026-07-14 07:54:04'),(14,2,2,'inspection_2_20260714_163056_004053.png','uploads/inspection_2_20260714_163056_004053.png','2026-07-14 14:30:56'),(15,2,1,'inspection_2_20260714_172426_979149.png','uploads/inspection_2_20260714_172426_979149.png','2026-07-14 15:24:27'),(16,2,1,'inspection_2_20260714_172442_867018.png','uploads/inspection_2_20260714_172442_867018.png','2026-07-14 15:24:43'),(17,2,2,'inspection_2_20260714_172527_544811.png','uploads/inspection_2_20260714_172527_544811.png','2026-07-14 15:25:28'),(18,2,2,'inspection_2_20260715_093315_077340.png','uploads/inspection_2_20260715_093315_077340.png','2026-07-15 07:33:15'),(19,2,2,'inspection_2_20260715_110755_509808.png','uploads/inspection_2_20260715_110755_509808.png','2026-07-15 09:07:56'),(20,1,2,'flask_inspection_1_20260801_095610_df9c6824.png','uploads/flask_inspection_1_20260801_095610_df9c6824.png','2026-08-01 07:56:10');
/*!40000 ALTER TABLE `inspection_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inspection_reports`
--

DROP TABLE IF EXISTS `inspection_reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inspection_reports` (
  `report_id` int NOT NULL AUTO_INCREMENT,
  `prediction_id` int DEFAULT NULL,
  `intervention_priority` enum('Faible','Moyenne','Élevée','Critique') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `recommendation` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`report_id`),
  KEY `prediction_id` (`prediction_id`),
  KEY `idx_reports_priority` (`intervention_priority`),
  CONSTRAINT `inspection_reports_ibfk_1` FOREIGN KEY (`prediction_id`) REFERENCES `predictions` (`prediction_id`)
) ENGINE=InnoDB AUTO_INCREMENT=20030 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inspection_reports`
--

LOCK TABLES `inspection_reports` WRITE;
/*!40000 ALTER TABLE `inspection_reports` DISABLE KEYS */;
INSERT INTO `inspection_reports` VALUES (1,1,'Moyenne','Surveiller la fissure et programmer une inspection de contrôle.','2026-07-06 15:27:49'),(2,2,'Faible','Aucune intervention nécessaire.','2026-07-06 15:27:49'),(3,3,'Élevée','Prévoir un traitement anticorrosion rapidement.','2026-07-06 15:27:49'),(4,4,'Critique','Réparer immédiatement la zone présentant un Éclatement du béton.','2026-07-06 15:27:49'),(5,5,'Critique','Inspection structurelle urgente des armatures apparentes.','2026-07-06 15:27:49'),(6,6,'Moyenne','Une fissure a été détectée. Une inspection humaine complémentaire est recommandée.','2026-07-14 07:45:05'),(7,7,'Critique','Sécuriser la zone et programmer rapidement une réparation du béton détérioré.','2026-07-14 07:49:33'),(8,8,'Faible','Contrôler l\'origine de l\'humidité et surveiller l\'évolution des dépôts.','2026-07-14 07:49:33'),(9,9,'Élevée','Prévoir rapidement un diagnostic et un traitement anticorrosion.','2026-07-14 07:49:33'),(10,10,'Moyenne','Une fissure a été détectée. Une inspection humaine complémentaire est recommandée.','2026-07-14 07:52:29'),(11,11,'Faible','Aucun défaut structurel significatif détecté.','2026-07-14 07:52:55'),(12,12,'Moyenne','Une fissure a été détectée. Une inspection humaine complémentaire est recommandée.','2026-07-14 07:53:30'),(13,13,'Faible','Aucun défaut structurel significatif détecté.','2026-07-14 07:54:04'),(14,14,'Moyenne','Une fissure a été détectée. Une classification détaillée des défauts est lancée automatiquement.','2026-07-14 14:30:57'),(15,15,'Faible','Aucun défaut structurel significatif détecté.','2026-07-14 14:30:57'),(16,16,'Faible','Aucune fissure significative détectée. Aucune intervention immédiate.','2026-07-14 15:24:27'),(17,17,'Faible','Aucune fissure significative détectée. Aucune intervention immédiate.','2026-07-14 15:24:43'),(18,18,'Moyenne','Une fissure a été détectée. Une classification détaillée des défauts est lancée automatiquement.','2026-07-14 15:25:28'),(19,19,'Critique','Sécuriser la zone et programmer rapidement une réparation du béton détérioré.','2026-07-14 15:25:29'),(20,20,'Élevée','Prévoir rapidement un diagnostic et un traitement anticorrosion.','2026-07-14 15:25:29'),(21,21,'Faible','Contrôler l\'origine de l\'humidité et surveiller l\'évolution des dépôts.','2026-07-14 15:25:29'),(22,22,'Moyenne','Une fissure a été détectée. Une classification détaillée des défauts est lancée automatiquement.','2026-07-15 07:33:15'),(23,23,'Élevée','Prévoir rapidement un diagnostic et un traitement anticorrosion.','2026-07-15 07:33:16'),(24,24,'Moyenne','Une fissure a été détectée. Une classification détaillée des défauts est lancée automatiquement.','2026-07-15 09:07:56'),(25,25,'Élevée','Prévoir rapidement un diagnostic et un traitement anticorrosion.','2026-07-15 09:07:56'),(26,26,'Moyenne','Une fissure a été détectée ; le niveau 2 est lancé.','2026-08-01 07:56:10'),(27,27,'Critique','Sécuriser la zone et programmer rapidement une réparation du béton détérioré.','2026-08-01 07:56:10'),(28,28,'Élevée','Prévoir rapidement un diagnostic et un traitement anticorrosion.','2026-08-01 07:56:10'),(29,29,'Faible','Contrôler l\'origine de l\'humidité et surveiller l\'évolution des dépôts.','2026-08-01 07:56:10');
/*!40000 ALTER TABLE `inspection_reports` ENABLE KEYS */;
UNLOCK TABLES;

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
  `location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `infrastructure_type` enum('Pont','Toiture','Pylône','Bâtiment','Autre') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `inspector_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `weather_conditions` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` enum('Planifiée','En cours','Terminée','Annulée') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'Planifiée',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`inspection_id`),
  KEY `drone_id` (`drone_id`),
  CONSTRAINT `inspections_ibfk_1` FOREIGN KEY (`drone_id`) REFERENCES `drones` (`drone_id`)
) ENGINE=InnoDB AUTO_INCREMENT=214 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inspections`
--

LOCK TABLES `inspections` WRITE;
/*!40000 ALTER TABLE `inspections` DISABLE KEYS */;
INSERT INTO `inspections` VALUES (1,1,'2026-07-06','Pont urbain - Île-de-France','Pont','Inspecteur Démo','Ciel dégagé','Terminée','Mission d'inspection réalisée pour analyser l'état visuel d'un pont à partir d'images capturées par drone.','2026-07-06 15:10:34'),(2,1,'2026-07-14','Affiche les communes ayant plus de 20 mutations en 2023','Bâtiment','Inspecteur Démo','','Planifiée','','2026-07-14 06:49:24'),(3,1,'2026-08-01','Pont de démonstration - Paris 12e','Pont','Inspecteur Démo','Temps clair','Planifiée','Import de démonstration CSV pour la thèse','2026-08-01 07:55:27'),(4,1,'2026-08-02','Bâtiment de démonstration - Saint-Denis','Bâtiment','Inspecteur Démo','Couvert','Planifiée','Import de démonstration JSON pour la thèse','2026-08-01 07:55:27'),(5,1,'2026-08-01','Pont de démonstration - Paris 12e','Pont','Inspecteur Démo','Temps clair','Planifiée','Import de démonstration CSV pour la thèse','2026-08-01 07:55:27'),(6,1,'2026-07-01','Site synthétique 0','Autre','Inspecteur Démo','Ciel dégagé','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(7,1,'2026-03-25','Site synthétique 1','Toiture','Inspecteur Démo','Nuageux','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(8,1,'2026-06-06','Site synthétique 2','Pont','Inspecteur Démo','Nuageux','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(9,1,'2026-02-04','Site synthétique 3','Toiture','Inspecteur Démo','Vent modéré','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(10,1,'2026-04-25','Site synthétique 4','Toiture','Inspecteur Démo','Vent modéré','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(11,1,'2026-07-22','Site synthétique 5','Toiture','Inspecteur Démo','Pluie légère','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(12,1,'2026-02-27','Site synthétique 6','Pylône','Inspecteur Démo','Pluie légère','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(13,1,'2026-01-10','Site synthétique 7','Pont','Inspecteur Démo','Ciel dégagé','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(14,1,'2026-02-06','Site synthétique 8','Pylône','Inspecteur Démo','Vent modéré','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(15,1,'2026-02-18','Site synthétique 9','Pont','Inspecteur Démo','Pluie légère','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(16,1,'2026-06-10','Site synthétique 10','Bâtiment','Inspecteur Démo','Ciel dégagé','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(17,1,'2026-01-16','Site synthétique 11','Toiture','Inspecteur Démo','Nuageux','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(18,1,'2026-01-24','Site synthétique 12','Pont','Inspecteur Démo','Ciel dégagé','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(19,1,'2026-02-21','Site synthétique 13','Pylône','Inspecteur Démo','Nuageux','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(20,1,'2026-06-13','Site synthétique 14','Bâtiment','Inspecteur Démo','Vent modéré','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(21,1,'2026-01-08','Site synthétique 15','Pylône','Inspecteur Démo','Ciel dégagé','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(22,1,'2026-06-09','Site synthétique 16','Pont','Inspecteur Démo','Pluie légère','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(23,1,'2026-07-17','Site synthétique 17','Pylône','Inspecteur Démo','Ciel dégagé','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(24,1,'2026-03-05','Site synthétique 18','Bâtiment','Inspecteur Démo','Ciel dégagé','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(25,1,'2026-01-15','Site synthétique 19','Toiture','Inspecteur Démo','Nuageux','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(26,1,'2026-04-06','Site synthétique 20','Autre','Inspecteur Démo','Nuageux','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(27,1,'2026-05-25','Site synthétique 21','Autre','Inspecteur Démo','Vent modéré','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(28,1,'2026-01-28','Site synthétique 22','Pylône','Inspecteur Démo','Ciel dégagé','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(29,1,'2026-06-10','Site synthétique 23','Toiture','Inspecteur Démo','Nuageux','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(30,1,'2026-05-18','Site synthétique 24','Toiture','Inspecteur Démo','Vent modéré','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(31,1,'2026-06-20','Site synthétique 25','Pylône','Inspecteur Démo','Vent modéré','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(32,1,'2026-04-06','Site synthétique 26','Autre','Inspecteur Démo','Ciel dégagé','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(33,1,'2026-03-22','Site synthétique 27','Toiture','Inspecteur Démo','Ciel dégagé','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(34,1,'2026-04-23','Site synthétique 28','Pont','Inspecteur Démo','Vent modéré','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(35,1,'2026-06-16','Site synthétique 29','Pylône','Inspecteur Démo','Vent modéré','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(36,1,'2026-01-07','Site synthétique 30','Pylône','Inspecteur Démo','Vent modéré','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(37,1,'2026-02-07','Site synthétique 31','Toiture','Inspecteur Démo','Nuageux','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(38,1,'2026-05-18','Site synthétique 32','Autre','Inspecteur Démo','Nuageux','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(39,1,'2026-01-04','Site synthétique 33','Bâtiment','Inspecteur Démo','Pluie légère','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(40,1,'2026-04-20','Site synthétique 34','Toiture','Inspecteur Démo','Ciel dégagé','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(41,1,'2026-03-25','Site synthétique 35','Pylône','Inspecteur Démo','Nuageux','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(42,1,'2026-01-02','Site synthétique 36','Autre','Inspecteur Démo','Vent modéré','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(43,1,'2026-07-22','Site synthétique 37','Bâtiment','Inspecteur Démo','Nuageux','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(44,1,'2026-02-08','Site synthétique 38','Toiture','Inspecteur Démo','Nuageux','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(45,1,'2026-01-24','Site synthétique 39','Pont','Inspecteur Démo','Nuageux','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(46,1,'2026-04-21','Site synthétique 40','Autre','Inspecteur Démo','Nuageux','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(47,1,'2026-06-16','Site synthétique 41','Toiture','Inspecteur Démo','Nuageux','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(48,1,'2026-06-04','Site synthétique 42','Autre','Inspecteur Démo','Vent modéré','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(49,1,'2026-06-02','Site synthétique 43','Toiture','Inspecteur Démo','Nuageux','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(50,1,'2026-04-06','Site synthétique 44','Autre','Inspecteur Démo','Nuageux','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(51,1,'2026-06-13','Site synthétique 45','Pont','Inspecteur Démo','Vent modéré','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(52,1,'2026-03-21','Site synthétique 46','Toiture','Inspecteur Démo','Vent modéré','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(53,1,'2026-02-25','Site synthétique 47','Autre','Inspecteur Démo','Pluie légère','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(54,1,'2026-03-18','Site synthétique 48','Toiture','Inspecteur Démo','Nuageux','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(55,1,'2026-04-21','Site synthétique 49','Toiture','Inspecteur Démo','Pluie légère','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(56,1,'2026-03-17','Site synthétique 50','Autre','Inspecteur Démo','Pluie légère','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(57,1,'2026-05-13','Site synthétique 51','Pont','Inspecteur Démo','Ciel dégagé','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(58,1,'2026-03-15','Site synthétique 52','Autre','Inspecteur Démo','Nuageux','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(59,1,'2026-04-22','Site synthétique 53','Autre','Inspecteur Démo','Ciel dégagé','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(60,1,'2026-07-24','Site synthétique 54','Autre','Inspecteur Démo','Pluie légère','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(61,1,'2026-07-24','Site synthétique 55','Pylône','Inspecteur Démo','Ciel dégagé','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(62,1,'2026-01-26','Site synthétique 56','Pylône','Inspecteur Démo','Vent modéré','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(63,1,'2026-03-08','Site synthétique 57','Bâtiment','Inspecteur Démo','Nuageux','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(64,1,'2026-05-02','Site synthétique 58','Toiture','Inspecteur Démo','Nuageux','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(65,1,'2026-07-27','Site synthétique 59','Toiture','Inspecteur Démo','Ciel dégagé','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(66,1,'2026-05-15','Site synthétique 60','Toiture','Inspecteur Démo','Vent modéré','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(67,1,'2026-01-18','Site synthétique 61','Bâtiment','Inspecteur Démo','Ciel dégagé','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(68,1,'2026-04-13','Site synthétique 62','Toiture','Inspecteur Démo','Vent modéré','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(69,1,'2026-07-18','Site synthétique 63','Pylône','Inspecteur Démo','Nuageux','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(70,1,'2026-01-08','Site synthétique 64','Bâtiment','Inspecteur Démo','Pluie légère','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(71,1,'2026-04-18','Site synthétique 65','Autre','Inspecteur Démo','Ciel dégagé','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(72,1,'2026-03-25','Site synthétique 66','Bâtiment','Inspecteur Démo','Vent modéré','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(73,1,'2026-03-27','Site synthétique 67','Pont','Inspecteur Démo','Pluie légère','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(74,1,'2026-04-13','Site synthétique 68','Autre','Inspecteur Démo','Ciel dégagé','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(75,1,'2026-07-06','Site synthétique 69','Pylône','Inspecteur Démo','Ciel dégagé','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(76,1,'2026-04-15','Site synthétique 70','Autre','Inspecteur Démo','Vent modéré','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(77,1,'2026-05-16','Site synthétique 71','Toiture','Inspecteur Démo','Vent modéré','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(78,1,'2026-05-25','Site synthétique 72','Toiture','Inspecteur Démo','Ciel dégagé','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(79,1,'2026-02-10','Site synthétique 73','Autre','Inspecteur Démo','Ciel dégagé','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(80,1,'2026-01-05','Site synthétique 74','Pylône','Inspecteur Démo','Ciel dégagé','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(81,1,'2026-04-11','Site synthétique 75','Pont','Inspecteur Démo','Ciel dégagé','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(82,1,'2026-01-10','Site synthétique 76','Toiture','Inspecteur Démo','Pluie légère','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(83,1,'2026-07-07','Site synthétique 77','Pylône','Inspecteur Démo','Ciel dégagé','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(84,1,'2026-07-13','Site synthétique 78','Pylône','Inspecteur Démo','Pluie légère','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(85,1,'2026-04-16','Site synthétique 79','Autre','Inspecteur Démo','Nuageux','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(86,1,'2026-01-12','Site synthétique 80','Bâtiment','Inspecteur Démo','Ciel dégagé','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(87,1,'2026-02-02','Site synthétique 81','Toiture','Inspecteur Démo','Pluie légère','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(88,1,'2026-02-09','Site synthétique 82','Pylône','Inspecteur Démo','Pluie légère','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(89,1,'2026-06-04','Site synthétique 83','Autre','Inspecteur Démo','Vent modéré','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(90,1,'2026-03-05','Site synthétique 84','Pylône','Inspecteur Démo','Vent modéré','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(91,1,'2026-06-14','Site synthétique 85','Autre','Inspecteur Démo','Pluie légère','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(92,1,'2026-06-17','Site synthétique 86','Autre','Inspecteur Démo','Pluie légère','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(93,1,'2026-04-10','Site synthétique 87','Pylône','Inspecteur Démo','Pluie légère','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(94,1,'2026-07-19','Site synthétique 88','Pont','Inspecteur Démo','Vent modéré','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(95,1,'2026-06-02','Site synthétique 89','Toiture','Inspecteur Démo','Vent modéré','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(96,1,'2026-05-22','Site synthétique 90','Pont','Inspecteur Démo','Vent modéré','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(97,1,'2026-05-26','Site synthétique 91','Bâtiment','Inspecteur Démo','Pluie légère','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(98,1,'2026-02-23','Site synthétique 92','Pylône','Inspecteur Démo','Vent modéré','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(99,1,'2026-05-06','Site synthétique 93','Autre','Inspecteur Démo','Pluie légère','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(100,1,'2026-03-16','Site synthétique 94','Bâtiment','Inspecteur Démo','Ciel dégagé','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(101,1,'2026-05-07','Site synthétique 95','Toiture','Inspecteur Démo','Vent modéré','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(102,1,'2026-01-23','Site synthétique 96','Autre','Inspecteur Démo','Ciel dégagé','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(103,1,'2026-07-08','Site synthétique 97','Pont','Inspecteur Démo','Vent modéré','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(104,1,'2026-03-20','Site synthétique 98','Pont','Inspecteur Démo','Pluie légère','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(105,1,'2026-05-10','Site synthétique 99','Toiture','Inspecteur Démo','Nuageux','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(106,1,'2026-05-07','Site synthétique 100','Pylône','Inspecteur Démo','Nuageux','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(107,1,'2026-02-05','Site synthétique 101','Toiture','Inspecteur Démo','Vent modéré','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(108,1,'2026-06-13','Site synthétique 102','Pylône','Inspecteur Démo','Vent modéré','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(109,1,'2026-07-19','Site synthétique 103','Autre','Inspecteur Démo','Pluie légère','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(110,1,'2026-01-22','Site synthétique 104','Pylône','Inspecteur Démo','Ciel dégagé','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(111,1,'2026-02-19','Site synthétique 105','Pont','Inspecteur Démo','Pluie légère','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(112,1,'2026-01-12','Site synthétique 106','Autre','Inspecteur Démo','Vent modéré','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(113,1,'2026-06-23','Site synthétique 107','Pont','Inspecteur Démo','Ciel dégagé','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(114,1,'2026-04-22','Site synthétique 108','Pylône','Inspecteur Démo','Vent modéré','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(115,1,'2026-03-04','Site synthétique 109','Pont','Inspecteur Démo','Nuageux','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(116,1,'2026-05-07','Site synthétique 110','Autre','Inspecteur Démo','Vent modéré','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(117,1,'2026-01-24','Site synthétique 111','Autre','Inspecteur Démo','Vent modéré','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(118,1,'2026-03-27','Site synthétique 112','Pylône','Inspecteur Démo','Vent modéré','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(119,1,'2026-06-10','Site synthétique 113','Toiture','Inspecteur Démo','Ciel dégagé','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(120,1,'2026-01-26','Site synthétique 114','Autre','Inspecteur Démo','Nuageux','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(121,1,'2026-07-06','Site synthétique 115','Pylône','Inspecteur Démo','Vent modéré','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(122,1,'2026-07-04','Site synthétique 116','Pylône','Inspecteur Démo','Ciel dégagé','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(123,1,'2026-05-22','Site synthétique 117','Autre','Inspecteur Démo','Nuageux','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(124,1,'2026-06-25','Site synthétique 118','Pylône','Inspecteur Démo','Pluie légère','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(125,1,'2026-03-20','Site synthétique 119','Toiture','Inspecteur Démo','Vent modéré','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(126,1,'2026-01-05','Site synthétique 120','Bâtiment','Inspecteur Démo','Pluie légère','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(127,1,'2026-04-02','Site synthétique 121','Toiture','Inspecteur Démo','Vent modéré','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(128,1,'2026-02-15','Site synthétique 122','Pylône','Inspecteur Démo','Pluie légère','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(129,1,'2026-07-12','Site synthétique 123','Pylône','Inspecteur Démo','Nuageux','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(130,1,'2026-01-18','Site synthétique 124','Pont','Inspecteur Démo','Vent modéré','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(131,1,'2026-06-05','Site synthétique 125','Toiture','Inspecteur Démo','Pluie légère','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(132,1,'2026-02-17','Site synthétique 126','Autre','Inspecteur Démo','Vent modéré','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(133,1,'2026-04-04','Site synthétique 127','Pylône','Inspecteur Démo','Nuageux','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(134,1,'2026-05-26','Site synthétique 128','Autre','Inspecteur Démo','Vent modéré','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(135,1,'2026-05-07','Site synthétique 129','Autre','Inspecteur Démo','Pluie légère','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(136,1,'2026-02-27','Site synthétique 130','Toiture','Inspecteur Démo','Vent modéré','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(137,1,'2026-06-27','Site synthétique 131','Bâtiment','Inspecteur Démo','Nuageux','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(138,1,'2026-07-12','Site synthétique 132','Toiture','Inspecteur Démo','Nuageux','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(139,1,'2026-07-17','Site synthétique 133','Bâtiment','Inspecteur Démo','Vent modéré','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(140,1,'2026-02-01','Site synthétique 134','Autre','Inspecteur Démo','Nuageux','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(141,1,'2026-05-27','Site synthétique 135','Pylône','Inspecteur Démo','Vent modéré','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(142,1,'2026-02-20','Site synthétique 136','Autre','Inspecteur Démo','Pluie légère','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(143,1,'2026-01-03','Site synthétique 137','Pont','Inspecteur Démo','Pluie légère','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(144,1,'2026-03-14','Site synthétique 138','Pylône','Inspecteur Démo','Nuageux','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(145,1,'2026-06-04','Site synthétique 139','Toiture','Inspecteur Démo','Nuageux','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(146,1,'2026-03-11','Site synthétique 140','Autre','Inspecteur Démo','Pluie légère','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(147,1,'2026-05-06','Site synthétique 141','Toiture','Inspecteur Démo','Ciel dégagé','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(148,1,'2026-05-23','Site synthétique 142','Pont','Inspecteur Démo','Ciel dégagé','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(149,1,'2026-02-14','Site synthétique 143','Toiture','Inspecteur Démo','Ciel dégagé','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(150,1,'2026-06-11','Site synthétique 144','Autre','Inspecteur Démo','Ciel dégagé','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(151,1,'2026-02-15','Site synthétique 145','Autre','Inspecteur Démo','Nuageux','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(152,1,'2026-04-04','Site synthétique 146','Bâtiment','Inspecteur Démo','Ciel dégagé','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(153,1,'2026-02-28','Site synthétique 147','Pont','Inspecteur Démo','Pluie légère','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(154,1,'2026-07-13','Site synthétique 148','Pont','Inspecteur Démo','Vent modéré','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(155,1,'2026-03-15','Site synthétique 149','Pont','Inspecteur Démo','Nuageux','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(156,1,'2026-06-08','Site synthétique 150','Pylône','Inspecteur Démo','Nuageux','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(157,1,'2026-02-06','Site synthétique 151','Toiture','Inspecteur Démo','Pluie légère','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(158,1,'2026-02-21','Site synthétique 152','Pont','Inspecteur Démo','Ciel dégagé','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(159,1,'2026-03-02','Site synthétique 153','Pont','Inspecteur Démo','Nuageux','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(160,1,'2026-04-13','Site synthétique 154','Bâtiment','Inspecteur Démo','Nuageux','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(161,1,'2026-05-22','Site synthétique 155','Pylône','Inspecteur Démo','Nuageux','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(162,1,'2026-02-24','Site synthétique 156','Bâtiment','Inspecteur Démo','Ciel dégagé','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(163,1,'2026-04-20','Site synthétique 157','Pont','Inspecteur Démo','Nuageux','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(164,1,'2026-03-24','Site synthétique 158','Pylône','Inspecteur Démo','Vent modéré','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(165,1,'2026-05-17','Site synthétique 159','Pont','Inspecteur Démo','Vent modéré','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(166,1,'2026-02-07','Site synthétique 160','Toiture','Inspecteur Démo','Nuageux','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(167,1,'2026-07-06','Site synthétique 161','Pylône','Inspecteur Démo','Vent modéré','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(168,1,'2026-04-14','Site synthétique 162','Bâtiment','Inspecteur Démo','Pluie légère','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(169,1,'2026-04-24','Site synthétique 163','Pont','Inspecteur Démo','Nuageux','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(170,1,'2026-05-01','Site synthétique 164','Autre','Inspecteur Démo','Ciel dégagé','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(171,1,'2026-01-15','Site synthétique 165','Toiture','Inspecteur Démo','Vent modéré','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(172,1,'2026-03-13','Site synthétique 166','Autre','Inspecteur Démo','Vent modéré','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(173,1,'2026-06-20','Site synthétique 167','Pont','Inspecteur Démo','Ciel dégagé','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(174,1,'2026-04-28','Site synthétique 168','Pont','Inspecteur Démo','Pluie légère','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(175,1,'2026-03-09','Site synthétique 169','Pont','Inspecteur Démo','Nuageux','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(176,1,'2026-06-09','Site synthétique 170','Bâtiment','Inspecteur Démo','Ciel dégagé','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(177,1,'2026-07-10','Site synthétique 171','Toiture','Inspecteur Démo','Vent modéré','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(178,1,'2026-03-01','Site synthétique 172','Bâtiment','Inspecteur Démo','Pluie légère','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(179,1,'2026-03-15','Site synthétique 173','Pylône','Inspecteur Démo','Ciel dégagé','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(180,1,'2026-05-04','Site synthétique 174','Toiture','Inspecteur Démo','Ciel dégagé','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(181,1,'2026-05-10','Site synthétique 175','Pylône','Inspecteur Démo','Ciel dégagé','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(182,1,'2026-05-22','Site synthétique 176','Pylône','Inspecteur Démo','Pluie légère','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(183,1,'2026-01-18','Site synthétique 177','Autre','Inspecteur Démo','Pluie légère','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(184,1,'2026-01-13','Site synthétique 178','Autre','Inspecteur Démo','Vent modéré','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(185,1,'2026-03-01','Site synthétique 179','Bâtiment','Inspecteur Démo','Vent modéré','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(186,1,'2026-01-27','Site synthétique 180','Pylône','Inspecteur Démo','Vent modéré','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(187,1,'2026-03-25','Site synthétique 181','Autre','Inspecteur Démo','Vent modéré','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(188,1,'2026-06-09','Site synthétique 182','Bâtiment','Inspecteur Démo','Pluie légère','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(189,1,'2026-05-12','Site synthétique 183','Bâtiment','Inspecteur Démo','Vent modéré','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(190,1,'2026-03-13','Site synthétique 184','Autre','Inspecteur Démo','Pluie légère','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(191,1,'2026-05-22','Site synthétique 185','Bâtiment','Inspecteur Démo','Ciel dégagé','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(192,1,'2026-05-08','Site synthétique 186','Toiture','Inspecteur Démo','Pluie légère','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(193,1,'2026-01-26','Site synthétique 187','Pont','Inspecteur Démo','Vent modéré','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(194,1,'2026-06-11','Site synthétique 188','Pont','Inspecteur Démo','Vent modéré','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(195,1,'2026-04-20','Site synthétique 189','Bâtiment','Inspecteur Démo','Vent modéré','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(196,1,'2026-07-19','Site synthétique 190','Autre','Inspecteur Démo','Vent modéré','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(197,1,'2026-03-11','Site synthétique 191','Pont','Inspecteur Démo','Nuageux','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(198,1,'2026-05-05','Site synthétique 192','Pont','Inspecteur Démo','Vent modéré','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(199,1,'2026-04-20','Site synthétique 193','Toiture','Inspecteur Démo','Pluie légère','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(200,1,'2026-01-16','Site synthétique 194','Autre','Inspecteur Démo','Vent modéré','En cours','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(201,1,'2026-06-20','Site synthétique 195','Pont','Inspecteur Démo','Ciel dégagé','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(202,1,'2026-01-16','Site synthétique 196','Toiture','Inspecteur Démo','Pluie légère','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(203,1,'2026-04-28','Site synthétique 197','Pont','Inspecteur Démo','Nuageux','Terminée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(204,1,'2026-05-13','Site synthétique 198','Pylône','Inspecteur Démo','Nuageux','Annulée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(205,1,'2026-05-10','Site synthétique 199','Toiture','Inspecteur Démo','Nuageux','Planifiée','Inspection générée pour le benchmark SQL.','2026-08-02 07:18:00'),(206,1,'2026-07-10','Toiture entrepôt Saint-Denis','Toiture','Inspecteur Démo','Ciel dégagé','Terminée','Inspection de toiture suite à signalement d\'infiltration.','2026-08-02 07:38:58'),(207,1,'2026-07-12','Pylône ligne HT Bobigny','Pylône','Inspecteur Démo','Vent modéré','Planifiée','Contrôle périodique annuel du pylône.','2026-08-02 07:38:58'),(208,1,'2026-07-15','Pont RN2 Aulnay','Pont','Inspecteur Démo','Pluie légère','En cours','Inspection suite à alerte fissuration.','2026-08-02 07:38:58'),(209,1,'2026-07-18','Bâtiment industriel Pantin','Bâtiment','Inspecteur Démo','Ciel dégagé','Terminée','Contrôle de façade béton.','2026-08-02 07:38:58'),(210,1,'2026-07-10','Toiture entrepôt Saint-Denis','Toiture','Inspecteur Démo','Ciel dégagé','Terminée','Inspection de toiture suite à signalement d\'infiltration.','2026-08-02 07:56:38'),(211,1,'2026-07-12','Pylône ligne HT Bobigny','Pylône','Inspecteur Démo','Vent modéré','Planifiée','Contrôle périodique annuel du pylône.','2026-08-02 07:56:38'),(212,1,'2026-07-15','Pont RN2 Aulnay','Pont','Inspecteur Démo','Pluie légère','En cours','Inspection suite à alerte fissuration.','2026-08-02 07:56:38'),(213,1,'2026-07-18','Bâtiment industriel Pantin','Bâtiment','Inspecteur Démo','Ciel dégagé','Terminée','Contrôle de façade béton.','2026-08-02 07:56:38');
/*!40000 ALTER TABLE `inspections` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logs`
--

DROP TABLE IF EXISTS `logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `logs` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `action_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `action_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logs`
--

LOCK TABLES `logs` WRITE;
/*!40000 ALTER TABLE `logs` DISABLE KEYS */;
INSERT INTO `logs` VALUES (1,1,'Création base','Création de la base drone_inspection_ai','2026-07-06 15:39:05'),(2,1,'Ajout modèles','Ajout des modèles MobileNetV2 et EfficientNetB3','2026-07-06 15:39:05'),(3,1,'Prédiction','Exécution de prédictions de démonstration','2026-07-06 15:39:05'),(4,1,'Rapport','Génération des rapports d'inspection','2026-07-06 15:39:05'),(5,1,'Création inspection','Création de l\'inspection n°2 à Affiche les communes ayant plus de 20 mutations en 2023.','2026-07-14 06:49:24'),(6,1,'Import image','Ajout de l\'image n°6 pour l\'inspection n°2.','2026-07-14 07:03:00'),(7,1,'Import image','Ajout de l\'image n°7 pour l\'inspection n°2.','2026-07-14 07:03:02'),(8,1,'Prédiction IA','Analyse de l\'image n°8 avec MobileNetV2. 1 résultat(s) enregistré(s).','2026-07-14 07:45:05'),(9,1,'Prédiction IA','Analyse de l\'image n°9 avec EfficientNetB3. 3 résultat(s) enregistré(s).','2026-07-14 07:49:33'),(10,1,'Prédiction IA','Analyse de l\'image n°10 avec MobileNetV2. 1 résultat(s) enregistré(s).','2026-07-14 07:52:29'),(11,1,'Prédiction IA','Analyse de l\'image n°11 avec EfficientNetB3. 1 résultat(s) enregistré(s).','2026-07-14 07:52:55'),(12,1,'Prédiction IA','Analyse de l\'image n°12 avec MobileNetV2. 1 résultat(s) enregistré(s).','2026-07-14 07:53:30'),(13,1,'Prédiction IA','Analyse de l\'image n°13 avec EfficientNetB3. 1 résultat(s) enregistré(s).','2026-07-14 07:54:04'),(14,1,'Prédiction IA','Analyse automatique à deux niveaux de l\'image n°14. 2 prédiction(s) enregistrée(s).','2026-07-14 14:30:57'),(15,1,'Prédiction IA','Analyse automatique à deux niveaux de l\'image n°15. 1 prédiction(s) enregistrée(s).','2026-07-14 15:24:27'),(16,1,'Prédiction IA','Analyse automatique à deux niveaux de l\'image n°16. 1 prédiction(s) enregistrée(s).','2026-07-14 15:24:43'),(17,1,'Prédiction IA','Analyse automatique à deux niveaux de l\'image n°17. 4 prédiction(s) enregistrée(s).','2026-07-14 15:25:29'),(18,1,'Prédiction IA','Analyse automatique à deux niveaux de l\'image n°18. 2 prédiction(s) enregistrée(s).','2026-07-15 07:33:16'),(19,1,'Prédiction IA','Analyse automatique à deux niveaux de l\'image n°19. 2 prédiction(s) enregistrée(s).','2026-07-15 09:07:56'),(20,1,'Import inspections','1 inspection(s) importée(s) depuis inspections_import.csv.','2026-08-01 07:55:27'),(21,1,'Import inspections','1 inspection(s) importée(s) depuis inspections_import.json.','2026-08-01 07:55:27'),(22,1,'Import inspections','1 inspection(s) importée(s) depuis inspections_import.xlsx.','2026-08-01 07:55:27'),(23,1,'Prédiction Flask','Image 20 analysée via Flask ; 4 prédiction(s).','2026-08-01 07:56:10');
/*!40000 ALTER TABLE `logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `models`
--

DROP TABLE IF EXISTS `models`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `models` (
  `model_id` int NOT NULL AUTO_INCREMENT,
  `model_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `model_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `dataset_id` int DEFAULT NULL,
  `task_type` enum('Classification binaire','Classification multiclasses') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `input_size` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `classes_count` int DEFAULT NULL,
  `model_path` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `accuracy` decimal(5,2) DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`model_id`),
  KEY `dataset_id` (`dataset_id`),
  CONSTRAINT `models_ibfk_1` FOREIGN KEY (`dataset_id`) REFERENCES `datasets` (`dataset_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `models`
--

LOCK TABLES `models` WRITE;
/*!40000 ALTER TABLE `models` DISABLE KEYS */;
INSERT INTO `models` VALUES (1,'MobileNetV2','CNN Transfer Learning',1,'Classification binaire','224x224x3',2,'models/MobileNetV2_archive_structure_commente.keras',NULL,'Modèle utilisé pour détecter la présence ou l'absence de fissure à partir du dataset Surface Crack Detection.','2026-07-06 14:56:19'),(2,'EfficientNetB3','CNN Transfer Learning',2,'Classification multiclasses','300x300x3',6,'models/efficientnetb3_concrete_defects_corrige.keras',NULL,'Modèle utilisé pour classifier les défauts du dataset CODEBRIM : Crack, Corrosion, Efflorescence, Spallation, Exposed Rebar et Honeycombing.','2026-07-06 14:56:19');
/*!40000 ALTER TABLE `models` ENABLE KEYS */;
UNLOCK TABLES;

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
  KEY `idx_predictions_date` (`prediction_date`),
  CONSTRAINT `fk_predictions_model` FOREIGN KEY (`model_id`) REFERENCES `models` (`model_id`),
  CONSTRAINT `predictions_ibfk_1` FOREIGN KEY (`image_id`) REFERENCES `inspection_images` (`image_id`),
  CONSTRAINT `predictions_ibfk_2` FOREIGN KEY (`predicted_class`) REFERENCES `defect_classes` (`class_id`)
) ENGINE=InnoDB AUTO_INCREMENT=20030 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `predictions`
--

LOCK TABLES `predictions` WRITE;
/*!40000 ALTER TABLE `predictions` DISABLE KEYS */;
INSERT INTO `predictions` VALUES (1,1,1,2,98.70,'2026-07-06 15:25:22'),(2,2,1,1,99.10,'2026-07-06 15:25:22'),(3,3,2,3,96.40,'2026-07-06 15:25:22'),(4,4,2,5,94.80,'2026-07-06 15:25:22'),(5,5,2,6,97.20,'2026-07-06 15:25:22'),(6,8,1,2,100.00,'2026-07-14 07:45:05'),(7,9,2,5,62.93,'2026-07-14 07:49:33'),(8,9,2,4,36.07,'2026-07-14 07:49:33'),(9,9,2,3,44.18,'2026-07-14 07:49:33'),(10,10,1,2,86.84,'2026-07-14 07:52:29'),(11,11,2,1,97.17,'2026-07-14 07:52:55'),(12,12,1,2,86.84,'2026-07-14 07:53:30'),(13,13,2,1,97.17,'2026-07-14 07:54:04'),(14,14,1,2,74.62,'2026-07-14 14:30:57'),(15,14,2,1,100.00,'2026-07-14 14:30:57'),(16,15,1,1,92.79,'2026-07-14 15:24:27'),(17,16,1,1,92.79,'2026-07-14 15:24:43'),(18,17,1,2,100.00,'2026-07-14 15:25:28'),(19,17,2,5,62.93,'2026-07-14 15:25:29'),(20,17,2,3,44.18,'2026-07-14 15:25:29'),(21,17,2,4,36.07,'2026-07-14 15:25:29'),(22,18,1,2,100.00,'2026-07-15 07:33:15'),(23,18,2,3,61.77,'2026-07-15 07:33:16'),(24,19,1,2,100.00,'2026-07-15 09:07:56'),(25,19,2,3,61.77,'2026-07-15 09:07:56'),(26,20,1,2,100.00,'2026-08-01 07:56:10'),(27,20,2,5,62.93,'2026-08-01 07:56:10'),(28,20,2,3,44.18,'2026-08-01 07:56:10'),(29,20,2,4,36.07,'2026-08-01 07:56:10');
/*!40000 ALTER TABLE `predictions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `role` enum('Administrateur','Inspecteur','Observateur') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'Inspecteur',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Administrateur Démo','admin.demo@example.invalid','b6a1d1be6af2827fcf17d2cb7e2565a6ea88a415dd399bca65be4e14dcff62ce','Administrateur','2026-07-06 15:37:58',1);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-02 10:29:25
