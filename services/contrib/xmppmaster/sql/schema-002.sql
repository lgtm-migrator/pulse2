--
-- (c) 2016 Siveo, http://www.siveo.net/
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

START TRANSACTION;

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------

ALTER TABLE  `deploy` ADD `title` varchar(255) DEFAULT NULL;
ALTER TABLE  `deploy` ADD `startcmd` timestamp NULL DEFAULT NULL;
ALTER TABLE  `deploy` ADD `endcmd` timestamp NULL DEFAULT NULL;
ALTER TABLE  `deploy` ADD `group_uuid` varchar(11) DEFAULT NULL;
ALTER TABLE  `deploy` ADD `macadress` varchar(255) DEFAULT NULL;
ALTER TABLE  `deploy` DROP `deploycol`;

UPDATE version SET Number = 2;

COMMIT;
