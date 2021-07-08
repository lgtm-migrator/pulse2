--
-- (c) 2021 Siveo, http://www.siveo.net/
--
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

START TRANSACTION;

USE `xmppmaster`;
SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------------------------------------------------
-- Database xmppmaster
-- ----------------------------------------------------------------------
-- ----------------------------------------------------------------------
-- Creation table update_machine
-- cette table nous renseigne sur l'état de mise a jour d'une machine. 
- ----------------------------------------------------------------------

CREATE  TABLE IF NOT EXISTS  `update_machine` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `hostname` varchar(120) NOT NULL,
  `jid` varchar(255) NOT NULL,
  `status` varchar(15) NOT NULL DEFAULT 'ready',
  `descriptor` text NOT NULL DEFAULT '""',
  `md5` varchar(45) NOT NULL,
  `date_creation` timestamp NOT NULL DEFAULT current_timestamp(),
  `ars` varchar(255) DEFAULT NULL COMMENT 'cette information doit etre initialise si la machine doit utiliser 1 ars pour ce mettre a jour\n',
  PRIMARY KEY (`id`),
  UNIQUE KEY `jid_UNIQUE` (`jid`),
  KEY `ind_jid` (`jid`),
  KEY `ind_status` (`status`),
  KEY `ind_hostname` (`hostname`),
  KEY `ind_date` (`date_creation`),
  KEY `ind_ars` (`ars`)
) ENGINE=InnoDB AUTO_INCREMENT=93368 DEFAULT CHARSET=utf8 COMMENT='Cette table permet de definir l etat de mise a jour d une machine.'

-- ----------------------------------------------------------------------
-- Creation table ban_machine
-- cette table nous renseigne sur les machine bannir. 
- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `xmppmaster`.`ban_machine` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `jid` VARCHAR(255) NULL COMMENT 'permet de connaitre le nom du compte,\nle jid de la machine bannie.',
  `ars_server` VARCHAR(255) NULL COMMENT 'permet de definir ars sur lequel agir pour envoyer les commande ejabberd',
  `date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  PRIMARY KEY (`id`),
  UNIQUE INDEX `jid_UNIQUE` (`jid` ASC))ENGINE=InnoDB DEFAULT CHARSET=utf8 
  COMMENT = 'cette table permet de definir les machines qui sont excluts. pour reinclure les machine excluts il faut supprimer son compte sur le server xmpp';
  
  
SET FOREIGN_KEY_CHECKS=1;
-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 60;

COMMIT;
