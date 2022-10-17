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

START TRANSACTION;
USE `xmppmaster`;
CREATE TABLE IF NOT EXISTS `up_packages` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  PRIMARY KEY (`updateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- ----------------------------------------------------------------------
-- CREATE TABLE update_data
-- this table are the updates windows
-- this table is the update_data table image of table base_wsusscn2.update_data
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_reinit_table_update_data`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_reinit_table_update_data`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_reinit_table_update_data`()
begin
        set  @existtable_in_base_wsusscn2 := ( select EXISTS (
            SELECT *
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = 'base_wsusscn2'
                AND TABLE_NAME = 'update_data'));

        set  @existtable_in_xmppmaster := NULL;
        if @existtable_in_base_wsusscn2 is not null then
            --  table existtable
            DROP TABLE IF EXISTS xmppmaster.update_datacopy ;
            create table xmppmaster.update_datacopy as ( SELECT * FROM base_wsusscn2.update_data);
            -- --------------------------------------------------------
            -- creation des index sur la table copie
            --
            -- --------------------------------------------------------
            ALTER TABLE `xmppmaster`.`update_datacopy`
                CHANGE COLUMN `updateid` `updateid` VARCHAR(38) CHARACTER SET 'utf8mb4' NOT NULL ,
                ADD PRIMARY KEY (`updateid`),
                ADD UNIQUE INDEX `updateid_UNIQUE` (`updateid` ASC) ;


            ALTER TABLE `xmppmaster`.`update_datacopy`
                ADD INDEX `ind_product` (`product` ASC);

            ALTER TABLE `xmppmaster`.`update_datacopy`
                ADD INDEX `indkb` (`kb` ASC);


            ALTER TABLE `xmppmaster`.`update_datacopy`
                ADD INDEX `ind_update_classification` (`updateclassification` ASC) ;


            ALTER TABLE `xmppmaster`.`update_datacopy`
                ADD INDEX `ind_replaceby` (`supersededby` ASC);


            ALTER TABLE `xmppmaster`.`update_datacopy`
                ADD INDEX `ind_title` (`title` ASC);

            ALTER TABLE `xmppmaster`.`update_datacopy`
                ADD INDEX `ind_category` (`category` ASC);

            ALTER TABLE `xmppmaster`.`update_datacopy`
                ADD INDEX `ind_product_family` (`productfamily` ASC) ;


            ALTER TABLE `xmppmaster`.`update_datacopy`
                ADD INDEX `ind_msrcseverity` (`msrcseverity` ASC) ;


            ALTER TABLE `xmppmaster`.`update_datacopy`
            ADD INDEX `ind_msrcnumber` (`msrcnumber` ASC) ;


            ALTER TABLE `xmppmaster`.`update_datacopy`
            ADD INDEX `ind_revisionnumber` (`revisionnumber` ASC) ;


		DROP TABLE IF EXISTS xmppmaster.update_data ;
           ALTER TABLE `xmppmaster`.`update_datacopy`
              RENAME TO  `xmppmaster`.`update_data` ;

        end if;
            CREATE TABLE  IF NOT EXISTS  `update_data` (
                `updateid` varchar(38) CHARACTER SET utf8mb4 NOT NULL,
                `revisionid` varchar(16) CHARACTER SET utf8mb4 NOT NULL,
                `creationdate` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
                `company` varchar(36) CHARACTER SET utf8mb4 DEFAULT '',
                `product` varchar(1024) CHARACTER SET utf8mb4 DEFAULT '',
                `productfamily` varchar(52) CHARACTER SET utf8mb4 DEFAULT '',
                `updateclassification` varchar(36) CHARACTER SET utf8mb4 DEFAULT '',
                `prerequisite` varchar(4096) CHARACTER SET utf8mb4 DEFAULT '',
                `title` varchar(1024) CHARACTER SET utf8mb4 DEFAULT '',
                `description` varchar(4096) CHARACTER SET utf8mb4 DEFAULT '',
                `msrcseverity` varchar(16) CHARACTER SET utf8mb4 DEFAULT '',
                `msrcnumber` varchar(16) CHARACTER SET utf8mb4 DEFAULT '',
                `kb` varchar(16) CHARACTER SET utf8mb4 DEFAULT '',
                `languages` varchar(16) CHARACTER SET utf8mb4 DEFAULT '',
                `category` varchar(128) CHARACTER SET utf8mb4 DEFAULT '',
                `supersededby` varchar(3072) CHARACTER SET utf8mb4 DEFAULT '',
                `supersedes` text CHARACTER SET utf8mb4 DEFAULT NULL,
                `payloadfiles` varchar(2048) CHARACTER SET utf8mb4 DEFAULT '',
                `revisionnumber` varchar(30) CHARACTER SET utf8mb4 DEFAULT '',
                `bundledby_revision` varchar(30) CHARACTER SET utf8mb4 DEFAULT '',
                `isleaf` varchar(6) CHARACTER SET utf8mb4 DEFAULT '',
                `issoftware` varchar(30) CHARACTER SET utf8mb4 DEFAULT '',
                `deploymentaction` varchar(30) CHARACTER SET utf8mb4 DEFAULT '',
                    PRIMARY KEY (`updateid`),
                    UNIQUE KEY `updateid_UNIQUE` (`updateid`),
                    KEY `ind_product` (`product`(768)),
                    KEY `indkb` (`kb`),
                    KEY `ind_update_classification` (`updateclassification`),
                    KEY `ind_replaceby` (`supersededby`(768)),
                    KEY `ind_title` (`title`(768)),
                    KEY `ind_category` (`category`),
                    KEY `ind_product_family` (`productfamily`),
                    KEY `ind_msrcseverity` (`msrcseverity`),
                    KEY `ind_msrcnumber` (`msrcnumber`),
                    KEY `ind_revisionnumber` (`revisionnumber`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
     END$$

DELIMITER ;
;

-- Execute the procedure
call up_reinit_table_update_data();



-- ----------------------------------------------------------------------
-- CREATE TABLE up_machine_windows
-- this table are the updates machine
-- this table contient les updates des machines possible
-- ----------------------------------------------------------------------

CREATE TABLE `up_machine_windows` (
  `id_machine` int(11) NOT NULL,
  `update_id` varchar(38) NOT NULL,
  `kb` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id_machine`,`update_id`),
  KEY `up_machine_windows_id_machine1_idx` (`id_machine`),
  CONSTRAINT `fk_up_machine_windows_1` FOREIGN KEY (`id_machine`) REFERENCES `machines` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ;


-- Drop the procedure
-- drop procedure intit_table_update_data;

-- -------------------------------------------------------
-- cette procedure permet de rechercher les updates pour windows
-- Exemple
-- call up_search_kb_windows( "%Windows 10 Version 21H2 for x64-based%",
--       "5015730,5003791,5012170,5016616,5006753,5007273,5014035,5015895,5005699");
-- 1er parametre le filtre dans title
-- 2eme parametre les kb trouver sur la machine wmic qfe
-- cette procedure renvois les kbs a installer
-- -------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_search_kb_windows`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_search_kb_windows`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_search_kb_windows`( in FILTERtable varchar(2048), in KB_LIST varchar(2048))
BEGIN
DECLARE _next TEXT DEFAULT NULL;
DECLARE _nextlen INT DEFAULT NULL;
DECLARE _value TEXT DEFAULT NULL;
DECLARE _list MEDIUMTEXT;
DECLARE kb_next TEXT DEFAULT NULL;
DECLARE kb_nextlen INT DEFAULT NULL;
DECLARE kb_value TEXT DEFAULT NULL;
DECLARE kb_updateid  varchar(50) DEFAULT NULL;
-- declare name table temporaire
DECLARE tmp_kb_updateid varchar(90) DEFAULT "tmp_kb_updateid";
DECLARE tmp_t1 varchar(90) DEFAULT "tmp_t1";
DECLARE tmp_my_mise_a_jour varchar(90) DEFAULT "tmp_my_mise_a_jour";
DECLARE tmp_result_procedure varchar(90) DEFAULT "tmp_result_procedure";

SELECT
    CONCAT('tmp_kb_updateid_',
            REPLACE(UUID(), '-', ''))
INTO tmp_kb_updateid;
SELECT CONCAT('tmp_t1_', REPLACE(UUID(), '-', '')) INTO tmp_t1;
SELECT
    CONCAT('tmp_my_mise_a_jour_',
            REPLACE(UUID(), '-', ''))
INTO tmp_my_mise_a_jour;
SELECT
    CONCAT('tmp_result_procedure_',
            REPLACE(UUID(), '-', ''))
INTO tmp_result_procedure;

CREATE temporary TABLE IF NOT EXISTS `tmp_kb_updateid` (
  `c1` varchar(64) NOT NULL,
  PRIMARY KEY (`c1`),
  UNIQUE KEY `c1_UNIQUE` (`c1`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ;
truncate tmp_kb_updateid;

iteratorkb:
LOOP
  -- exit the loop if the list seems empty or was null;
  -- this extra caution is necessary to avoid an endless loop in the proc.
  IF CHAR_LENGTH(TRIM(kb_list)) = 0 OR kb_list IS NULL THEN
    LEAVE iteratorkb;
  END IF;

  -- capture the next value from the list
  SET kb_next = SUBSTRING_INDEX(kb_list,',',1);

  -- save the length of the captured value; we will need to remove this
  -- many characters + 1 from the beginning of the string
  -- before the next iteration
  SET kb_nextlen = CHAR_LENGTH(kb_next);

  -- trim the value of leading and trailing spaces, in case of sloppy CSV strings
  SET kb_value = TRIM(kb_next);

  -- insert the extracted value into the target table
  -- select updateid into kb_updateid from xmppmaster.update_data where kb = kb_value;
  -- select kb_updateid;
  INSERT IGNORE INTO tmp_kb_updateid (c1) VALUES (kb_value );

  -- rewrite the original string using the `INSERT()` string function,
  -- args are original string, start position, how many characters to remove,
  -- and what to "insert" in their place (in this case, we "insert"
  -- an empty string, which removes kb_nextlen + 1 characters)
  SET kb_list = INSERT(kb_list,1,kb_nextlen + 1,'');
END LOOP;
-- ------ generation table kb tmp_kb_updateid -----------
-- call list_kb_machine(KBLIST);
-- les updatesid des mise a jour deja installer seront inclus dans la table des update excluts tmp_t1

-- creation table filter
CREATE temporary TABLE IF NOT EXISTS tmp_my_mise_a_jour AS (SELECT * FROM
    xmppmaster.update_data
WHERE
    title LIKE FILTERtable
    and title not like "%Dynamic Cumulative Update%"
    and supersededby in (null,"" ));
SELECT
    GROUP_CONCAT(DISTINCT supersedes
        ORDER BY supersedes ASC
        SEPARATOR ',')
INTO _list FROM
    tmp_my_mise_a_jour;


CREATE temporary TABLE IF NOT EXISTS `tmp_t1` (
    `c1` VARCHAR(64) NOT NULL,
    PRIMARY KEY (`c1`),
    UNIQUE KEY `c1_UNIQUE` (`c1`)
)  ENGINE=INNODB DEFAULT CHARSET=UTF8;
truncate tmp_t1;
iterator:
LOOP
  -- exit the loop if the list seems empty or was null;
  -- this extra caution is necessary to avoid an endless loop in the proc.
  IF CHAR_LENGTH(TRIM(_list)) = 0 OR _list IS NULL THEN
    LEAVE iterator;
  END IF;

  -- capture the next value from the list
  SET _next = SUBSTRING_INDEX(_list,',',1);

  -- save the length of the captured value; we will need to remove this
  -- many characters + 1 from the beginning of the string
  -- before the next iteration
  SET _nextlen = CHAR_LENGTH(_next);
  -- trim the value of leading and trailing spaces, in case of sloppy CSV strings
  SET _value = TRIM(_next);
  -- insert the extracted value into the target table
  INSERT IGNORE INTO tmp_t1 (c1) VALUES (_value);
  -- rewrite the original string using the `INSERT()` string function,
  -- args are original string, start position, how many characters to remove,
  -- and what to "insert" in their place (in this case, we "insert"
  -- an empty string, which removes _nextlen + 1 characters)
  SET _list = INSERT(_list,1,_nextlen + 1,'');
END LOOP;
DELETE FROM `tmp_t1`
WHERE
    (`c1` = '');
-- injection les update_id deja installer dans tmp_t1
 INSERT IGNORE INTO tmp_t1  select updateid from xmppmaster.update_data where kb in (select c1 from tmp_kb_updateid);

CREATE temporary TABLE tmp_result_procedure AS (SELECT * FROM
    tmp_my_mise_a_jour
WHERE
    updateid NOT IN (SELECT
            c1
        FROM
            tmp_t1));
-- on supprime les updateid qui sont dans select c1 from tmp_kb_updateid
DELETE FROM tmp_result_procedure
WHERE
    updateid IN (SELECT
        c1
    FROM
        tmp_kb_updateid);
drop temporary table tmp_kb_updateid;
drop temporary table tmp_t1;
drop temporary table tmp_my_mise_a_jour;
SELECT
    *
FROM
    tmp_result_procedure;
drop temporary table tmp_result_procedure;
END$$

DELIMITER ;
;

-- -------------------------------------------------------
-- cette procedure permet de rechercher les updates pour windows
-- plus de parametre de recherche
-- Exemple
-- call up_search_kb_windows1( "","%Windows 10%","%21H2%","Critical","%x64%",
--       "5015730,5003791,5012170,5016616,5006753,5007273,5014035,5015895,5005699");
-- 1er parametre le filtre dans title
-- 2eme parametre les kb trouver sur la machine wmic qfe
-- cette procedure renvois les kbs a installer
-- -------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `up_search_kb_windows1`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_search_kb_windows1`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_search_kb_windows1`( in FILTERtable varchar(2048),
                                           in PRODUCTtable varchar(80),
                                           in VERSIONtable varchar(20),
                                           in MSRSEVERITYtable varchar(40),
                                           in ARCHItable varchar(20),
                                           in KB_LIST varchar(2048))
BEGIN
	DECLARE _next TEXT DEFAULT NULL;
	DECLARE _nextlen INT DEFAULT NULL;
	DECLARE _value TEXT DEFAULT NULL;
	DECLARE _list MEDIUMTEXT;

	DECLARE kb_next TEXT DEFAULT NULL;
	DECLARE kb_nextlen INT DEFAULT NULL;
	DECLARE kb_value TEXT DEFAULT NULL;
	DECLARE kb_updateid  varchar(50) DEFAULT NULL;
	-- declare name table temporaire
	-- tmp_kb_updateid contient les updateid correspondant a la liste klist
	DECLARE tmp_kb_updateid varchar(90) DEFAULT "tmp_kb_updateid";

	DECLARE tmp_t1 varchar(90) DEFAULT "tmp_t1";
	DECLARE tmp_my_mise_a_jour varchar(90) DEFAULT "tmp_my_mise_a_jour";
	DECLARE tmp_result_procedure varchar(90) DEFAULT "tmp_result_procedure";

	DECLARE msrseverity varchar(40) DEFAULT "Critical";
	DECLARE produc_windows varchar(80) DEFAULT '%Windows 10%';
	DECLARE archi varchar(20) DEFAULT "%x64%";
	DECLARE version varchar(20) DEFAULT "%21H2%";
	DECLARE filterp varchar(2048) DEFAULT "%%";
-- attribution de nom aleatoire au table temporaire
-- uuid random des table
SELECT
    CONCAT('tmp_kb_updateid_',
            REPLACE(UUID(), '-', ''))
                        INTO tmp_kb_updateid;

SELECT CONCAT('tmp_t1_', REPLACE(UUID(), '-', ''))
                        INTO tmp_t1;
SELECT
    CONCAT('tmp_my_mise_a_jour_',
            REPLACE(UUID(), '-', ''))
                        INTO tmp_my_mise_a_jour;

SELECT
    CONCAT('tmp_result_procedure_',
            REPLACE(UUID(), '-', ''))
                        INTO tmp_result_procedure;

-- initialise produc_windows Windows 10 si pas ""
if PRODUCTtable  !="" THEN
    SELECT
        CONCAT('%',PRODUCTtable,'%') INTO produc_windows;
END IF;

-- initialise version 21H2 si pas ""
if VERSIONtable !="" THEN
    SELECT
        CONCAT('%',VERSIONtable,'%') INTO version;
END IF;

-- initialise archi 21H2 si pas ""
if ARCHItable !="" THEN
    SELECT
        CONCAT('%',ARCHItable,'%') INTO archi;
END IF;

-- initialise filter %% si ""
if FILTERtable != "" THEN
    SELECT
        CONCAT('%',FILTERtable,'%') INTO filterp;
END IF;

if MSRSEVERITYtable != "" THEN
	SELECT
		CONCAT('%',MSRSEVERITYtable,'%') INTO msrseverity;
END IF;

CREATE temporary TABLE IF NOT EXISTS `tmp_kb_updateid` (
  `c1` varchar(64) NOT NULL,
  PRIMARY KEY (`c1`),
  UNIQUE KEY `c1_UNIQUE` (`c1`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ;
truncate tmp_kb_updateid;

iteratorkb:
LOOP
  -- exit the loop if the list seems empty or was null;
  -- this extra caution is necessary to avoid an endless loop in the proc.
  IF CHAR_LENGTH(TRIM(kb_list)) = 0 OR kb_list IS NULL THEN
    LEAVE iteratorkb;
  END IF;

  -- capture the next value from the list
  SET kb_next = SUBSTRING_INDEX(kb_list,',',1);

  -- save the length of the captured value; we will need to remove this
  -- many characters + 1 from the beginning of the string
  -- before the next iteration
  SET kb_nextlen = CHAR_LENGTH(kb_next);

  -- trim the value of leading and trailing spaces, in case of sloppy CSV strings
  SET kb_value = TRIM(kb_next);
  -- insert the extracted value into the target table
  -- select updateid into kb_updateid from xmppmaster.update_data where kb = kb_value;
  -- select kb_updateid;
  INSERT IGNORE INTO tmp_kb_updateid (c1) VALUES (kb_value );

  -- rewrite the original string using the `INSERT()` string function,
  -- args are original string, start position, how many characters to remove,
  -- and what to "insert" in their place (in this case, we "insert"
  -- an empty string, which removes kb_nextlen + 1 characters)
  SET kb_list = INSERT(kb_list,1,kb_nextlen + 1,'');
END LOOP;
-- ------ generation table kb tmp_kb_updateid -----------
-- call list_kb_machine(KBLIST);
-- les updatesid des mise a jour deja installer seront inclus dans la table des update excluts tmp_t1

-- depuis la table general on cree 1 table des mise à jour possible
-- on utilise le filter pour definir filter
-- msrcseverity  uniquement  'Critical'

CREATE temporary TABLE IF NOT EXISTS tmp_my_mise_a_jour AS (SELECT * FROM
    xmppmaster.update_data
WHERE
    title LIKE filterp
    and title not like "%Dynamic Cumulative Update%"
    and supersededby in (null,"" )
    AND msrcseverity LIKE msrseverity
    AND product LIKE produc_windows
    AND title LIKE archi
    AND title LIKE version
    );
SELECT
    GROUP_CONCAT(DISTINCT supersedes
        ORDER BY supersedes ASC
        SEPARATOR ',')
INTO _list FROM
    tmp_my_mise_a_jour;

CREATE temporary TABLE IF NOT EXISTS `tmp_t1` (
    `c1` VARCHAR(64) NOT NULL,
    PRIMARY KEY (`c1`),
    UNIQUE KEY `c1_UNIQUE` (`c1`)
)  ENGINE=INNODB DEFAULT CHARSET=UTF8;
truncate tmp_t1;
iterator:
LOOP
  -- exit the loop if the list seems empty or was null;
  -- this extra caution is necessary to avoid an endless loop in the proc.
  IF CHAR_LENGTH(TRIM(_list)) = 0 OR _list IS NULL THEN
    LEAVE iterator;
  END IF;

  -- capture the next value from the list
  SET _next = SUBSTRING_INDEX(_list,',',1);

  -- save the length of the captured value; we will need to remove this
  -- many characters + 1 from the beginning of the string
  -- before the next iteration
  SET _nextlen = CHAR_LENGTH(_next);
  -- trim the value of leading and trailing spaces, in case of sloppy CSV strings
  SET _value = TRIM(_next);
  -- insert the extracted value into the target table
  INSERT IGNORE INTO tmp_t1 (c1) VALUES (_value);
  -- rewrite the original string using the `INSERT()` string function,
  -- args are original string, start position, how many characters to remove,
  -- and what to "insert" in their place (in this case, we "insert"
  -- an empty string, which removes _nextlen + 1 characters)
  SET _list = INSERT(_list,1,_nextlen + 1,'');
END LOOP;
DELETE FROM `tmp_t1`
WHERE
    (`c1` = '');
-- injection les update_id deja installer dans tmp_t1
 INSERT IGNORE INTO tmp_t1  select updateid from xmppmaster.update_data where kb in (select c1 from tmp_kb_updateid);

CREATE temporary TABLE tmp_result_procedure AS (SELECT * FROM
    tmp_my_mise_a_jour
WHERE
    updateid NOT IN (SELECT
            c1
        FROM
            tmp_t1));
-- on supprime les updateid qui sont dans select c1 from tmp_kb_updateid
DELETE FROM tmp_result_procedure
WHERE
    updateid IN (SELECT
        c1
    FROM
        tmp_kb_updateid);
drop temporary table tmp_kb_updateid;
drop temporary table tmp_t1;
drop temporary table tmp_my_mise_a_jour;
SELECT
    *
FROM
    tmp_result_procedure;
drop temporary table tmp_result_procedure;

END$$

DELIMITER ;
;
/*
-- ------ generation table kb tmp_kb_updateid -----------
-- call list_kb_machine(KBLIST);
-- les updatesid des mise a jour deja installer seront inclus dans la table des update excluts tmp_t1

-- depuis la table general on cree 1 table des mise à jour possible
-- on utilise le filter pour definir filter
-- msrcseverity  uniquement  'Critical'

CREATE temporary TABLE IF NOT EXISTS tmp_my_mise_a_jour AS (SELECT * FROM
    xmppmaster.update_data
WHERE
    title LIKE filterp
    and title not like "%Dynamic Cumulative Update%"
    and supersededby in (null,"" )
    AND msrcseverity LIKE msrseverity
    AND product LIKE produc_windows
    AND title LIKE archi
    AND title LIKE version
    );
SELECT
    GROUP_CONCAT(DISTINCT supersedes
        ORDER BY supersedes ASC
        SEPARATOR ',')
INTO _list FROM
    tmp_my_mise_a_jour;

CREATE temporary TABLE IF NOT EXISTS `tmp_t1` (
    `c1` VARCHAR(64) NOT NULL,
    PRIMARY KEY (`c1`),
    UNIQUE KEY `c1_UNIQUE` (`c1`)
)  ENGINE=INNODB DEFAULT CHARSET=UTF8;
truncate tmp_t1;
iterator:
LOOP
  -- exit the loop if the list seems empty or was null;
  -- this extra caution is necessary to avoid an endless loop in the proc.
  IF CHAR_LENGTH(TRIM(_list)) = 0 OR _list IS NULL THEN
    LEAVE iterator;
  END IF;

  -- capture the next value from the list
  SET _next = SUBSTRING_INDEX(_list,',',1);

  -- save the length of the captured value; we will need to remove this
  -- many characters + 1 from the beginning of the string
  -- before the next iteration
  SET _nextlen = CHAR_LENGTH(_next);
  -- trim the value of leading and trailing spaces, in case of sloppy CSV strings
  SET _value = TRIM(_next);
  -- insert the extracted value into the target table
  INSERT IGNORE INTO tmp_t1 (c1) VALUES (_value);
  -- rewrite the original string using the `INSERT()` string function,
  -- args are original string, start position, how many characters to remove,
  -- and what to "insert" in their place (in this case, we "insert"
  -- an empty string, which removes _nextlen + 1 characters)
  SET _list = INSERT(_list,1,_nextlen + 1,'');
END LOOP;
DELETE FROM `tmp_t1`
WHERE
    (`c1` = '');
-- injection les update_id deja installer dans tmp_t1
 INSERT IGNORE INTO tmp_t1  select updateid from xmppmaster.update_data where kb in (select c1 from tmp_kb_updateid);

CREATE temporary TABLE tmp_result_procedure AS (SELECT * FROM
    tmp_my_mise_a_jour
WHERE
    updateid NOT IN (SELECT
            c1
        FROM
            tmp_t1));
-- on supprime les updateid qui sont dans select c1 from tmp_kb_updateid
DELETE FROM tmp_result_procedure
WHERE
    updateid IN (SELECT
        c1
    FROM
        tmp_kb_updateid);
drop temporary table tmp_kb_updateid;
drop temporary table tmp_t1;
drop temporary table tmp_my_mise_a_jour;
SELECT
    *
FROM
    tmp_result_procedure;
drop temporary table tmp_result_procedure;

END$$

DELIMITER ;
;*/


DELIMITER $$
USE `xmppmaster`$$
CREATE  PROCEDURE `update_datetime`()
BEGIN
  UPDATE `xmppmaster`.`update_data`
SET
    `creationdate` = STR_TO_DATE(concat(SUBSTRING(title, 1, 7),'-01'),'%Y-%m-%d %h:%i%s')
WHERE
    (`updateid` IN (SELECT
            updateid
        FROM
            update_data
        WHERE
            title REGEXP ('^[0-9]{4}-[0-9]{2} *')));


UPDATE `xmppmaster`.`update_data`
SET
    `title_short` = TRIM(SUBSTR(SUBSTR(title, 9, CHAR_LENGTH(title)),
            1,
            LENGTH(SUBSTR(title, 9, CHAR_LENGTH(title))) - 11))
WHERE
    (`updateid` IN (SELECT
            updateid
        FROM
            update_data
        WHERE
            title REGEXP ('^[0-9]{4}-[0-9]{2} .*\(kB[0-9]{7}\)$')));
END$$

DELIMITER ;

DROP TABLE IF EXISTS `xmppmaster`.`up_offline_arch`;
CREATE TABLE IF NOT EXISTS `xmppmaster`.`up_offline_arch` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `os` VARCHAR(5) NOT NULL,
  `complete` VARCHAR(15) NULL,
  PRIMARY KEY (`id`));

INSERT INTO `xmppmaster`.`up_offline_arch` (`os`, `complete`) VALUES ('x86', 'x86-based');
INSERT INTO `xmppmaster`.`up_offline_arch` (`os`, `complete`) VALUES ('x64', 'x64-based');
INSERT INTO `xmppmaster`.`up_offline_arch` (`os`, `complete`) VALUES ('ARM64', 'ARM64-based');

DROP TABLE IF EXISTS `xmppmaster`.`up_offline_os`;
CREATE TABLE IF NOT EXISTS `xmppmaster`.`up_offline_os` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `os` VARCHAR(45) NULL,
  `version` VARCHAR(45) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `version_UNIQUE` (`version` ASC) );

INSERT INTO `xmppmaster`.`up_offline_os` (`os`) VALUES ('Windows 10');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '21H2');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '21H1');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '1607');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '1903');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '1809');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '1803');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '2004');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '1511');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '1507');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '1909');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '1709 ');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '20H2');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '1703');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', 'Next');

DROP TABLE IF EXISTS `xmppmaster`.`up_offline_machine`;
CREATE TABLE `up_offline_machine` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `machineid` int(10) NOT NULL,
  `updateid` varchar(38) NOT NULL,
  `kb` varchar(16) NOT NULL DEFAULT '""',
  `file` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_up_offline_machine_ind_idx` (`machineid`),
  CONSTRAINT `fk_up_offline_machine_ind` FOREIGN KEY (`machineid`) REFERENCES `machines` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- -------------------------------------------------------
-- cette procedure permet de genere les table
-- up_download_from_kb and
-- up_download_not_kb
-- -------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_table_download_from_kb`;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_table_download_from_kb`()
BEGIN
DROP TABLE IF EXISTS `xmppmaster`.`up_download_from_kb`;
create table up_download_from_kb as
(SELECT
    revisionid, updateid, payloadfiles, ckb, kb, dateupdate
FROM
    (SELECT revisionid,
        SUBSTRING_INDEX(SUBSTRING(payloadfiles, LENGTH(SUBSTRING_INDEX(payloadfiles, '-kb', 1)) + 4), '_', 1) AS ckb,
            SUBSTRING(payloadfiles, LENGTH(SUBSTRING_INDEX(payloadfiles, '-kb', 1)) + 4, 6) AS kb,
            updateid,
            payloadfiles,
            LEFT( SUBSTRING(payloadfiles, LENGTH(SUBSTRING_INDEX(payloadfiles, '/20', 1)) + 2),7) as dateupdate
    FROM
        xmppmaster.update_data
    WHERE
        payloadfiles LIKE 'http%' ) as ff
        where kb not like ''
);
DROP TABLE IF EXISTS `xmppmaster`.`up_download_not_kb`;
create table up_download_not_kb as
(SELECT
   revisionid,  updateid, payloadfiles, dateupdate
FROM
    (SELECT revisionid,
        SUBSTRING_INDEX(SUBSTRING(payloadfiles, LENGTH(SUBSTRING_INDEX(payloadfiles, '-kb', 1)) + 4), '_', 1) AS ckb,
            SUBSTRING(payloadfiles, LENGTH(SUBSTRING_INDEX(payloadfiles, '-kb', 1)) + 4, 6) AS kb,
            updateid,
            payloadfiles,
            LEFT( SUBSTRING(payloadfiles, LENGTH(SUBSTRING_INDEX(payloadfiles, '/20', 1)) + 2),7) as dateupdate
    FROM
        xmppmaster.update_data
    WHERE
        payloadfiles LIKE 'http%' ) as ff
        where kb like ''
);
END$$

DELIMITER ;
-- -------------------------------------------------------
-- cette procedure permet de chercher les mise a jour pour les software Malicious
-- parametre  Produit windows, archirexture, major du kb installer, minor du kb installer
-- exemple : call up_windows_malicious_software_tool("Windows 10", "x64", 5, 104);
-- -------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `up_windows_malicious_software_tool`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_windows_malicious_software_tool`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_windows_malicious_software_tool`(in PRODUCTtable varchar(80),
                                                                                 in ARCHItable varchar(20),
                                                                                 in major integer,
                                                                                 in minor integer)
proc_Exit:BEGIN
    DECLARE version varchar(10) DEFAULT NULL;
    DECLARE  titleval varchar(1024) DEFAULT NULL;
    DECLARE major_update INT DEFAULT 0;
    DECLARE minor_update INT DEFAULT 0;
    DECLARE position_str INT DEFAULT 0;
    -- product and architecture
    DECLARE produc_windows varchar(80) DEFAULT '%Windows 10%';
	DECLARE archi varchar(20) DEFAULT "%x64%";
-- initialise produc_windows Windows 10 si pas ""
if PRODUCTtable  !="" THEN
    SELECT
        CONCAT('%',PRODUCTtable,'%') INTO produc_windows;
END IF;
-- initialise archi x64 si pas ""
if ARCHItable !="" THEN
    SELECT
        CONCAT('%',ARCHItable,'%') INTO archi;
END IF;

SELECT
    title
FROM
    xmppmaster.update_data
WHERE
    title LIKE '%Windows Malicious Software Removal Tool%' and
    title LIKE archi
        AND product LIKE produc_windows
ORDER BY revisionid DESC
LIMIT 0 , 1 INTO titleval;

SELECT INSTR(titleval, '- v') INTO position_str;

SELECT SUBSTR(titleval, position_str + 3, 5) INTO version;
SELECT LEFT(version, 2) INTO major_update;
SELECT RIGHT(version, 3) INTO minor_update;

if major > major_update then
	SELECT
    *
FROM
    xmppmaster.update_data
WHERE
    title LIKE '%Windows Malicious Software Removal Tool%' and
    title LIKE archi
        AND product LIKE produc_windows
ORDER BY revisionid DESC
LIMIT 0 , 1;
	LEAVE proc_Exit;
end if;
if minor > minor_update then
	SELECT
    *
FROM
    xmppmaster.update_data
WHERE
    title LIKE '%Windows Malicious Software Removal Tool%'  and
    title LIKE archi
        AND product LIKE produc_windows
ORDER BY revisionid DESC
LIMIT 0 , 1;
    LEAVE proc_Exit;
end if;
END$$

DELIMITER ;
;


-- -------------------------------------------------------
-- cette procedure permet de faire le lien entre les update kb et les fichier a recuperer.
-- actuellement restreint a ("Windows 10", "x64", );
-- -------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packageid`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packageid`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packageid`()
BEGIN
	DECLARE is_done INTEGER DEFAULT 0;

	DECLARE c_title varchar(2040)  DEFAULT "";
	DECLARE c_udapeid varchar(2040)  DEFAULT "";
	DECLARE c_kb varchar(2040)  DEFAULT "";
	DECLARE c_revisionid varchar(2040)  DEFAULT "";


  DECLARE client_cursor CURSOR FOR
	  SELECT
		updateid, kb, revisionid, title
	FROM
		xmppmaster.update_data
	WHERE
		product like '%Windows 10%'
		AND title NOT LIKE '%ARM64%'
		AND title NOT LIKE '%X86%';

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

  OPEN client_cursor;

  get_list: LOOP
  FETCH client_cursor INTO c_udapeid, c_kb,c_revisionid, c_title;

  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
SELECT CONCAT('%', c_revisionid, '%') INTO @rev;
SELECT CONCAT('%', c_kb, '%') INTO @kb;

INSERT IGNORE INTO `xmppmaster`.`up_packages`
SELECT
    c_udapeid, c_kb,c_revisionid, c_title,
    updateid, payloadfiles
FROM
    xmppmaster.update_data
WHERE
    payloadfiles NOT IN ('')
        AND payloadfiles LIKE @kb
        AND supersededby LIKE @rev;

  END LOOP get_list;

  CLOSE client_cursor;
END$$

DELIMITER ;
;


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 72;

COMMIT;
