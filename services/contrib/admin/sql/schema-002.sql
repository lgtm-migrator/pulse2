--
-- (c) 2020 Siveo, http://www.siveo.net/
--
-- $Id$
--
-- This file is part of Pulse 2, http://www.siveo.net/
--
-- Pulse 2 is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 2 of the License, or
-- (at your option) any later version.
--
-- Pulse 2 is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with Pulse 2; if not, write to the Free Software
-- Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
-- MA 02110-1301, USA.

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------

-- MySQL dump 10.19
--
-- Host: localhost    Database: admin
-- ------------------------------------------------------
-- Server version	10.3.34-MariaDB-0+deb10u1


--
-- Table structure for table `udp_list`
--

DROP TABLE IF EXISTS `udp_list`;
CREATE TABLE `udp_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `list_name` varchar(90) NOT NULL,
  `comment` varchar(255) DEFAULT NULL,
  `priority` int(11) DEFAULT 10 COMMENT 'la liste de plus haute priorite est applique en dernier.\n',
  `action` varchar(45) DEFAULT 'admin' COMMENT 'action : admin, exclud, includ\n',
  `deleted` int(11) DEFAULT 0 COMMENT 'trois 4 listes ne sont pas supprimable:\nlist admin, black liste interdir, liste permettre, list rest.\n\n',
  PRIMARY KEY (`id`),
  KEY `id_unique` (`list_name`),
  KEY `idx_list_name` (`list_name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
--
-- Dumping data for table `udp_list`
--

LOCK TABLES `udp_list` WRITE;
INSERT INTO `udp_list` VALUES (1,'white_list','list package installer ce package',2,'include',0),(2,'black_list','list_package ne pas installer ce package',1,'exclude',0),(3,'gray_list','list_package en attente danalyse.',3,'exclude',0);
UNLOCK TABLES;

--
-- Table structure for table `udp_list_package`
--

DROP TABLE IF EXISTS `udp_list_package`;
CREATE TABLE `udp_list_package` (
  `package_id` int(11) NOT NULL,
  `list_id` int(11) NOT NULL,
  `method_id` int(11) NOT NULL,
  `actif` int(11) NOT NULL DEFAULT 1,
  PRIMARY KEY (`package_id`,`list_id`,`method_id`),
  KEY `fk_pack` (`package_id`),
  KEY `fk_list` (`list_id`),
  KEY `fk_methode` (`method_id`),
  CONSTRAINT `fk_udp_list_package_1` FOREIGN KEY (`package_id`) REFERENCES `udp_package` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `fk_udp_list_package_2` FOREIGN KEY (`list_id`) REFERENCES `udp_list` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `fk_udp_list_package_3` FOREIGN KEY (`method_id`) REFERENCES `udp_method` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
--
-- Dumping data for table `udp_list_package`
--

LOCK TABLES `udp_list_package` WRITE;
UNLOCK TABLES;

--
-- Table structure for table `udp_method`
--

DROP TABLE IF EXISTS `udp_method`;
CREATE TABLE `udp_method` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `method` varchar(45) NOT NULL,
  `transfert_method` varchar(45) DEFAULT 'pull curl cdn',
  `nb_remise` int(11) DEFAULT 3,
  `delta_time` int(11) DEFAULT 3600,
  `comment` varchar(45) DEFAULT NULL,
  `msg_method` text DEFAULT '{}',
  PRIMARY KEY (`id`),
  UNIQUE KEY `method_UNIQUE` (`method`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
--
-- Dumping data for table `udp_method`
--

LOCK TABLES `udp_method` WRITE;
INSERT INTO `udp_method` VALUES (1,'interactif','pull curl cdn',3,45,'remise 3 fois la mise à jour','{\n    \"messagelist\": {\n        \"1\": \"accepter ou remtre la mise a jour\", \n        \"3\": \"la mise \\u00e0 jour va commencer dans 5 minutes sauver votre travail\", \n        \"2\": \"accepter secondee mise \\u00e0 jour\", \n        \"warning\": \"attention sauver votre travail\"\n    }\n}\n'),(2,'direct','pull curl cdn',0,0,'update sans interaction avec l\'utilisateur','{}'),(3,'conditionel','pull curl cdn',3,45,'remise 3 fois si user connecter, sinon instal','{\n    \"messagelist\": {\n        \"1\": \"accepter ou remtre la mise a jour\", \n        \"3\": \"la mise \\u00e0 jour va commencer dans 5 minutes sauver votre travail\", \n        \"2\": \"accepter secondee mise \\u00e0 jour\", \n        \"warning\": \"attention sauver votre travail\"\n    }\n}\n'),(4,'no_process','pull curl cdn',0,0,'ne pas installer','{ }');
UNLOCK TABLES;

--
-- Table structure for table `udp_msg_send`
--

DROP TABLE IF EXISTS `udp_msg_send`;
CREATE TABLE `udp_msg_send` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` timestamp NOT NULL DEFAULT current_timestamp(),
  `jid` varchar(255) NOT NULL,
  `json_msg` text NOT NULL,
  `ars` varchar(255) DEFAULT NULL COMMENT 'ars\n',
  `session_id` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `udp_msg_send`
--

LOCK TABLES `udp_msg_send` WRITE;
UNLOCK TABLES;

--
-- Table structure for table `udp_package`
--

DROP TABLE IF EXISTS `udp_package`;
CREATE TABLE `udp_package` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `package` varchar(100) NOT NULL,
  `version` varchar(45) DEFAULT NULL,
  `type` varchar(45) DEFAULT 'secutity',
  `platform` varchar(45) NOT NULL,
  `cmd_before` varchar(512) DEFAULT NULL,
  `cmd_after` varchar(512) DEFAULT NULL,
  `script` text DEFAULT NULL,
  `comment` varchar(45) DEFAULT NULL,
  `url_info` varchar(512) DEFAULT NULL,
  `creation_date` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_name_package` (`package`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `udp_package`
--

LOCK TABLES `udp_package` WRITE;
UNLOCK TABLES;

--
-- Table structure for table `udp_package_unknown`
--

DROP TABLE IF EXISTS `udp_package_unknown`;
CREATE TABLE `udp_package_unknown` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) DEFAULT NULL,
  `jid` varchar(45) DEFAULT NULL,
  `platform` varchar(45) DEFAULT NULL,
  `reception_date` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
--
-- Dumping data for table `udp_package_unknown`
--

LOCK TABLES `udp_package_unknown` WRITE;
UNLOCK TABLES;

--
-- Table structure for table `udp_rules`
--

DROP TABLE IF EXISTS `udp_rules`;
CREATE TABLE `udp_rules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `package_id` int(11) NOT NULL,
  `method_id` int(11) NOT NULL,
  `jid` varchar(255) DEFAULT NULL,
  `name` varchar(90) DEFAULT NULL,
  `software_exist` varchar(255) DEFAULT NULL,
  `software_no_exist` varchar(255) DEFAULT NULL,
  `list_list` varchar(512) DEFAULT '0',
  `include_exclude` int(11) NOT NULL DEFAULT 1 COMMENT 'include or exclude\n',
  `actif` int(11) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `pack_id` (`package_id`),
  KEY `method_id` (`method_id`),
  CONSTRAINT `fk_udp_method` FOREIGN KEY (`method_id`) REFERENCES `udp_method` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `fk_udp_pack` FOREIGN KEY (`package_id`) REFERENCES `udp_package` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `udp_rules`
--

LOCK TABLES `udp_rules` WRITE;
-- insert
UNLOCK TABLES;

--
-- Dumping data for table `version`
--

INSERT INTO `version` VALUES (2);
