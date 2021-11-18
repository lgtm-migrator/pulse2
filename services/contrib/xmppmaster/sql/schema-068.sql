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


SET FOREIGN_KEY_CHECKS=1;
-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 67;

COMMIT;
