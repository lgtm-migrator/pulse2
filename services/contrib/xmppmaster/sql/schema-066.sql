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
-- Definition procedure stockee for support
-- ces procedure sont prefixe par support.
- ----------------------------------------------------------------------



-- /#####################################################################\
-- | View vs_updatingmachine_updating                                    |
-- | cette vue permet de voir les machines en attente de mise à jour     |
-- | exemple select * from vs_updatingmachine;                           |
-- \#####################################################################/
USE `xmppmaster`;
DROP VIEW IF EXISTS `xmppmaster`.`vs_updatingmachine` ;
CREATE
     OR REPLACE ALGORITHM = UNDEFINED
    DEFINER = `root`@`localhost`
    SQL SECURITY DEFINER
VIEW `vs_updatingmachine_updating` AS
    SELECT
        `update_machine`.`jid` AS `jid`,
        `update_machine`.`ars` AS `ars`,
        `update_machine`.`status` AS `status`,
        `machines`.`enabled` AS `enabled`
    FROM
        (`machines`
        JOIN `update_machine` ON (SUBSTRING_INDEX(`machines`.`jid`, '/', 1) = `update_machine`.`jid`))
    WHERE
        `machines`.`enabled` = 1
            AND `update_machine`.`status` LIKE 'updating';

            UPDATE `xmppmaster`.`support_help_command` SET `id` = '10', `name` = 'vs_updatingmachine_updating', `description` = 'Cette vue affiche les machines qui son en train d\'etre updater .', `example` = 'SELECT * FROM xmppmaster.vs_updatingmachine_updating\\G;', `result` = '' WHERE (`id` = '8');

INSERT INTO `xmppmaster`.`support_help_command` (`id`, `name`, `description`, `example`, `type`, `result`) VALUES ('', 'vs_updatingmachine_updating', 'Cette vue affiche les machines qui son en train d\'etre updater .', 'SELECT * FROM xmppmaster.vs_updatingmachine_updating\\G;', 'V', '');



-- /#####################################################################\
-- | View vs_updatingmachine_ready                                    |
-- | cette vue permet de voir les machines en attente de mise à jour     |
-- | exemple select * from vs_updatingmachine;                           |
-- \#####################################################################/


USE `xmppmaster`;
DROP VIEW IF EXISTS `xmppmaster`.`vs_updatingmachine_ready` ;
CREATE
     OR REPLACE ALGORITHM = UNDEFINED
    DEFINER = `root`@`localhost`
    SQL SECURITY DEFINER
VIEW `vs_updatingmachine_ready` AS
    SELECT
        `update_machine`.`jid` AS `jid`,
        `update_machine`.`ars` AS `ars`,
        `update_machine`.`status` AS `status`,
        `machines`.`enabled` AS `enabled`
    FROM
        (`machines`
        JOIN `update_machine` ON (SUBSTRING_INDEX(`machines`.`jid`, '/', 1) = `update_machine`.`jid`))
    WHERE
        `machines`.`enabled` = 1
            AND `update_machine`.`status` LIKE 'ready';

INSERT INTO `xmppmaster`.`support_help_command` (`name`, `description`, `example`, `type`) VALUES ('vs_updatingmachine_ready', 'Cette vue affiche les machines qui doivent etre mise à jour en attente du status updating pour etre mise à jour ', 'SELECT * FROM xmppmaster.vs_updatingmachine_ready;', 'V');




-- /############################################################################\
-- | procedure support_enableupdating                                           |
-- | cette procedure permet de remplacer 1 status dans la table updatemachine.  |
-- | on peut selectionne les machines pour 1 ars ou pour tout les ars.          |
-- | exemple call support_enableupdating("rsqa-ars1","ready","updating");       |
-- |     met tout les status updating a redy pour les machine màj par rsqa-ars1 |
-- \############################################################################/


USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`support_enableupdating`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `support_enableupdating`(IN P_ars VARCHAR(90), IN new_status varchar(40),IN old_status varchar(40))
BEGIN
    IF P_ars = "ALL" or P_ars = ""  THEN
        -- updating tout les enregistrement
        UPDATE `xmppmaster`.`update_machine`
        SET
            `status` = new_status
        WHERE
            `id` in (SELECT
                    xmppmaster.update_machine.id
                FROM
                    xmppmaster.machines
                        JOIN
                    xmppmaster.update_machine ON SUBSTRING_INDEX(xmppmaster.machines.jid, '@', 1) = SUBSTRING_INDEX(xmppmaster.update_machine.jid,'@',1)
                WHERE
                    xmppmaster.machines.enabled = 1
                        AND xmppmaster.update_machine.status LIKE old_status);
    ELSE
        -- updating les machine pour ars determine.
        UPDATE `xmppmaster`.`update_machine`
        SET
            `status` = new_status
        WHERE
            `id` in (SELECT
                    xmppmaster.update_machine.id
                FROM
                    xmppmaster.machines
                        JOIN
                    xmppmaster.update_machine ON SUBSTRING_INDEX(xmppmaster.machines.jid, '@', 1) = SUBSTRING_INDEX(xmppmaster.update_machine.jid,'@',1)
                WHERE
                    xmppmaster.machines.enabled = 1
                        AND xmppmaster.update_machine.status LIKE old_status
                        and substring_index(xmppmaster.update_machine.ars, '@', 1) LIKE P_ars );
    END IF;
END$$

DELIMITER ;
;

UPDATE `xmppmaster`.`support_help_command` SET `description` = 'Cette Procedure permet de remplacer lel\'ancien status par le nouveau\n3 parametres.  :\n   -1)  le nom de ars ( La mise à jour ne consernera que les machines affiliées a cet ARS.  Si valeurs \"ALL\" ou \"\" pour tout les ars)\n   -2) le nouveau status\n   -3) l\'ancien status' WHERE (`id` = '8');




-- /################################################################################\
-- | procedure support_get_machine_restart                                          |
-- | cette procedure sert a recherche les machines redémarrant en boucle.           |
-- | non compte les machine avec 1 tres petit uptime                                |
-- | exemple call support_get_machine_restart(10,24);                               |
-- | l'exemple renvoi les machines avec aux moins 10 restart les dernier 24 heures. |
-- \################################################################################/
USE `xmppmaster`;
DROP procedure IF EXISTS `support_get_machine_restart`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `support_get_machine_restart` (in in_nbstart int, in  in_nb_hour int)
BEGIN
    SELECT
        COUNT(*) AS restart, hostname
    FROM
        xmppmaster.uptime_machine
    WHERE
        status = 1 AND updowntime < 100
            AND date > (NOW() - INTERVAL in_nb_hour HOUR)
    GROUP BY hostname
    HAVING restart > in_nbstart;
END$$

DELIMITER ;
INSERT INTO `xmppmaster`.`support_help_command` (`name`, `description`, `example`, `type`) VALUES ('support_get_machine_restart', 'cette procedure sert a recherche les machines redémarrant en boucle.\non compte les machine avec 1 tres petit uptime.\nl\'exemple renvoi les machines avec aux moins 10 restart les dernier 24 heures. ', 'call support_get_machine_restart(10,24);', 'P');



-- /############################################################################\
-- | add device typre alertmonitoring                                           |
-- \############################################################################/
ALTER TABLE `xmppmaster`.`mon_devices`
CHANGE COLUMN `device_type` `device_type` ENUM('thermalPrinter', 'nfcReader', 'opticalReader', 'cpu', 'memory', 'storage', 'network', 'system', 'alertmonitoring') NOT NULL ;
