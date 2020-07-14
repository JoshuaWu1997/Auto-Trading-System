-- MySQL dump 10.13  Distrib 8.0.19, for Win64 (x86_64)
--
-- Host: localhost    Database: userdb
-- ------------------------------------------------------
-- Server version	8.0.19

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

--
-- Current Database: `userdb`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `userdb` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `userdb`;

--
-- Table structure for table `position`
--

DROP TABLE IF EXISTS `position`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `position` (
  `t_id` int NOT NULL,
  `stock_id` varchar(45) NOT NULL,
  `volume` int DEFAULT NULL,
  PRIMARY KEY (`t_id`,`stock_id`),
  CONSTRAINT `id` FOREIGN KEY (`t_id`) REFERENCES `trade_list` (`t_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `trade_detail`
--

DROP TABLE IF EXISTS `trade_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `trade_detail` (
  `t_id` int NOT NULL,
  `stock_id` varchar(45) NOT NULL,
  `transaction_datetime` datetime NOT NULL,
  `volume` int DEFAULT NULL,
  `direction` varchar(45) DEFAULT NULL,
  `price` double DEFAULT NULL,
  PRIMARY KEY (`t_id`,`stock_id`,`transaction_datetime`),
  CONSTRAINT `idd` FOREIGN KEY (`t_id`) REFERENCES `trade_list` (`t_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `trade_list`
--

DROP TABLE IF EXISTS `trade_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `trade_list` (
  `t_id` int NOT NULL,
  `begin_datetime` datetime DEFAULT NULL,
  `end_datetime` datetime DEFAULT NULL,
  `begin_cash` double unsigned DEFAULT NULL,
  `valid_cash` double unsigned DEFAULT NULL,
  `total_asset` double DEFAULT NULL,
  `trade_state` varchar(45) DEFAULT NULL,
  `trade_baseline` varchar(45) NOT NULL,
  PRIMARY KEY (`t_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `trade_stock`
--

DROP TABLE IF EXISTS `trade_stock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `trade_stock` (
  `t_id` int NOT NULL,
  `stock_id` varchar(45) NOT NULL,
  PRIMARY KEY (`t_id`),
  CONSTRAINT `ids` FOREIGN KEY (`t_id`) REFERENCES `trade_list` (`t_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping events for database 'userdb'
--

--
-- Dumping routines for database 'userdb'
--

--
-- Current Database: `crawlerdb`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `crawlerdb` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `crawlerdb`;

--
-- Table structure for table `crawl_data`
--

DROP TABLE IF EXISTS `crawl_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `crawl_data` (
  `id` varchar(45) NOT NULL,
  `datetime` datetime NOT NULL,
  `price` double DEFAULT NULL,
  `buy` double DEFAULT NULL,
  `sell` double DEFAULT NULL,
  `amount` int DEFAULT NULL,
  PRIMARY KEY (`id`,`datetime`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `selected_stocks`
--

DROP TABLE IF EXISTS `selected_stocks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `selected_stocks` (
  `stockID` varchar(45) NOT NULL,
  PRIMARY KEY (`stockID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping events for database 'crawlerdb'
--

--
-- Dumping routines for database 'crawlerdb'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-07-14 15:16:47
