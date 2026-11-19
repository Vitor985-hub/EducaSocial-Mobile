CREATE DATABASE  IF NOT EXISTS `dbaeducasocial` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `dbaeducasocial`;
-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: db-educasocial-mysql.csdqeu28a38w.us-east-1.rds.amazonaws.com    Database: dbaeducasocial
-- ------------------------------------------------------
-- Server version	8.4.11

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '';

--
-- Table structure for table `category`
--

DROP TABLE IF EXISTS `category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `category` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `document`
--

DROP TABLE IF EXISTS `document`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `document` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `opportunity_id` bigint NOT NULL,
  `source_id` bigint DEFAULT NULL,
  `chunk_index` int NOT NULL,
  `content` longtext NOT NULL,
  `embedding_model` varchar(255) DEFAULT NULL,
  `embedding` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_document_opportunity_chunk` (`opportunity_id`,`chunk_index`),
  KEY `fk_document_source` (`source_id`),
  KEY `idx_document_opportunity` (`opportunity_id`),
  CONSTRAINT `fk_document_opportunity` FOREIGN KEY (`opportunity_id`) REFERENCES `opportunity` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_document_source` FOREIGN KEY (`source_id`) REFERENCES `source` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `opportunity`
--

DROP TABLE IF EXISTS `opportunity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `opportunity` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(500) NOT NULL,
  `description` text NOT NULL,
  `eligibility` text NOT NULL,
  `required_documents` json NOT NULL,
  `application_steps` json NOT NULL,
  `region_id` bigint NOT NULL,
  `category_id` bigint NOT NULL,
  `last_reviewed` date NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'unconfirmed',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_opportunity_category` (`category_id`),
  KEY `idx_opportunity_region_category` (`region_id`,`category_id`),
  CONSTRAINT `fk_opportunity_category` FOREIGN KEY (`category_id`) REFERENCES `category` (`id`),
  CONSTRAINT `fk_opportunity_region` FOREIGN KEY (`region_id`) REFERENCES `region` (`id`),
  CONSTRAINT `chk_opportunity_status` CHECK ((`status` in (_utf8mb4'current',_utf8mb4'outdated',_utf8mb4'unconfirmed')))
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region`
--

DROP TABLE IF EXISTS `region`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `region` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `level` varchar(20) NOT NULL,
  `state` char(2) DEFAULT NULL,
  `parent_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_region_name_level` (`name`,`level`),
  KEY `fk_region_parent` (`parent_id`),
  CONSTRAINT `fk_region_parent` FOREIGN KEY (`parent_id`) REFERENCES `region` (`id`),
  CONSTRAINT `chk_region_level` CHECK ((`level` in (_utf8mb4'national',_utf8mb4'state',_utf8mb4'city'))),
  CONSTRAINT `chk_region_parent` CHECK ((((`level` = _utf8mb4'national') and (`parent_id` is null)) or ((`level` <> _utf8mb4'national') and (`parent_id` is not null))))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `source`
--

DROP TABLE IF EXISTS `source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `source` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `opportunity_id` bigint NOT NULL,
  `name` varchar(255) NOT NULL,
  `url` varchar(2048) NOT NULL,
  `consulted_at` date NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_source_opportunity_url` (`opportunity_id`,`url`(500)),
  KEY `idx_source_opportunity` (`opportunity_id`),
  CONSTRAINT `fk_source_opportunity` FOREIGN KEY (`opportunity_id`) REFERENCES `opportunity` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-19 19:42:23
