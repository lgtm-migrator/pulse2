--
-- (c) 2021 Siveo, http://www.siveo.net/
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
-- Database xmppmaster
-- ----------------------------------------------------------------------

START TRANSACTION;

USE `xmppmaster`;

-- ----------------------------------------------------------------------
-- Definition of procedures for support
-- These procedures are prefixed support_
-- -----------------------------------------------------------------------

-- /#####################################################################\
-- | creation table help command                                         |
-- \#####################################################################/
 CREATE TABLE `support_help_command` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) DEFAULT NULL,
  `description` varchar(5000) DEFAULT NULL,
  `example` varchar(5000) DEFAULT NULL,
  `type` varchar(45) DEFAULT NULL,
  `result` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;


-- /############################################################################\
-- | support_restart_single_deploy procedure                                    |
-- | This procedure is used to restart a deployment on a single machine         |
-- | The session's logs are removed                                             |
-- | exemple: call support_restart_single_deploy('command3bd50e905a4f4c4e82');  |
-- \############################################################################/
USE `xmppmaster`;
DROP procedure IF EXISTS `support_restart_single_deploy`;
DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `support_restart_single_deploy`(IN IN_sessid VARCHAR(255))
BEGIN
set @cmd = (select command from  xmppmaster.deploy where sessionid like IN_sessid);
DELETE FROM `xmppmaster`.`logs` WHERE (`sessionname` like IN_sessid);
DELETE FROM `xmppmaster`.`deploy` WHERE (`sessionid` like IN_sessid);
UPDATE `msc`.`commands` SET `end_date` = now() + INTERVAL 1 DAY WHERE (`id` = @cmd) and  NOW() > end_date;
UPDATE `msc`.`phase` SET `state` = 'ready' WHERE (`msc`.`phase`.`fk_commands_on_host` = @cmd );
END$$
DELIMITER ;

INSERT INTO `xmppmaster`.`support_help_command` (`name`, `description`, `example`, `type`) VALUES ('support_restart_single_deploy', 'This procedure is used to restart deployment on a single machine.\nThe old logs are replaced by the new ones.', 'call support_restart_single_deploy(\'command3bd50e905a4f4c4e82\');', 'P');


-- /############################################################################\
-- | support_restart_group_deploy procedure                                     |
-- | This procedure is used to restart a deployment on a group                  |
-- | The session's logs are removed                                             |
-- | exemple: call support_restart_group_deploy('command3bd50e905a4f4c4e82');   |
-- \############################################################################/
USE `xmppmaster`;
DROP procedure IF EXISTS `support_restart_group_deploy`;
DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `support_restart_group_deploy`(IN IN_sessid VARCHAR(255))
BEGIN
set @cmd = (select command from  xmppmaster.deploy where sessionid like IN_sessid);
set @grp = (select group_uuid from  xmppmaster.deploy where sessionid like IN_sessid );
DELETE FROM `xmppmaster`.`logs` WHERE (`sessionname` like IN_sessid);
DELETE FROM `xmppmaster`.`logs` WHERE (`sessionname` IN (SELECT sessionid FROM `xmppmaster`.`deploy` WHERE (`command` = @cmd) AND (`group_uuid` = @grp)));
DELETE FROM `xmppmaster`.`deploy` WHERE (`sessionid` like IN_sessid);
DELETE FROM `xmppmaster`.`deploy` WHERE (`command` = @cmd) AND (`group_uuid` = @grp);
UPDATE `msc`.`commands` SET `end_date` = now() + INTERVAL 1 DAY WHERE (`id` = @cmd) and  NOW() > end_date;
UPDATE `msc`.`phase` SET `state` = 'ready' WHERE (`msc`.`phase`.`fk_commands_on_host` = @cmd );
UPDATE `msc`.`phase` SET `state` = 'ready' WHERE (`msc`.`phase`.`fk_commands_on_host` IN ( SELECT id FROM `msc`.`commands_on_host` WHERE (`fk_commands` = @cmd))); 
END$$
DELIMITER ;

INSERT INTO `xmppmaster`.`support_help_command` (`name`, `description`, `example`, `type`) VALUES ('support_restart_group_deploy', 'This procedure is used to restart deployments on a group.\nThe old logs are replaced by the new ones.', 'call support_restart_group_deploy(\'command3bd50e905a4f4c4e82\');', 'P');


-- /#####################################################################\
-- | support_delete_deploy procedure                                     |
-- | This procedure is used to delete a deploy                           |
-- | The session's logs and command are removed                          |
-- | exemple: call support_delete_deploy('command3bd50e905a4f4c4e82');   |
-- \#####################################################################/
USE `xmppmaster`;
DROP procedure IF EXISTS `support_delete_deploy`;
DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `support_delete_deploy`(IN IN_sessid VARCHAR(255))
BEGIN
set @cmd = (select command from  xmppmaster.deploy where sessionid like IN_sessid);
set @grp = (select group_uuid from  xmppmaster.deploy where sessionid like IN_sessid );
DELETE FROM `xmppmaster`.`logs` WHERE (`sessionname` like IN_sessid);
DELETE FROM `xmppmaster`.`logs` WHERE (`sessionname` IN (SELECT sessionid FROM `xmppmaster`.`deploy` WHERE (`command` = @cmd) AND (`group_uuid` = @grp)));
DELETE FROM `xmppmaster`.`deploy` WHERE (`sessionid` like IN_sessid);
DELETE FROM `xmppmaster`.`deploy` WHERE (`command` = @cmd) AND (`group_uuid` = @grp);
DELETE FROM `msc`.`commands_on_host` WHERE (`fk_commands` = @cmd);
DELETE FROM `msc`.`commands` WHERE (`id` = @cmd);
END$$
DELIMITER ;

INSERT INTO `xmppmaster`.`support_help_command` (`name`, `description`, `example`, `type`) VALUES ('support_delete_deploy', 'This procedure is used to delete deploys.\nAll records about the deployment are removed.', 'call support_delete_deploy(\'command3bd50e905a4f4c4e82\');', 'P');


-- /#######################################################################\
-- | support_deploy_stat procedure                                         |
-- | This procedure is used to show deployment stats for a relay,          |
-- | package and week                                                      |
-- | exemple: call support_deploy_stat('ars_name', 'package_name', 'week');|
-- \#######################################################################/
USE `xmppmaster`;
DROP procedure IF EXISTS `support_deploy_stat`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `support_deploy_stat`(IN P_arsname VARCHAR(90), IN P_packagename varchar(40),  IN P_week int)
BEGIN
IF P_arsname = "ALL" or P_arsname = ""  THEN
    set @ars = "";
else
   set @arsn = SUBSTRING_INDEX(P_arsname, '@', 1);
   select CONCAT(" SUBSTRING_INDEX(jid_relay, '@', 1) LIKE '", @arsn, "' and ") into  @ars;
END IF;


IF P_packagename = "ALL" or P_packagename = ""  THEN
    set @packn = "";
else
    select CONCAT(" pathpackage LIKE '", P_packagename, "' and ") into  @packn;
END IF;
 
set @P_week1 = P_week - 1;

select CONCAT(" start BETWEEN DATE_SUB(NOW(), INTERVAL ",P_week,"  WEEK) AND DATE_SUB(NOW(), INTERVAL ",@P_week1," WEEK)") into  @weekselect;

SET @sqlv = "SELECT 
    pathpackage,
    SUBSTRING_INDEX(jid_relay, '@', 1) AS ARS,
    SUM(CASE
        WHEN (state = 'DEPLOYMENT SUCCESS') THEN 1
        ELSE 0
    END) AS 'dep_sucess',
    SUM(CASE
        WHEN (state = 'DEPLOYMENT ERROR') THEN 1
        ELSE 0
    END) AS `dep_error`,
    SUM(CASE
        WHEN (state = 'DEPLOYMENT ABORT') THEN 1
        ELSE 0
    END) AS `dep_abort`,
    SUM(CASE
        WHEN (state = 'DEPLOYMENT ERROR ON TIMEOUT') THEN 1
        ELSE 0
    END) AS `dep_timeout`,
    SUM(CASE
        WHEN (state = 'DEPLOYMENT PARTIAL SUCCESS') THEN 1
        ELSE 0
    END) AS `dep_part_sucess`,
    SUM(CASE
        WHEN (state = 'ERROR UNKNOWN ERROR') THEN 1
        ELSE 0
    END) AS `err_unknow`,
    SUM(CASE
        WHEN (state = 'ABORT ON TIMEOUT') THEN 1
        ELSE 0
    END) AS `abt_timeout`,
    SUM(CASE
        WHEN (state = 'ABORT DEPLOYMENT CANCELLED BY USER') THEN 1
        ELSE 0
    END) AS `abt_cancel`,
    SUM(CASE
        WHEN (state = 'ABORT INCONSISTENT GLPI INFORMATION') THEN 1
        ELSE 0
    END) AS `abt_id_glpi`,
    SUM(CASE
        WHEN (state = 'ABORT MISSING AGENT') THEN 1
        ELSE 0
    END) AS `abt_missing_agent`,
    SUM(CASE
        WHEN (state = 'ERROR TRANSFER FAILED') THEN 1
        ELSE 0
    END) AS `err_transfert`,
    SUM(CASE
        WHEN (state = 'ABORT MACHINE DISAPPEARED') THEN 1
        ELSE 0
    END) AS `abt_mach_disp`,
    SUM(CASE
        WHEN (state = 'WAITING MACHINE ONLINE') THEN 1
        ELSE 0
    END) AS `waiting_mach`,
    SUM(CASE
        WHEN (state = 'WOL 1') THEN 1
        ELSE 0
    END) AS `wol1`,
    SUM(CASE
        WHEN (state = 'WOL 2') THEN 1
        ELSE 0
    END) AS `wol2`,
    SUM(CASE
        WHEN (state = 'WOL 3') THEN 1
        ELSE 0
    END) AS `wol3`,
    SUM(CASE
        WHEN (state = 'ABORT PACKAGE IDENTIFIER MISSING') THEN 1
        ELSE 0
    END) AS `abt_missing_identifier`,
    SUM(CASE
        WHEN (state = 'ABORT PACKAGE EXECUTION ERROR') THEN 1
        ELSE 0
    END) AS `abt_execution`,
    SUM(CASE
        WHEN (state = 'ABORT TRANSFER FAILED') THEN 1
        ELSE 0
    END) AS `abt_transfert`,
    SUM(CASE
        WHEN (state = 'ABORT PACKAGE EXECUTION CANCELLED') THEN 1
        ELSE 0
    END) AS `abt_exec_cancel`,
    SUM(CASE
        WHEN (state = 'ABORT RELAY DOWN') THEN 1
        ELSE 0
    END) AS `abt_down_ars`,
    SUM(CASE
        WHEN (state = 'DEPLOYMENT START') THEN 1
        ELSE 0
    END) AS `depl_start`,
    SUM(CASE
        WHEN (state = 'ABORT INFO RELAY MISSING') THEN 1
        ELSE 0
    END) AS `abt_missing_ars`,
    SUM(CASE
        WHEN (state = 'DEPLOYMENT DELAYED') THEN 1
        ELSE 0
    END) AS `depl_delayed`,
    SUM(CASE
        WHEN (state = 'ABORT MISSING DEPENDENCY') THEN 1
        ELSE 0
    END) AS `abt_dep_missing`,
    SUM(CASE
        WHEN (state = 'ABORT PACKAGE WORKFLOW ERROR') THEN 1
        ELSE 0
    END) AS `abt_workflow`,
    SUM(CASE
        WHEN (state = 'DEPLOYMENT PENDING (REBOOT/SHUTDOWN/...)') THEN 1
        ELSE 0
    END) AS `depl_pending`,
    SUM(CASE
        WHEN (state = state) THEN 1
        ELSE 0
    END) AS `total`,
    SUM(CASE
        WHEN
            (state NOT IN ('DEPLOYMENT SUCCESS' , 'DEPLOYMENT ERROR',
                'DEPLOYMENT ABORT',
                'DEPLOYMENT ERROR ON TIMEOUT',
                'DEPLOYMENT PARTIAL SUCCESS',
                'ERROR UNKNOWN ERROR',
                'ABORT ON TIMEOUT',
                'ABORT DEPLOYMENT CANCELLED BY USER',
                'ABORT INCONSISTENT GLPI INFORMATION',
                'ABORT MISSING AGENT',
                'ERROR TRANSFER FAILED',
                'ABORT MACHINE DISAPPEARED',
                'WAITING MACHINE ONLINE',
                'WOL 1',
                'WOL 2',
                'WOL 3',
                'ABORT PACKAGE IDENTIFIER MISSING',
                'ABORT PACKAGE EXECUTION ERROR',
                'ABORT TRANSFER FAILED',
                'ABORT PACKAGE EXECUTION CANCELLED',
                'ABORT RELAY DOWN',
                'DEPLOYMENT START',
                'ABORT INFO RELAY MISSING',
                'DEPLOYMENT DELAYED',
                'ABORT MISSING DEPENDENCY',
                'ABORT PACKAGE WORKFLOW ERROR',
                'DEPLOYMENT PENDING (REBOOT/SHUTDOWN/...)'))
        THEN
            1
        ELSE 0
    END) AS `other`
FROM
    xmppmaster.deploy
WHERE";

select  CONCAT(@sqlv, @ars, @packn , @weekselect," GROUP BY ARS;") into  @sqlrequette;

PREPARE stmt FROM @sqlrequette;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
END$$
DELIMITER ;

INSERT INTO `xmppmaster`.`support_help_command` (`name`, `description`, `example`, `type`, `result`) VALUES ('support_deploy_stat', 'cette procedure renvoie les informations d\'une semaine pour les deployement en fonctions des ars et des packages.\n1 er arg   t : le nom de ars  etre \"\" ou \"all\" pour tout las ars.  ce parametre accepte  1 jid complet. il en extrait automatiqurement la partie user.\n2 eme arg : le nom du package po \"\" ou \"all\". le nom du pacquage doit etre complrt et  correct. si \"\" ou \"all\" renvoie pour tout les packages.\n3 eme arg : la semaine. 1 pour la derniere semaine, 2 pour l\'avant derniere semaine, 3 , 4 ainsi de suite.', 'call support_deploy_stat(\"\", \"\", 1 );', 'P', 'exemple result \n| pathpackage | ARS     | dep_sucess | dep_error | dep_abort | dep_timeout | dep_part_sucess | err_unknow | abt_timeout | abt_cancel | abt_id_glpi | abt_missing_agent | err_transfert | abt_mach_disp | waiting_mach | wol1 | wol2 | wol3 | abt_missing_identifier | abt_execution | abt_transfert | abt_exec_cancel | abt_down_ars | depl_start | abt_missing_ars | depl_delayed | abt_dep_missing | abt_workflow | depl_pending | total | other |\n+-------------+---------+------------+-----------+-----------+-------------+-----------------+------------+-------------+------------+-------------+-------------------+---------------+---------------+--------------+------+------+------+------------------------+---------------+---------------+-----------------+--------------+------------+-----------------+--------------+-----------------+--------------+--------------+-------+-------+\n| testsimple  | rspulse |          1 |         0 |         0 |           0 |               0 |          0 |           0 |          0 |           0 |                 0 |             0 |             0 |            0 |    0 |    0 |    0 |                      0 |             0 |             0 |               0 |            0 |          0 |               0 |            0 |               0 |            0 |            0 |     1 |     0 |\n');


-- /#####################################################################\
-- | support_list_machines_on_relay procedure                            |
-- | This procedure is used to list machines using specified relay       |
-- | exemple: call support_list_machines_on_relay('dev-ars2');           |
-- \#####################################################################/
USE `xmppmaster`;
DROP procedure IF EXISTS `support_list_machines_on_relay`;
DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `support_list_machines_on_relay`(IN IN_relayname VARCHAR(255))
BEGIN
set @jid = concat("%@", IN_relayname, "/%");
SELECT DISTINCT
    `xmppmaster`.`machines`.`hostname` as Hostname, 
    `xmppmaster`.`network`.`ipaddress` as IPAddress, 
    `xmppmaster`.`network`.`gateway` as Gateway, 
    `xmppmaster`.`machines`.`groupdeploy` as RelayJID, 
    `xmppmaster`.`network`.`mask` as Subnet, 
    `xmppmaster`.`machines`.`enabled` as Online 
FROM `xmppmaster`.`machines` 
LEFT JOIN `xmppmaster`.`network` 
    ON `xmppmaster`.`machines`.`id` = `xmppmaster`.`network`.`machines_id` 
WHERE `xmppmaster`.`machines`.`jid` LIKE @jid
AND `xmppmaster`.`machines`.`agenttype` = 'machine'
AND `xmppmaster`.`network`.`ipaddress` != '';
END$$
DELIMITER ;

INSERT INTO `xmppmaster`.`support_help_command` (`name`, `description`, `example`, `type`) VALUES ('support_list_machines_on_relay', 'This procedure is used to list all machines on a specified relay.', 'call support_list_machines_on_relay(\'dev-ars2\');', 'P');


-- /#####################################################################\
-- | support_list_machines_in_subnet procedure                           |
-- | This procedure is used to list machines having the specified subnet |
-- | exemple: call support_list_machines_in_subnet('^55\.44\.1[2-5]\.'); |
-- \#####################################################################/
USE `xmppmaster`;
DROP procedure IF EXISTS `support_list_machines_in_subnet`;
DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `support_list_machines_in_subnet`(IN IN_regex_ip VARCHAR(255))
BEGIN
SELECT DISTINCT
    `xmppmaster`.`machines`.`hostname` as Hostname, 
    `xmppmaster`.`network`.`ipaddress` as IPAddress, 
    `xmppmaster`.`network`.`gateway` as Gateway, 
    `xmppmaster`.`machines`.`groupdeploy` as RelayJID, 
    `xmppmaster`.`network`.`mask` as Subnet,
    `xmppmaster`.`glpi_entity`.`name` as EntityName,
    `xmppmaster`.`glpi_entity`.`complete_name` as FullEntityName,
    `xmppmaster`.`glpi_location`.`complete_name` as FullLocationName,
    `xmppmaster`.`machines`.`enabled` as Online 
FROM `xmppmaster`.`machines` 
LEFT OUTER JOIN `xmppmaster`.`network` 
    ON `xmppmaster`.`machines`.`id` = `xmppmaster`.`network`.`machines_id` 
LEFT OUTER JOIN `xmppmaster`.`glpi_location` 
    ON `xmppmaster`.`glpi_location`.`id` = `xmppmaster`.`machines`.`glpi_location_id`
LEFT OUTER JOIN `xmppmaster`.`glpi_entity` 
    ON `xmppmaster`.`glpi_entity`.`id` = `xmppmaster`.`machines`.`glpi_entity_id`
WHERE `xmppmaster`.`machines`.`id` IN (SELECT 
            `xmppmaster`.`network`.`machines_id`
        FROM
            `xmppmaster`.`network`
        WHERE
            `xmppmaster`.`network`.`ipaddress` REGEXP IN_regex_ip)
AND `xmppmaster`.`machines`.`agenttype` = 'machine'
AND `xmppmaster`.`network`.`ipaddress` != ''
GROUP BY `xmppmaster`.`network`.`machines_id`;
END$$
DELIMITER ;

INSERT INTO `xmppmaster`.`support_help_command` (`name`, `description`, `example`, `type`) VALUES ('support_list_machines_in_subnet', 'This procedure is used to list machines having the specified subnet.', 'call support_list_machines_in_subnet(\'^55\.44\.1[2-5]\.\');', 'P');



-- ----------------------------------------------------------------------
-- Definition of functions for support
-- These functions are prefixed fs_
-- ----------------------------------------------------------------------

-- /##########################################################################\
-- | function  fs_help                                                        |
-- | cette function permet de demander de l'aide sur 1 function siveo definie |
-- | exemple : select fs_help("%restart_deploy%" );                           |
-- \##########################################################################/
USE `xmppmaster`;
DROP function IF EXISTS `fs_help`;
DELIMITER $$
USE `xmppmaster`$$
CREATE FUNCTION `fs_help`(command char(255) ) RETURNS text CHARSET utf8
BEGIN
set @typestr = "No definie type";
SELECT
    name, description, example, result, type
INTO @namects , @descriptioncts , @examplects , @resultcts , @typects FROM
    support_help_command
WHERE
    name LIKE command
    limit 1;

if @typects = "p" then
	set @typestr = "Procedure" ;
 else
	if @typects = "f" then
		set @typestr = "Function" ;
    else
        if @typects = "v" then
            set  @typestr = "View" ;
		end if;
	end if;
end if;

SELECT
    CONCAT(@typestr,
            ' : ',
            @namects,
            '\nDecription : \n\t',
             COALESCE(@descriptioncts,''),
            '\n\nExemple :\n\t',
            COALESCE(@examplects, '')) INTO @re1;

SELECT CONCAT("\nresult :\n",COALESCE(@resultcts, '')) INTO @re2;

SELECT CONCAT( @re1, @re2) into @re1;

RETURN @re1;
END$$
DELIMITER ;


-- /#####################################################################\
-- | function fs_jiduser                                                 |
-- | cette function renvoi user d'un jid                                 |
-- | exemple select fs_jiduser("jfk@pulse/ressource1");                  |
-- \#####################################################################/
USE `xmppmaster`;
DROP function IF EXISTS `fs_jiduser`;
DELIMITER $$
USE `xmppmaster`$$
CREATE FUNCTION `fs_jiduser`(jid char(255) ) RETURNS char(255) CHARSET utf8
BEGIN
-- return le user d'un jid
RETURN  substring_index(jid, '@', 1);
END$$
DELIMITER ;


-- /#####################################################################\
-- | function fs_jidresource                                             |
-- | cette function renvoi resource d'un jid                             |
-- | exemple select fs_jidresource("jfk@pulse/ressource1");              |
-- \#####################################################################/
USE `xmppmaster`;
DROP function IF EXISTS `fs_jidresource`;
DELIMITER $$
USE `xmppmaster`$$
CREATE FUNCTION `fs_jidresource`(jid char(255)) RETURNS char(255) CHARSET utf8
BEGIN
-- return la resource d'un jid
RETURN  substring_index(jid, '/', -1);
END$$
DELIMITER ;

INSERT INTO `xmppmaster`.`support_help_command` (`name`, `description`, `example`, `type`, `result`) VALUES ('fs_jidresource', ' cette function renvoi resource d\'un jid      ', 'select fs_jidresource(\"jfk@pulse/ressource1\");    ', 'F', '+----------------------------------------+\n| fs_jidresource(\"jfk@pulse/ressource1\") |\n+----------------------------------------+\n| ressource1                             |\n+----------------------------------------+\n');


-- /#####################################################################\
-- | function fs_jiddomain                                               |
-- | cette function renvoi domain d'un jid                               |
-- | exemple select fs_jiddomain("jfk.xya@pulse/ressource1");            |
-- \#####################################################################/
USE `xmppmaster`;
DROP function IF EXISTS `fs_jiddomain`;
DELIMITER $$
USE `xmppmaster`$$
CREATE FUNCTION `fs_jiddomain` (jid char(255))
	RETURNS char(255) CHARSET utf8
BEGIN
-- return le domaine d'un jid
RETURN  substring_index(substring_index(jid, '/', 1), '@', -1);
END$$
DELIMITER ;

INSERT INTO `xmppmaster`.`support_help_command` (`name`, `description`, `example`, `type`, `result`) VALUES ('fs_jiddomain', 'cette function renvoi domain d\'un jid', 'select fs_jiddomain(\"jfk.xya@pulse/ressource1\");', 'F', '+------------------------------------------+\n| fs_jiddomain(\"jfk.xya@pulse/ressource1\") |\n+------------------------------------------+\n| pulse                                    |\n+------------------------------------------+\n');


-- /#####################################################################\
-- | function fs_jidusertrue                                             |
-- | cette function renvoi domain d'un jid sans le .xxx de user          |
-- | exemple select fs_jidusertrue("jfk.xya@pulse/ressource1");          |
-- \#####################################################################/
USE `xmppmaster`;
DROP function IF EXISTS `fs_jidusertrue`;
DELIMITER $$
USE `xmppmaster`$$
CREATE FUNCTION `fs_jidusertrue` (jid char(255))
	RETURNS char(255) CHARSET utf8
BEGIN
-- return le user d'un jid sans .xxx
RETURN  substring_index(substring_index(jid, '@', 1), '.', 1);
END$$
DELIMITER ;

INSERT INTO `xmppmaster`.`support_help_command` (`name`, `description`, `example`, `type`, `result`) VALUES ('fs_jidusertrue', 'cette function renvoi domain d\'un jid sans le .xxx de user ', 'select fs_jidusertrue(\"jfk.xya@pulse/ressource1\");', 'F', '+--------------------------------------------+\n| fs_jidusertrue(\"jfk.xya@pulse/ressource1\") |\n+--------------------------------------------+\n| jfk                                        |\n+--------------------------------------------+\n');


-- /########################################################################\
-- | function fs_tablefields                                                |
-- | cette function renvoie la list des champ de la table xmppmaster passee |
-- | exemple select fs_jidusershort("jfk.xya@pulse/ressource1);             |
-- \########################################################################/
USE `xmppmaster`;
DROP function IF EXISTS `fs_tablefields`;
DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `fs_tablefields`(tablename char(255)) RETURNS text CHARSET utf8
BEGIN
select listcolumn  into @malist from (
  SELECT GROUP_CONCAT(COLUMN_NAME) as listcolumn
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = 'xmppmaster' AND TABLE_NAME like tablename ) as dede;
 RETURN @malist;
END$$
DELIMITER ;

INSERT INTO `xmppmaster`.`support_help_command` (`name`, `description`, `example`, `type`, `result`) VALUES ('fs_tablefields', 'cette function renvoie la list des champs de la table xmppmaster passee', 'select fs_tablefields(\'logs\');', 'F', '+----------------------------------------------------------------------------------+\n| fs_tablefields(\'logs\')                                                            |\n+----------------------------------------------------------------------------------+\n| id,date,type,module,text,fromuser,touser,action,sessionname,how,why,priority,who |\n+----------------------------------------------------------------------------------+\n');




-- ----------------------------------------------------------------------
-- Definition of views for support
-- These views are prefixed vs_
-- ----------------------------------------------------------------------

-- /#####################################################################\
-- | View vs_stats_ars                                                   |
-- | cette vue permet de voir la repartition des machine des ars         |
-- | exemple select * from vs_stats_ars;                                 |
-- \#####################################################################/
USE `xmppmaster`;
CREATE
    OR REPLACE ALGORITHM = UNDEFINED
VIEW `vs_stats_ars` AS
    SELECT
        `machines`.`groupdeploy` AS `groupdeploy`,
        SUM(CASE
            WHEN LOCATE('linux', `machines`.`platform`) THEN 1
            ELSE 0
        END) AS `nblinuxmachine`,
        SUM(CASE
            WHEN LOCATE('windows', `machines`.`platform`) THEN 1
            ELSE 0
        END) AS `nbwindows`,
        SUM(CASE
            WHEN LOCATE('darwin', `machines`.`platform`) THEN 1
            ELSE 0
        END) AS `nbdarwin`,
        SUM(CASE
            WHEN `machines`.`enabled` = '1' THEN 1
            ELSE 0
        END) AS `mach_on`,
        SUM(CASE
            WHEN `machines`.`enabled` = '0' THEN 1
            ELSE 0
        END) AS `mach_off`,
        SUM(CASE
            WHEN
                SUBSTR(`machines`.`uuid_inventorymachine`,
                    1,
                    1) = 'U'
            THEN
                0
            ELSE 1
        END) AS `uninventoried`,
        SUM(CASE
            WHEN
                SUBSTR(`machines`.`uuid_inventorymachine`,
                    1,
                    1) = 'U'
            THEN
                1
            ELSE 0
        END) AS `inventoried`,
        SUM(CASE
            WHEN
                (`machines`.`enabled` = '1'
                    AND SUBSTR(`machines`.`uuid_inventorymachine`,
                    1,
                    1) <> 'U')
            THEN
                1
            ELSE 0
        END) AS `uninventoried_online`,
        SUM(CASE
            WHEN
                (`machines`.`enabled` = '0'
                    AND SUBSTR(`machines`.`uuid_inventorymachine`,
                    1,
                    1) <> 'U')
            THEN
                1
            ELSE 0
        END) AS `uninventoried_offline`,
        SUM(CASE
            WHEN
                (`machines`.`enabled` = 1
                    AND SUBSTR(`machines`.`uuid_inventorymachine`,
                    1,
                    1) = 'U')
            THEN
                1
            ELSE 0
        END) AS `inventoried_online`,
        SUM(CASE
            WHEN
                (`machines`.`enabled` = '0'
                    AND SUBSTR(`machines`.`uuid_inventorymachine`,
                    1,
                    1) = 'U')
            THEN
                1
            ELSE 0
        END) AS `inventoried_offline`,
        SUM(CASE
            WHEN `machines`.`id` THEN 1
            ELSE 0
        END) AS `nbmachine`,
        SUM(CASE
            WHEN COALESCE(`machines`.`uuid_serial_machine`, '') <> '' THEN 1
            ELSE 0
        END) AS `with_uuid_serial`,
        SUM(CASE
            WHEN `machines`.`classutil` = 'both' THEN 1
            ELSE 0
        END) AS `bothclass`,
        SUM(CASE
            WHEN `machines`.`classutil` = 'public' THEN 1
            ELSE 0
        END) AS `publicclass`,
        SUM(CASE
            WHEN `machines`.`classutil` = 'private' THEN 1
            ELSE 0
        END) AS `privateclass`,
        SUM(CASE
            WHEN COALESCE(`machines`.`ad_ou_user`, '') <> '' THEN 1
            ELSE 0
        END) AS `nb_ou_user`,
        SUM(CASE
            WHEN COALESCE(`machines`.`ad_ou_machine`, '') <> '' THEN 1
            ELSE 0
        END) AS `nb_OU_mach`,
        SUM(CASE
            WHEN `machines`.`kiosk_presence` = 'True' THEN 1
            ELSE 0
        END) AS `kioskon`,
        SUM(CASE
            WHEN `machines`.`kiosk_presence` = 'FALSE' THEN 1
            ELSE 0
        END) AS `kioskoff`,
        SUM(CASE
            WHEN `machines`.`need_reconf` THEN 1
            ELSE 0
        END) AS `nbmachinereconf`
    FROM
        `machines`
    WHERE
        `machines`.`groupdeploy` IN (SELECT
                `relayserver`.`jid`
            FROM
                `relayserver`)
            AND `machines`.`agenttype` = 'machine'
    GROUP BY `machines`.`groupdeploy`;

INSERT INTO `xmppmaster`.`support_help_command` (`name`, `description`, `example`, `type`, `result`) VALUES ('vs_stats_ars', 'cette vue donne la répartition des machines pour les ars', ' select * from vs_stats_ars; ', 'V', '*************************** 1. row ***************************\n          groupdeploy: rspulse@pulse/000c29f61ff6\n       nblinuxmachine: 2\n            nbwindows: 1\n             nbdarwin: 0\n              mach_on: 1\n             mach_off: 2\n        uninventoried: 0\n          inventoried: 3\n uninventoried_online: 0\nuninventoried_offline: 0\n   inventoried_online: 1\n  inventoried_offline: 2\n            nbmachine: 3\n     with_uuid_serial: 3\n            bothclass: 3\n          publicclass: 0\n         privateclass: 0\n           nb_ou_user: 0\n           nb_OU_mach: 0\n              kioskon: 0\n             kioskoff: 3\n      nbmachinereconf: 0\n');


SET FOREIGN_KEY_CHECKS=0;

-- ---------------------------------------------------------------------
-- ADD ccolunm    subdep table deploy
-- ADD index ind_sub_dep table deploy
- ----------------------------------------------------------------------

ALTER TABLE `xmppmaster`.`deploy`
ADD COLUMN IF NOT EXISTS `subdep` VARCHAR(45) NULL DEFAULT NULL AFTER `result`;
ALTER TABLE `xmppmaster`.`deploy`
ADD INDEX IF NOT EXISTS `ind_sub_dep` (`subdep` ASC) ;

-- ---------------------------------------------------------------------
-- ADD index ind_session table users
-- ADD index ind__hostname table users
- ----------------------------------------------------------------------

ALTER TABLE `xmppmaster`.`users` 
ADD INDEX IF NOT EXISTS `ind_session` (`namesession` ASC) ,
ADD INDEX IF NOT EXISTS `ind__hostname` (`hostname` ASC) ;

SET FOREIGN_KEY_CHECKS=1;
-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 70;

COMMIT;
