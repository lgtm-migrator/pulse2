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
-- Creation table pulse_users
-- cette table permet de definir des users et leur attribuer des preferences ou des droits pour visualiser les partages. 
- ----------------------------------------------------------------------
CREATE TABLE `pulse_users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `login` varchar(255) NOT NULL,
  `comment` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `login_UNIQUE` (`login`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
-- ----------------------------------------------------------------------
-- Creation table pulse_teams
-- cette table permet de definir les teams.. 
-- ----------------------------------------------------------------------
CREATE TABLE `pulse_teams` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'definie la team',
  `name` varchar(120) NOT NULL,
  `comment` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------------------------------------------------
-- Creation table pulse_preferences
-- cette table permet d'attribuer des preference sous forme key value a 1 utilisateurs
-- ----------------------------------------------------------------------

CREATE TABLE `pulse_preferences` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `key` varchar(120) NOT NULL,
  `value` text DEFAULT '""',
  `id_user` int(11) NOT NULL,
  `domain` varchar(80) DEFAULT NULL COMMENT 'ce champ peut specialiser des preferences a 1 domaine. 1 domaine peut etre 1 pageweb par exemple.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `key_UNIQUE` (`key`,`id_user`,`domain`),
  KEY `fk_pulse_preferences_1_idx` (`id_user`),
  CONSTRAINT `fk_pulse_preferences_1` FOREIGN KEY (`id_user`) REFERENCES `pulse_users` (`id`)
  ON DELETE NO ACTION 
  ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------------------------------------------------
-- Creation table pulse_team_user
-- cette table permet de crer des team
-- ----------------------------------------------------------------------

 CREATE TABLE `pulse_team_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_user` int(11) DEFAULT NULL,
  `id_team` int(11) DEFAULT NULL,
  `comment` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unix_team_user` (`id_user`,`id_team`),
  KEY `fk_pulse_team_user_1_idx` (`id_user`),
  KEY `fk_pulse_team_user_2_idx` (`id_team`),
  CONSTRAINT `fk_pulse_team_user_1` FOREIGN KEY (`id_user`) REFERENCES `pulse_users` (`id`) 
  ON DELETE CASCADE 
  ON UPDATE CASCADE,
  CONSTRAINT `fk_pulse_team_user_2` FOREIGN KEY (`id_team`) REFERENCES `pulse_teams` (`id`) 
  ON DELETE CASCADE 
  ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8; 


-- ----------------------------------------------------------------------
-- create use root
-- ----------------------------------------------------------------------

INSERT INTO `xmppmaster`.`pulse_users` (`login`) VALUES ('root');


SET FOREIGN_KEY_CHECKS=1;
-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 60;

COMMIT;
