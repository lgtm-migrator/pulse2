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

-- ----------------------------------------------------------------------
-- Database xmppmaster
-- ----------------------------------------------------------------------
-- ----------------------------------------------------------------------
-- ADD COLUMNS md5agentversion AND version table uptime_machine
-- ADD INDEX ON COLUMNS  md5agentversion AND version and date
- ----------------------------------------------------------------------

START TRANSACTION;

USE `xmppmaster`;
SET FOREIGN_KEY_CHECKS=0;

ALTER TABLE `xmppmaster`.`uptime_machine`
ADD COLUMN `md5agentversion` VARCHAR(32) NULL AFTER `timetempunix`,
ADD COLUMN `version` VARCHAR(10) NULL AFTER `md5agentversion`,
ADD INDEX `ind_md5agent` (`md5agentversion` ASC) ,
ADD INDEX `ind_agenntversion` (`version` ASC) ,
ADD INDEX `ind_date` (`date` ASC) ;
;
-- ----------------------------------------------------------------------
-- PURGE uptime_machine OLD RECORD  Weeks
-- ----------------------------------------------------------------------
CREATE EVENT IF NOT EXISTS purgeuptimemachine
  ON SCHEDULE
  AT
  (CURRENT_TIMESTAMP + INTERVAL 1 DAY) ON COMPLETION PRESERVE ENABLE
  DO
    DELETE FROM xmppmaster.uptime_machine
    WHERE
        date < DATE_SUB(NOW(), INTERVAL 4 WEEK);




-- ----------------------------------------------------------------------
-- PROCEDURE purgeoldmachines Purges les machines offline plus de 64 jours.
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `purgeoldmachines`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`purgeoldmachines`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE OR REPLACE PROCEDURE `purgeoldmachines`()
BEGIN
set @dayinterval =  60;
DROP TABLE IF EXISTS mesdelete;
CREATE TEMPORARY TABLE IF NOT EXISTS mesdelete AS (
SELECT
        machines.id AS idmach,
            MAX(uptime_machine.id) as iduptime,
            uptime_machine.hostname as mach
    FROM
        xmppmaster.machines
    INNER JOIN xmppmaster.uptime_machine ON uptime_machine.hostname = SUBSTR(SUBSTRING_INDEX(machines.jid, '@', 1), 1, CHAR_LENGTH(SUBSTRING_INDEX(machines.jid, '@', 1)) - 4)
    WHERE
        enabled = 0 AND agenttype LIKE 'machine'
            AND uptime_machine.status = 0
            AND date <= CURDATE() - INTERVAL @dayinterval DAY
    GROUP BY uptime_machine.hostname);

delete
FROM
    uptime_machine
WHERE
    uptime_machine.hostname IN (SELECT
            mesdelete.mach
        FROM
            mesdelete);
delete
FROM
    machines
WHERE
    machines.id IN (SELECT
            mesdelete.idmach
        FROM
            mesdelete);
END$$

DELIMITER ;
;

-- ----------------------------------------------------------------------
-- PURGE old machine tout les jours
-- ----------------------------------------------------------------------

CREATE EVENT IF NOT EXISTS purgeoldmachines
  ON SCHEDULE
  AT
  (CURRENT_TIMESTAMP + INTERVAL 1 DAY) ON COMPLETION PRESERVE ENABLE
  DO
   call purgeoldmachines() ;



-- ----------------------------------------------------------------------
-- PROCEDUE STOCKEE support_get_outdated_machine_hostname
-- ----------------------------------------------------------------------
   CREATE OR REPLACE PROCEDURE `support_get_outdated_machine_hostname`(IN param_fingerprint VARCHAR(45))
BEGIN
	SELECT
		MAX(id) as id, hostname, md5agentversion
	FROM
		xmppmaster.uptime_machine
	WHERE
		status = 1
			AND md5agentversion NOT LIKE param_fingerprint
	GROUP BY hostname;
END

 -- ----------------------------------------------------------------------
-- AIDE PROCEDURE
-- ----------------------------------------------------------------------
INSERT INTO `xmppmaster`.`support_help_command` (`name`, `description`, `example`, `type`, `result`) VALUES ('support_get_outdated_machine_hostname', 'cette procedure est a utilise pour resortir les machine qui n\'on pas le finger print defini en parametre.', 'call support_get_outdated_machine_hostname(\'8c8265f15b43521ca726628dbd5068e1\')', 'P', 'call support_get_outdated_machine_hostname(\'8c8265f15b43521ca726628dbd5068e1\');\n+---------+----------+----------------------------------+\n| MAX(id) | hostname | md5agentversion                  |\n+---------+----------+----------------------------------+\n|    6448 | deb10-90 | 8c8265f15b43521ca726628dbd5068e3 |\n|    6453 | deb10-91 | 8c8265f15b43521ca726628dbd5068e6 |\n|    6454 | deb10-92 | 8c8265f15b43521ca726628dbd5068ea |\n|    6459 | deb10-93 | 8c8265f15b43521ca726628dbd5068e2 |\n+---------+----------+----------------------------------+');

-- ----------------------------------------------------------------------
-- PROCEDUE STOCKEE support_base_size
-- ----------------------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `support_base_size`;

DELIMITER $$
USE `xmppmaster`$$
CREATE OR REPLACE PROCEDURE `support_base_size` (IN param_name_base VARCHAR(45))
BEGIN
SELECT
    table_name AS 'Tables',
    table_rows AS 'lines',
    ROUND(((data_length + index_length) / 1024 / 1024),
            2) 'Size in MB'
FROM
    information_schema.TABLES
WHERE
    table_schema = param_name_base
ORDER BY `lines` DESC;
END$$

DELIMITER ;

-- ----------------------------------------------------------------------
-- AIDE PROCEDURE
-- ----------------------------------------------------------------------

INSERT INTO `xmppmaster`.`support_help_command` (`name`, `description`, `example`, `type`, `result`) VALUES ('support_base_size', 'cette procedure renvoi les table d\'une base avec lenombre de d\'enregistrement et la taille en mb', 'call support_base_size(\'xmppmaster\');', 'P', 'call support_base_size(\'pkgs\');\n+----------------------------+-------+------------+\n| Tables                     | lines | Size in MB |\n+----------------------------+-------+------------+\n| pkgs_rules_global          |  1581 |       0.16 |\n| dependencies               |    15 |       0.02 |\n| packages                   |    15 |       0.05 |\n| extensions                 |     5 |       0.02 |\n| pkgs_rules_local           |     3 |       0.05 |\n| pkgs_rules_algos           |     3 |       0.02 |\n| pkgs_shares                |     2 |       0.03 |\n| pkgs_shares_ars            |     0 |       0.03 |\n| syncthingsync              |     0 |       0.02 |\n| package_pending_exclusions |     0 |       0.02 |\n| pkgs_shares_ars_web        |     0 |       0.06 |\n| version                    |     0 |       0.02 |\n+----------------------------+-------+------------+\n12 rows in set (0.001 sec)\n');


-- ----------------------------------------------------------------------
-- PROCEDUE STOCKEE support_size_all_table
-- ----------------------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `support_size_all_table`;

DELIMITER $$
USE `xmppmaster`$$
CREATE OR REPLACE PROCEDURE `support_size_all_table` ()
BEGIN
SELECT
    table_schema 'Databases',
    SUM(data_length + index_length) / 1024 / 1024 'Size of DB in MB'
FROM
    information_schema.TABLES
GROUP BY table_schema ORDER BY `Size of DB in MB` DESC;
END$$

DELIMITER ;

-- ----------------------------------------------------------------------
-- AIDE PROCEDURE
-- ----------------------------------------------------------------------
INSERT INTO `xmppmaster`.`support_help_command` (`name`, `description`, `example`, `type`, `result`) VALUES ('support_size_all_table', 'cette procédure est utilisée pour voir la taille des toutes les bases en MB', 'call support_size_all_table();', 'P', 'call support_size_all_table();\n+--------------------+------------------+\n| Databases          | Size of DB in MB |\n+--------------------+------------------+\n| admin              |       0.01562500 |\n| backuppc           |       0.04376984 |\n| dyngroup           |       0.50000000 |\n| glpi               |       9.88636017 |\n| guacamole          |       0.59375000 |\n| imaging            |       1.31250000 |\n| information_schema |       0.17187500 |\n| inventory          |       0.52736950 |\n| kiosk              |       0.15625000 |\n| msc                |       0.09834194 |\n| mysql              |       0.94722652 |\n| performance_schema |       0.00000000 |\n| pkgs               |       0.46875000 |\n| pulse2             |       0.07812500 |\n| update             |       0.09375000 |\n| xmppmaster         |      15.90211105 |\n+--------------------+------------------+\n');



SET FOREIGN_KEY_CHECKS=1;
-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 67;

COMMIT;
