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
-- | procedure support_restart_deploy                                    |
-- | cette procedure permet de remettre 1 deployment.                    |
-- | les log de la session passe sont supprimer.                         |
-- | exemple call support_restart_deploy('command3bd50e905a4f4c4e82');   |
-- \#####################################################################/
USE `xmppmaster`;
DROP procedure IF EXISTS `support_restart_deploy`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`support_restart_deploy`;
;


DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `support_restart_deploy`(IN IN_sessid VARCHAR(255))
BEGIN
set @cmd = (select command from  xmppmaster.deploy where sessionid like IN_sessid);
set @grp = (select group_uuid from  xmppmaster.deploy where sessionid like IN_sessid );
set @name_mach = (select FS_JIDUSERTRUE(host) as host from  xmppmaster.deploy where sessionid like IN_sessid );
set @fk_commands_on_host = (select fk_commands from msc.commands_on_host where host=@name_mach and fk_commands = @cmd);

DELETE FROM `xmppmaster`.`logs` WHERE (`sessionname` like IN_sessid);
DELETE FROM `xmppmaster`.`deploy` WHERE (`sessionid` like IN_sessid);
UPDATE `msc`.`commands` SET `end_date` = now() + INTERVAL 1 DAY WHERE (`id` = @cmd) and  NOW() > end_date;
UPDATE `msc`.`phase` SET `state` = 'ready' WHERE (`msc`.`phase`.`fk_commands_on_host` = @cmd );
END$$

DELIMITER ;


-- ----------------------------------------------------------------------
-- Definition functions for support
-- ces fonctions sont prfixe par fs_
- ----------------------------------------------------------------------
-- /#####################################################################\
-- | function fs_jiduser                                                 |
-- | cette function renvoi user d'un jid                                 |
-- | exemple select fs_jiduser("jfk@pulse/ressource1);                   |
-- \#####################################################################/
USE `xmppmaster`;
DROP function IF EXISTS `fs_jiduser`;
;
DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `fs_jiduser`(jid char(255) ) RETURNS char(255) CHARSET utf8
BEGIN
-- return le user d'un jid
RETURN  substring_index(jid, '@', 1);
END$$
DELIMITER ;
;
-- /#####################################################################\
-- | function fs_jidresource                                               |
-- | cette function renvoi resource d'un jid                               |
-- | exemple select fs_jidresource("jfk@pulse/ressource1);                 |
-- \#####################################################################/
USE `xmppmaster`;
DROP function IF EXISTS `fs_jidresource`;
DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `fs_jidresource`(jid char(255)) RETURNS char(255) CHARSET utf8
BEGIN
-- return la resource d'un jid
RETURN  substring_index(jid, '/', -1)
END$$
DELIMITER ;
-- /#####################################################################\
-- | function fs_jiddomain                                             |
-- | cette function renvoi domain d'un jid sans le .xxx de user          |
-- | exemple select fs_jiddomain("jfk.xya@pulse/ressource1);                 |
-- \#####################################################################/
USE `xmppmaster`;
DROP function IF EXISTS `fs_jiddomain`;
DELIMITER $$
USE `xmppmaster`$$
CREATE FUNCTION `fs_jiddomain` (jid char(255)) 
	RETURNS char(255) CHARSET utf8
BEGIN
-- return le domaine d'un jid
RETURN  substring_index(substring_index(jid, '/', 1), '@', -1) 
END$$
DELIMITER ;
-- /#####################################################################\
-- | function fs_jidusertrue                                             |
-- | cette function renvoi domain d'un jid sans le .xxx de user          |
-- | exemple select fs_jidusershort("jfk.xya@pulse/ressource1);                 |
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
