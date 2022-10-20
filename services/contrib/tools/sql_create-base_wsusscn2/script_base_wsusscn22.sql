-- MariaDB dump 10.19  Distrib 10.6.7-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: base_wsusscn2
-- ------------------------------------------------------
-- Server version	10.6.7-MariaDB-2ubuntu1.1
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `base_wsusscn2`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `base_wsusscn2` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;

USE `base_wsusscn2`;

--
-- Dumping routines for database 'base_wsusscn2'
--
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `create_update_result`( in FILTERtable varchar(2048), in KB_LIST varchar(2048), in createtbleresult int)
BEGIN
DECLARE _next TEXT DEFAULT NULL;
DECLARE _nextlen INT DEFAULT NULL;
DECLARE _value TEXT DEFAULT NULL;
DECLARE _list MEDIUMTEXT;

DECLARE kb_next TEXT DEFAULT NULL;
DECLARE kb_nextlen INT DEFAULT NULL;
DECLARE kb_value TEXT DEFAULT NULL;
DECLARE kb_updateid  varchar(50) DEFAULT NULL;
-- clean table
drop table if EXISTS tmp_kb_updateid;
drop table IF EXISTS tmp_t1;
drop table IF EXISTS tmp_my_mise_a_jour;
drop table IF EXISTS tmp_result_procedure;
CREATE TABLE IF NOT EXISTS `tmp_kb_updateid` (
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
  -- select updateid into kb_updateid from base_wsusscn2.update_data where kb = kb_value;
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
CREATE TABLE IF NOT EXISTS tmp_my_mise_a_jour AS (SELECT * FROM
    base_wsusscn2.update_data
WHERE
    title LIKE FILTERtable and title not like "%Dynamic Cumulative Update%");

SELECT
    GROUP_CONCAT(DISTINCT supersedes
        ORDER BY supersedes ASC
        SEPARATOR ',')
INTO _list FROM
    base_wsusscn2.tmp_my_mise_a_jour;

CREATE TABLE IF NOT EXISTS `tmp_t1` (
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
DELETE FROM `base_wsusscn2`.`tmp_t1`
WHERE
    (`c1` = '');

-- injection les update_id deja installer dans tmp_t1
 INSERT IGNORE INTO tmp_t1  select updateid from base_wsusscn2.update_data where kb in (select c1 from tmp_kb_updateid);

CREATE TABLE tmp_result_procedure AS (SELECT * FROM
    tmp_my_mise_a_jour
WHERE
    updateid NOT IN (SELECT
            c1
        FROM
            tmp_t1));

-- on supprime les updateid qui sont dans select c1 from tmp_kb_updateid
DELETE FROM tmp_result_procedure WHERE updateid IN (select c1 from tmp_kb_updateid);
drop table IF EXISTS tmp_t1;
drop table IF EXISTS tmp_my_mise_a_jour;
drop table IF EXISTS tmp_kb_updateid;
SELECT
    *
FROM
    tmp_result_procedure;
	if    createtbleresult = 0 then
		drop table IF EXISTS tmp_result_procedure;
	END IF;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `update_datetime`()
BEGIN
  UPDATE `base_wsusscn2`.`update_data`
SET
    `creationdate` = STR_TO_DATE(concat(SUBSTRING(title, 1, 7),'-01'),'%Y-%m-%d %h:%i%s')
WHERE
    (`updateid` IN (SELECT
            updateid
        FROM
            update_data
        WHERE
            title REGEXP ('^[0-9]{4}-[0-9]{2} *')));


UPDATE `base_wsusscn2`.`update_data`
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
            title REGEXP ('^[0-9]{4}-[0-9]{2} .*\\(kB[0-9]{7}\\)$')));
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb3 */ ;
/*!50003 SET character_set_results = utf8mb3 */ ;
/*!50003 SET collation_connection  = utf8mb3_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `update_updateclassification`()
BEGIN
  DECLARE is_done INTEGER DEFAULT 0;
  
  DECLARE c_title varchar(2040)  DEFAULT "";
  DECLARE c_udateid varchar(2040)  DEFAULT "";
  
  DECLARE client_cursor CURSOR FOR
   select title, updateid FROM base_wsusscn2.update_data where updateid in
   (SELECT distinct updateclassification FROM base_wsusscn2.update_data where updateclassification not in (''));

  
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;
    
  OPEN client_cursor;
  
  get_list: LOOP
  FETCH client_cursor INTO c_title,c_udateid;

  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;

  
  UPDATE `base_wsusscn2`.`update_data` SET `updateclassification` = c_title WHERE (`updateclassification` = c_udateid);

  END LOOP get_list;
  
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `update_updatecompagny`()
BEGIN
  DECLARE is_done INTEGER DEFAULT 0;
  -- déclarer la variable qui va contenir les noms des clients récupérer par le curseur .
  DECLARE c_title varchar(2040)  DEFAULT "";
  DECLARE c_udateid varchar(2040)  DEFAULT "";
  -- déclarer le curseur
  DECLARE client_cursor CURSOR FOR
   select title, updateid FROM base_wsusscn2.update_data where updateid in
   (SELECT distinct compagny FROM base_wsusscn2.update_data where compagny not in (''));

  -- déclarer le gestionnaire NOT FOUND
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;
    -- ouvrir le curseur
  OPEN client_cursor;
  -- parcourir la liste des noms des clients et concatèner tous les noms où chaque nom est séparé par un point-virgule(;)
  get_list: LOOP
  FETCH client_cursor INTO c_title,c_udateid;

  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;

  -- traitement
  UPDATE `base_wsusscn2`.`update_data` SET `compagny` = c_title WHERE (`compagny` = c_udateid);

  END LOOP get_list;
  -- fermer le curseur
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `update_updateproductfamily`()
BEGIN
  DECLARE is_done INTEGER DEFAULT 0;
  -- déclarer la variable qui va contenir les noms des clients récupérer par le curseur .
  DECLARE c_title varchar(2040)  DEFAULT "";
  DECLARE c_udateid varchar(2040)  DEFAULT "";
  -- déclarer le curseur
  DECLARE client_cursor CURSOR FOR
   select title, updateid FROM base_wsusscn2.update_data where updateid in
   (SELECT distinct productfamily FROM base_wsusscn2.update_data where productfamily not in (''));

  -- déclarer le gestionnaire NOT FOUND
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

  -- ouvrir le curseur
  OPEN client_cursor;
  -- parcourir la liste des noms des clients et concatèner tous les noms où chaque nom est séparé par un point-virgule(;)
  get_list: LOOP
  FETCH client_cursor INTO c_title,c_udateid;
   IF is_done = 1 THEN
  LEAVE get_list;
  END IF;

  -- traitement
  UPDATE `base_wsusscn2`.`update_data` SET `productfamily` = c_title WHERE (`productfamily` = c_udateid);

  END LOOP get_list;
  -- fermer le curseur
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `update_update_product`()
BEGIN
  DECLARE is_done INTEGER DEFAULT 0;
  -- déclarer la variable qui va contenir les noms des clients récupérer par le curseur .
  DECLARE c_updateid varchar(2040)  DEFAULT "";
  DECLARE c_product varchar(2040)  DEFAULT "";
  DECLARE productelt varchar(2040)  DEFAULT "";
  DECLARE c_title_select varchar(2040)  DEFAULT "";
  DECLARE c_title_result varchar(2040)  DEFAULT "";
  declare c_size int  DEFAULT 0;
  -- déclarer le curseur
  DECLARE client_cursor CURSOR FOR
   select updateid, product, length(product) FROM base_wsusscn2.update_data where product not like '';
  -- déclarer le gestionnaire NOT FOUND
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;
  -- ouvrir le curseur
  OPEN client_cursor;
  -- parcourir la liste des noms des clients et concatèner tous les noms où chaque nom est séparé par un point-virgule(;)
  get_list: LOOP
  FETCH client_cursor INTO c_updateid, c_product, c_size;
   IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
    select "" into  c_title_result;
    if (c_size >= 36) then
        WHILE (SELECT SUBSTR(c_product, 9 ,1 ) = "-") do
			SELECT SUBSTRING_INDEX(c_product , ',', 1 ) into productelt;
            SELECT SUBSTR(c_product, LENGTH(productelt)+2 ) into c_product;
			SELECT title FROM base_wsusscn2.update_data WHERE updateid LIKE productelt INTO c_title_select;
            SELECT concat(c_title_result," ; ",c_title_select) into c_title_result;
	    END WHILE;
        if (c_title_result != "") then
		    UPDATE `base_wsusscn2`.`update_data` SET `product` = c_title_result WHERE (`updateid` = c_updateid);
		end if;
    end if;
  -- traitement
  END LOOP get_list;
  -- fermer le curseur
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `update_update_remplaces`()
BEGIN
  DECLARE is_done INTEGER DEFAULT 0;
  -- déclarer la variable qui va contenir les noms des clients récupérer par le curseur .
  DECLARE c_updateid varchar(2048)  DEFAULT "";
  DECLARE c_supersedes  varchar(9096)  DEFAULT "";
  DECLARE supersedeselt varchar(2048)  DEFAULT "";
   declare counpp int default 0;
  -- déclarer le curseur
  DECLARE client_cursor CURSOR FOR
   select updateid, supersedes FROM base_wsusscn2.update_data where supersedes not like '' limit 5;
  -- déclarer le gestionnaire NOT FOUND
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;
 drop table IF EXISTS `data_supersedes`;
 CREATE TABLE `data_supersedes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `updateid` varchar(37) NOT NULL,
  `title` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniid` (`updateid`,`title`) USING HASH
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
  -- ouvrir le curseur
  -- set counpp = 0;
  OPEN client_cursor;
  -- parcourir la liste des noms des clients et concatèner tous les noms où chaque nom est séparé par un point-virgule(;)
  get_list: LOOP
	  FETCH client_cursor INTO c_updateid, c_supersedes;
	 -- select LENGTH(c_supersedes);
	  IF is_done = 1 THEN
		LEAVE get_list;
	  END IF;
		  if (LENGTH(c_supersedes) >= 36) then
			select c_updateid, c_supersedes;
		  call _add_new_remplace(c_updateid, c_supersedes);
		 end if;
	  -- traitement
  END LOOP get_list;
  -- fermer le curseur
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_create_product_tables`()
BEGIN
	-- cette procedure stockee genere les tables pour different produit
    -- list des procedure a appeler pour generer les tables updates
	call up_init_packages_Win10_X64_1903();
	call up_init_packages_Win10_X64_21H2();
	call up_init_packages_Win10_X64_21H1();
	call up_init_packages_office_2003_64bit();
	call up_init_packages_office_2007_64bit();
	call up_init_packages_office_2010_64bit();
	call up_init_packages_office_2013_64bit();
	call up_init_packages_office_2016_64bit();
	call up_init_packages_Vstudio_2005();
	call up_init_packages_Vstudio_2008();
	call up_init_packages_Vstudio_2010();
	call up_init_packages_Vstudio_2012();
	call up_init_packages_Vstudio_2013();
	call up_init_packages_Vstudio_2015();
	call up_init_packages_Vstudio_2017();
	call up_init_packages_Vstudio_2019();
	call up_init_packages_Vstudio_2022();
	call up_init_packages_Win11_X64();
	call up_init_packages_Win_Malicious_X64();
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_office_2003_64bit`()
BEGIN
	DECLARE is_done INTEGER DEFAULT 0;
	DECLARE c_title varchar(2040)  DEFAULT "";
    DECLARE c_description varchar(2040)DEFAULT "";
	DECLARE c_udapeid varchar(2040)  DEFAULT "";
	DECLARE c_kb varchar(2040)  DEFAULT "";
	DECLARE c_revisionid varchar(2040)  DEFAULT "";
  DECLARE client_cursor CURSOR FOR
	  SELECT 
		updateid, kb, revisionid, title, description
	FROM
		base_wsusscn2.update_data
	WHERE
        product LIKE '%Office 2003%'
		AND title NOT LIKE '%ARM64%'
		AND title NOT LIKE '%32-Bit%' 
        AND title NOT LIKE '%Server%' 
        AND title NOT LIKE '%X86%' 
        AND title not like '%Dynamic%';
        
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_office_2003_64bit`;
CREATE TABLE `up_packages_office_2003_64bit` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  `supersededby` varchar(2048),
  `creationdate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  `title_short` varchar(500),
  PRIMARY KEY (`updateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
  OPEN client_cursor;

  get_list: LOOP
  FETCH client_cursor INTO c_udapeid, c_kb,c_revisionid, c_title, c_description;
 
  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
SELECT CONCAT('%', c_revisionid, '%') INTO @rev;
SELECT CONCAT('%', c_kb, '%') INTO @kb;

INSERT IGNORE INTO `base_wsusscn2`.`up_packages_office_2003_64bit`
SELECT 
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    base_wsusscn2.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;  
  END LOOP get_list;
  
        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_office_2007_64bit`()
BEGIN
	DECLARE is_done INTEGER DEFAULT 0;
	DECLARE c_title varchar(2040)  DEFAULT "";
    DECLARE c_description varchar(2040)DEFAULT "";
	DECLARE c_udapeid varchar(2040)  DEFAULT "";
	DECLARE c_kb varchar(2040)  DEFAULT "";
	DECLARE c_revisionid varchar(2040)  DEFAULT "";
  DECLARE client_cursor CURSOR FOR
	  SELECT 
		updateid, kb, revisionid, title, description
	FROM
		base_wsusscn2.update_data
	WHERE
        product LIKE '%Office 2007%'
		AND title NOT LIKE '%ARM64%'
		AND title NOT LIKE '%32-Bit%' 
        AND title NOT LIKE '%Server%' 
        AND title NOT LIKE '%X86%' 
        AND title not like '%Dynamic%';
        
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_office_2007_64bit`;
CREATE TABLE `up_packages_office_2007_64bit` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  `supersededby` varchar(2048),
  `creationdate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  `title_short` varchar(500),
  PRIMARY KEY (`updateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
  OPEN client_cursor;

  get_list: LOOP
  FETCH client_cursor INTO c_udapeid, c_kb,c_revisionid, c_title, c_description;
 
  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
SELECT CONCAT('%', c_revisionid, '%') INTO @rev;
SELECT CONCAT('%', c_kb, '%') INTO @kb;

INSERT IGNORE INTO `base_wsusscn2`.`up_packages_office_2007_64bit`
SELECT 
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    base_wsusscn2.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;  
  END LOOP get_list;
  
        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_office_2010_64bit`()
BEGIN
	DECLARE is_done INTEGER DEFAULT 0;
	DECLARE c_title varchar(2040)  DEFAULT "";
    DECLARE c_description varchar(2040)DEFAULT "";
	DECLARE c_udapeid varchar(2040)  DEFAULT "";
	DECLARE c_kb varchar(2040)  DEFAULT "";
	DECLARE c_revisionid varchar(2040)  DEFAULT "";
  DECLARE client_cursor CURSOR FOR
	  SELECT 
		updateid, kb, revisionid, title, description
	FROM
		base_wsusscn2.update_data
	WHERE
        product LIKE '%Office 2010%'
		AND title NOT LIKE '%ARM64%'
		AND title NOT LIKE '%32-Bit%' 
        AND title NOT LIKE '%Server%' 
        AND title NOT LIKE '%X86%' 
        AND title not like '%Dynamic%';
        
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_office_2010_64bit`;
CREATE TABLE `up_packages_office_2010_64bit` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  `supersededby` varchar(2048),
  `creationdate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  `title_short` varchar(500),
  PRIMARY KEY (`updateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
  OPEN client_cursor;

  get_list: LOOP
  FETCH client_cursor INTO c_udapeid, c_kb,c_revisionid, c_title, c_description;
 
  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
SELECT CONCAT('%', c_revisionid, '%') INTO @rev;
SELECT CONCAT('%', c_kb, '%') INTO @kb;

INSERT IGNORE INTO `base_wsusscn2`.`up_packages_office_2010_64bit`
SELECT 
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    base_wsusscn2.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;  
  END LOOP get_list;
  
        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_office_2013_64bit`()
BEGIN
	DECLARE is_done INTEGER DEFAULT 0;
	DECLARE c_title varchar(2040)  DEFAULT "";
    DECLARE c_description varchar(2040)DEFAULT "";
	DECLARE c_udapeid varchar(2040)  DEFAULT "";
	DECLARE c_kb varchar(2040)  DEFAULT "";
	DECLARE c_revisionid varchar(2040)  DEFAULT "";
  DECLARE client_cursor CURSOR FOR
	  SELECT 
		updateid, kb, revisionid, title, description
	FROM
		base_wsusscn2.update_data
	WHERE
        product LIKE '%Office 2013%'
		AND title NOT LIKE '%ARM64%'
		AND title NOT LIKE '%32-Bit%' 
        AND title NOT LIKE '%Server%' 
        AND title NOT LIKE '%X86%' 
        AND title not like '%Dynamic%';
        
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_office_2013_64bit`;
CREATE TABLE `up_packages_office_2013_64bit` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  `supersededby` varchar(2048),
  `creationdate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  `title_short` varchar(500),
  PRIMARY KEY (`updateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
  OPEN client_cursor;

  get_list: LOOP
  FETCH client_cursor INTO c_udapeid, c_kb,c_revisionid, c_title, c_description;
 
  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
SELECT CONCAT('%', c_revisionid, '%') INTO @rev;
SELECT CONCAT('%', c_kb, '%') INTO @kb;

INSERT IGNORE INTO `base_wsusscn2`.`up_packages_office_2013_64bit`
SELECT 
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    base_wsusscn2.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;  
  END LOOP get_list;
  
        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_office_2016_64bit`()
BEGIN
	DECLARE is_done INTEGER DEFAULT 0;
	DECLARE c_title varchar(2040)  DEFAULT "";
    DECLARE c_description varchar(2040)DEFAULT "";
	DECLARE c_udapeid varchar(2040)  DEFAULT "";
	DECLARE c_kb varchar(2040)  DEFAULT "";
	DECLARE c_revisionid varchar(2040)  DEFAULT "";
  DECLARE client_cursor CURSOR FOR
	  SELECT 
		updateid, kb, revisionid, title, description
	FROM
		base_wsusscn2.update_data
	WHERE
        product LIKE '%Office 2016%'
		AND title NOT LIKE '%ARM64%'
		AND title NOT LIKE '%32-Bit%' 
        AND title NOT LIKE '%Server%' 
        AND title NOT LIKE '%X86%' 
        AND title not like '%Dynamic%';
        
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_office_2016_64bit`;
CREATE TABLE `up_packages_office_2016_64bit` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  `supersededby` varchar(2048),
  `creationdate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  `title_short` varchar(500),
  PRIMARY KEY (`updateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
  OPEN client_cursor;

  get_list: LOOP
  FETCH client_cursor INTO c_udapeid, c_kb,c_revisionid, c_title, c_description;
 
  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
SELECT CONCAT('%', c_revisionid, '%') INTO @rev;
SELECT CONCAT('%', c_kb, '%') INTO @kb;

INSERT IGNORE INTO `base_wsusscn2`.`up_packages_office_2016_64bit`
SELECT 
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    base_wsusscn2.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;  
  END LOOP get_list;
  
        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_Vstudio_2005`()
BEGIN
	DECLARE is_done INTEGER DEFAULT 0;
	DECLARE c_title varchar(2040)  DEFAULT "";
    DECLARE c_description varchar(2040)DEFAULT "";
	DECLARE c_udapeid varchar(2040)  DEFAULT "";
	DECLARE c_kb varchar(2040)  DEFAULT "";
	DECLARE c_revisionid varchar(2040)  DEFAULT "";
  DECLARE client_cursor CURSOR FOR
	  SELECT 
		updateid, kb, revisionid, title, description
	FROM
		base_wsusscn2.update_data
	WHERE
        product LIKE '%Visual Studio 2005%';
        
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Vstudio_2005`;
CREATE TABLE `up_packages_Vstudio_2005` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  `supersededby` varchar(2048),
  `creationdate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  `title_short` varchar(500),
  PRIMARY KEY (`updateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
  OPEN client_cursor;

  get_list: LOOP
  FETCH client_cursor INTO c_udapeid, c_kb,c_revisionid, c_title, c_description;
 
  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
SELECT CONCAT('%', c_revisionid, '%') INTO @rev;
SELECT CONCAT('%', c_kb, '%') INTO @kb;

INSERT IGNORE INTO `base_wsusscn2`.`up_packages_Vstudio_2005`
SELECT 
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    base_wsusscn2.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;  
  END LOOP get_list;
  
        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_Vstudio_2008`()
BEGIN
	DECLARE is_done INTEGER DEFAULT 0;
	DECLARE c_title varchar(2040)  DEFAULT "";
    DECLARE c_description varchar(2040)DEFAULT "";
	DECLARE c_udapeid varchar(2040)  DEFAULT "";
	DECLARE c_kb varchar(2040)  DEFAULT "";
	DECLARE c_revisionid varchar(2040)  DEFAULT "";
  DECLARE client_cursor CURSOR FOR
	  SELECT 
		updateid, kb, revisionid, title, description
	FROM
		base_wsusscn2.update_data
	WHERE
        product LIKE '%Visual Studio 2008%';
        
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Vstudio_2008`;
CREATE TABLE `up_packages_Vstudio_2008` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  `supersededby` varchar(2048),
  `creationdate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  `title_short` varchar(500),
  PRIMARY KEY (`updateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
  OPEN client_cursor;

  get_list: LOOP
  FETCH client_cursor INTO c_udapeid, c_kb,c_revisionid, c_title, c_description;
 
  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
SELECT CONCAT('%', c_revisionid, '%') INTO @rev;
SELECT CONCAT('%', c_kb, '%') INTO @kb;

INSERT IGNORE INTO `base_wsusscn2`.`up_packages_Vstudio_2008`
SELECT 
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    base_wsusscn2.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;  
  END LOOP get_list;
  
        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_Vstudio_2010`()
BEGIN
	DECLARE is_done INTEGER DEFAULT 0;
	DECLARE c_title varchar(2040)  DEFAULT "";
    DECLARE c_description varchar(2040)DEFAULT "";
	DECLARE c_udapeid varchar(2040)  DEFAULT "";
	DECLARE c_kb varchar(2040)  DEFAULT "";
	DECLARE c_revisionid varchar(2040)  DEFAULT "";
  DECLARE client_cursor CURSOR FOR
	  SELECT 
		updateid, kb, revisionid, title, description
	FROM
		base_wsusscn2.update_data
	WHERE
        product LIKE '%Visual Studio 2010%';
        
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Vstudio_2010`;
CREATE TABLE `up_packages_Vstudio_2010` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  `supersededby` varchar(2048),
  `creationdate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  `title_short` varchar(500),
  PRIMARY KEY (`updateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
  OPEN client_cursor;

  get_list: LOOP
  FETCH client_cursor INTO c_udapeid, c_kb,c_revisionid, c_title, c_description;
 
  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
SELECT CONCAT('%', c_revisionid, '%') INTO @rev;
SELECT CONCAT('%', c_kb, '%') INTO @kb;

INSERT IGNORE INTO `base_wsusscn2`.`up_packages_Vstudio_2010`
SELECT 
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    base_wsusscn2.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;  
  END LOOP get_list;
  
        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_Vstudio_2012`()
BEGIN
	DECLARE is_done INTEGER DEFAULT 0;
	DECLARE c_title varchar(2040)  DEFAULT "";
    DECLARE c_description varchar(2040)DEFAULT "";
	DECLARE c_udapeid varchar(2040)  DEFAULT "";
	DECLARE c_kb varchar(2040)  DEFAULT "";
	DECLARE c_revisionid varchar(2040)  DEFAULT "";
  DECLARE client_cursor CURSOR FOR
	  SELECT 
		updateid, kb, revisionid, title, description
	FROM
		base_wsusscn2.update_data
	WHERE
        product LIKE '%Visual Studio 2012%';
        
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Vstudio_2012`;
CREATE TABLE `up_packages_Vstudio_2012` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  `supersededby` varchar(2048),
  `creationdate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  `title_short` varchar(500),
  PRIMARY KEY (`updateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
  OPEN client_cursor;

  get_list: LOOP
  FETCH client_cursor INTO c_udapeid, c_kb,c_revisionid, c_title, c_description;
 
  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
SELECT CONCAT('%', c_revisionid, '%') INTO @rev;
SELECT CONCAT('%', c_kb, '%') INTO @kb;

INSERT IGNORE INTO `base_wsusscn2`.`up_packages_Vstudio_2012`
SELECT 
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    base_wsusscn2.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;  
  END LOOP get_list;
  
        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_Vstudio_2013`()
BEGIN
	DECLARE is_done INTEGER DEFAULT 0;
	DECLARE c_title varchar(2040)  DEFAULT "";
    DECLARE c_description varchar(2040)DEFAULT "";
	DECLARE c_udapeid varchar(2040)  DEFAULT "";
	DECLARE c_kb varchar(2040)  DEFAULT "";
	DECLARE c_revisionid varchar(2040)  DEFAULT "";
  DECLARE client_cursor CURSOR FOR
	  SELECT 
		updateid, kb, revisionid, title, description
	FROM
		base_wsusscn2.update_data
	WHERE
        product LIKE '%Visual Studio 2013%';
        
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Vstudio_2013`;
CREATE TABLE `up_packages_Vstudio_2013` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  `supersededby` varchar(2048),
  `creationdate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  `title_short` varchar(500),
  PRIMARY KEY (`updateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
  OPEN client_cursor;

  get_list: LOOP
  FETCH client_cursor INTO c_udapeid, c_kb,c_revisionid, c_title, c_description;
 
  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
SELECT CONCAT('%', c_revisionid, '%') INTO @rev;
SELECT CONCAT('%', c_kb, '%') INTO @kb;

INSERT IGNORE INTO `base_wsusscn2`.`up_packages_Vstudio_2013`
SELECT 
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    base_wsusscn2.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;  
  END LOOP get_list;
  
        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_Vstudio_2015`()
BEGIN
	DECLARE is_done INTEGER DEFAULT 0;
	DECLARE c_title varchar(2040)  DEFAULT "";
    DECLARE c_description varchar(2040)DEFAULT "";
	DECLARE c_udapeid varchar(2040)  DEFAULT "";
	DECLARE c_kb varchar(2040)  DEFAULT "";
	DECLARE c_revisionid varchar(2040)  DEFAULT "";
  DECLARE client_cursor CURSOR FOR
	  SELECT 
		updateid, kb, revisionid, title, description
	FROM
		base_wsusscn2.update_data
	WHERE
        product LIKE '%Visual Studio 2015%';
        
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Vstudio_2015`;
CREATE TABLE `up_packages_Vstudio_2015` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  `supersededby` varchar(2048),
  `creationdate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  `title_short` varchar(500),
  PRIMARY KEY (`updateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
  OPEN client_cursor;

  get_list: LOOP
  FETCH client_cursor INTO c_udapeid, c_kb,c_revisionid, c_title, c_description;
 
  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
SELECT CONCAT('%', c_revisionid, '%') INTO @rev;
SELECT CONCAT('%', c_kb, '%') INTO @kb;

INSERT IGNORE INTO `base_wsusscn2`.`up_packages_Vstudio_2015`
SELECT 
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    base_wsusscn2.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;  
  END LOOP get_list;
  
        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_Vstudio_2017`()
BEGIN
	DECLARE is_done INTEGER DEFAULT 0;
	DECLARE c_title varchar(2040)  DEFAULT "";
    DECLARE c_description varchar(2040)DEFAULT "";
	DECLARE c_udapeid varchar(2040)  DEFAULT "";
	DECLARE c_kb varchar(2040)  DEFAULT "";
	DECLARE c_revisionid varchar(2040)  DEFAULT "";
  DECLARE client_cursor CURSOR FOR
	  SELECT 
		updateid, kb, revisionid, title, description
	FROM
		base_wsusscn2.update_data
	WHERE
        product LIKE '%Visual Studio 2017%';
        
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Vstudio_2017`;
CREATE TABLE `up_packages_Vstudio_2017` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  `supersededby` varchar(2048),
  `creationdate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  `title_short` varchar(500),
  PRIMARY KEY (`updateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
  OPEN client_cursor;

  get_list: LOOP
  FETCH client_cursor INTO c_udapeid, c_kb,c_revisionid, c_title, c_description;
 
  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
SELECT CONCAT('%', c_revisionid, '%') INTO @rev;
SELECT CONCAT('%', c_kb, '%') INTO @kb;

INSERT IGNORE INTO `base_wsusscn2`.`up_packages_Vstudio_2017`
SELECT 
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    base_wsusscn2.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;  
  END LOOP get_list;
  
        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_Vstudio_2019`()
BEGIN
	DECLARE is_done INTEGER DEFAULT 0;
	DECLARE c_title varchar(2040)  DEFAULT "";
    DECLARE c_description varchar(2040)DEFAULT "";
	DECLARE c_udapeid varchar(2040)  DEFAULT "";
	DECLARE c_kb varchar(2040)  DEFAULT "";
	DECLARE c_revisionid varchar(2040)  DEFAULT "";
  DECLARE client_cursor CURSOR FOR
	  SELECT 
		updateid, kb, revisionid, title, description
	FROM
		base_wsusscn2.update_data
	WHERE
        product LIKE '%Visual Studio 2019%';
        
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Vstudio_2019`;
CREATE TABLE `up_packages_Vstudio_2019` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  `supersededby` varchar(2048),
  `creationdate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  `title_short` varchar(500),
  PRIMARY KEY (`updateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
  OPEN client_cursor;

  get_list: LOOP
  FETCH client_cursor INTO c_udapeid, c_kb,c_revisionid, c_title, c_description;
 
  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
SELECT CONCAT('%', c_revisionid, '%') INTO @rev;
SELECT CONCAT('%', c_kb, '%') INTO @kb;

INSERT IGNORE INTO `base_wsusscn2`.`up_packages_Vstudio_2019`
SELECT 
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    base_wsusscn2.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;  
  END LOOP get_list;
  
        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_Vstudio_2022`()
BEGIN
	DECLARE is_done INTEGER DEFAULT 0;
	DECLARE c_title varchar(2040)  DEFAULT "";
    DECLARE c_description varchar(2040)DEFAULT "";
	DECLARE c_udapeid varchar(2040)  DEFAULT "";
	DECLARE c_kb varchar(2040)  DEFAULT "";
	DECLARE c_revisionid varchar(2040)  DEFAULT "";
  DECLARE client_cursor CURSOR FOR
	  SELECT 
		updateid, kb, revisionid, title, description
	FROM
		base_wsusscn2.update_data
	WHERE
        product LIKE '%Visual Studio 2022%';
        
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Vstudio_2022`;
CREATE TABLE `up_packages_Vstudio_2022` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  `supersededby` varchar(2048),
  `creationdate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  `title_short` varchar(500),
  PRIMARY KEY (`updateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
  OPEN client_cursor;

  get_list: LOOP
  FETCH client_cursor INTO c_udapeid, c_kb,c_revisionid, c_title, c_description;
 
  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
SELECT CONCAT('%', c_revisionid, '%') INTO @rev;
SELECT CONCAT('%', c_kb, '%') INTO @kb;

INSERT IGNORE INTO `base_wsusscn2`.`up_packages_Vstudio_2022`
SELECT 
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    base_wsusscn2.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;  
  END LOOP get_list;
  
        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_Win10_X64_1903`()
BEGIN
	DECLARE is_done INTEGER DEFAULT 0;
	DECLARE c_title varchar(2040)  DEFAULT "";
    DECLARE c_description varchar(2040)DEFAULT "";
	DECLARE c_udapeid varchar(2040)  DEFAULT "";
	DECLARE c_kb varchar(2040)  DEFAULT "";
	DECLARE c_revisionid varchar(2040)  DEFAULT "";
  DECLARE client_cursor CURSOR FOR
	  SELECT 
		updateid, kb, revisionid, title, description
	FROM
		base_wsusscn2.update_data
	WHERE
    title LIKE '%Version 1903%' 
    AND product LIKE '%Windows 10, version 1903 and later%'
		AND title NOT LIKE '%ARM64%'
		AND title NOT LIKE '%X86%' 
        AND title not like '%Dynamic%';
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;
drop tables if exists `up_packages_Win10_X64_1903`;
CREATE TABLE `up_packages_Win10_X64_1903` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  `supersededby` varchar(2048),
  `creationdate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  `title_short` varchar(500),
  PRIMARY KEY (`updateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
  OPEN client_cursor;

  get_list: LOOP
  FETCH client_cursor INTO c_udapeid, c_kb,c_revisionid, c_title, c_description;
 
  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
SELECT CONCAT('%', c_revisionid, '%') INTO @rev;
SELECT CONCAT('%', c_kb, '%') INTO @kb;
INSERT IGNORE INTO `base_wsusscn2`.`up_packages_Win10_X64_1903`
SELECT 
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    base_wsusscn2.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev; 
--        AND payloadfiles LIKE @kb
  END LOOP get_list;
  
        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_Win10_X64_21H1`()
BEGIN
	DECLARE is_done INTEGER DEFAULT 0;
	DECLARE c_title varchar(2040)  DEFAULT "";
    DECLARE c_description varchar(2040)DEFAULT "";
	DECLARE c_udapeid varchar(2040)  DEFAULT "";
	DECLARE c_kb varchar(2040)  DEFAULT "";
	DECLARE c_revisionid varchar(2040)  DEFAULT "";
  DECLARE client_cursor CURSOR FOR
	  SELECT 
		updateid, kb, revisionid, title, description
	FROM
		base_wsusscn2.update_data
	WHERE
    title LIKE '%21H1%' 
    AND (product LIKE '%Windows 10, version 1903 and later%'
        OR product LIKE '%Windows 10 and later GDR-DU%')
		AND title NOT LIKE '%ARM64%'
		AND title NOT LIKE '%X86%' 
        AND title not like '%Dynamic%';
  
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Win10_X64_21H1`;
CREATE TABLE `up_packages_Win10_X64_21H1` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  `supersededby` varchar(2048),
  `creationdate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  `title_short` varchar(500),
  PRIMARY KEY (`updateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
  OPEN client_cursor;

  get_list: LOOP
  FETCH client_cursor INTO c_udapeid, c_kb,c_revisionid, c_title, c_description;
 
  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
SELECT CONCAT('%', c_revisionid, '%') INTO @rev;
SELECT CONCAT('%', c_kb, '%') INTO @kb;

INSERT IGNORE INTO `base_wsusscn2`.`up_packages_Win10_X64_21H1`
SELECT 
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    base_wsusscn2.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;  
  END LOOP get_list;
  
        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_Win10_X64_21H2`()
BEGIN
	DECLARE is_done INTEGER DEFAULT 0;
	DECLARE c_title varchar(2040)  DEFAULT "";
    DECLARE c_description varchar(2040)DEFAULT "";
	DECLARE c_udapeid varchar(2040)  DEFAULT "";
	DECLARE c_kb varchar(2040)  DEFAULT "";
	DECLARE c_revisionid varchar(2040)  DEFAULT "";
  DECLARE client_cursor CURSOR FOR
	  SELECT 
		updateid, kb, revisionid, title, description
	FROM
		base_wsusscn2.update_data
	WHERE
    title LIKE '%21H2%' 
    AND (product LIKE '%Windows 10, version 1903 and later%'
        OR product LIKE '%Windows 10 and later GDR-DU%')
		AND title NOT LIKE '%ARM64%'
		AND title NOT LIKE '%X86%' 
        AND title not like '%Dynamic%';
  
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Win10_X64_21H2`;
CREATE TABLE `up_packages_Win10_X64_21H2` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  `supersededby` varchar(2048),
  `creationdate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  `title_short` varchar(500),
  PRIMARY KEY (`updateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
  OPEN client_cursor;

  get_list: LOOP
  FETCH client_cursor INTO c_udapeid, c_kb,c_revisionid, c_title, c_description;
 
  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
SELECT CONCAT('%', c_revisionid, '%') INTO @rev;
SELECT CONCAT('%', c_kb, '%') INTO @kb;

-- INSERT IGNORE INTO `base_wsusscn2`.`up_packages_Win10_X64`
-- SELECT 
--    c_udapeid, c_kb,c_revisionid, c_title, c_description,
--    updateid, payloadfiles
-- FROM
--    base_wsusscn2.update_data
-- WHERE
--    payloadfiles NOT IN ('')
--        AND payloadfiles LIKE @kb
--        AND supersededby LIKE @rev;
INSERT IGNORE INTO `base_wsusscn2`.`up_packages_Win10_X64_21H2`
SELECT 
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    base_wsusscn2.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;  
  END LOOP get_list;
  
        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_Win11_X64`()
BEGIN
	DECLARE is_done INTEGER DEFAULT 0;
	DECLARE c_title varchar(2040)  DEFAULT "";
    DECLARE c_description varchar(2040)DEFAULT "";
	DECLARE c_udapeid varchar(2040)  DEFAULT "";
	DECLARE c_kb varchar(2040)  DEFAULT "";
	DECLARE c_revisionid varchar(2040)  DEFAULT "";
  DECLARE client_cursor CURSOR FOR
	  SELECT 
		updateid, kb, revisionid, title, description
	FROM
		base_wsusscn2.update_data
	WHERE
    product LIKE '%Windows 11%'
		AND title NOT LIKE '%ARM64%'
		AND title NOT LIKE '%X86%' 
        AND title not like '%Dynamic%';
  
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Win11_X64`;
CREATE TABLE `up_packages_Win11_X64` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  `supersededby` varchar(2048),
  `creationdate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  `title_short` varchar(500),
  PRIMARY KEY (`updateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
  OPEN client_cursor;

  get_list: LOOP
  FETCH client_cursor INTO c_udapeid, c_kb,c_revisionid, c_title, c_description;
 
  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
SELECT CONCAT('%', c_revisionid, '%') INTO @rev;
SELECT CONCAT('%', c_kb, '%') INTO @kb;


INSERT IGNORE INTO `base_wsusscn2`.`up_packages_Win11_X64`
SELECT 
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    base_wsusscn2.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;  
  END LOOP get_list;
  
        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_Win_Malicious_X64`()
BEGIN
	DECLARE is_done INTEGER DEFAULT 0;
	DECLARE c_title varchar(2040)  DEFAULT "";
    DECLARE c_description varchar(2040)DEFAULT "";
	DECLARE c_udapeid varchar(2040)  DEFAULT "";
	DECLARE c_kb varchar(2040)  DEFAULT "";
	DECLARE c_revisionid varchar(2040)  DEFAULT "";
  DECLARE client_cursor CURSOR FOR  
	  SELECT 
		updateid, kb, revisionid, title, description
	FROM
		base_wsusscn2.update_data
	WHERE
		title LIKE '%Windows Malicious Software Removal Tool x64%' 
		and product like '%Windows 1%'
		ORDER BY revisionid DESC;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;
drop tables if exists `up_packages_Win_Malicious_X64`;
CREATE TABLE `up_packages_Win_Malicious_X64` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  `supersededby` varchar(2048),
  `creationdate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  `title_short` varchar(500),
  PRIMARY KEY (`updateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
  OPEN client_cursor;

  get_list: LOOP
  FETCH client_cursor INTO c_udapeid, c_kb,c_revisionid, c_title, c_description;
 
  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
SELECT CONCAT('%', c_revisionid, '%') INTO @rev;
SELECT CONCAT('%', c_kb, '%') INTO @kb;
INSERT IGNORE INTO `base_wsusscn2`.`up_packages_Win_Malicious_X64`
SELECT 
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    base_wsusscn2.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev; 
--        AND payloadfiles LIKE @kb
  END LOOP get_list;
  
        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `_add_new_remplace`(in uuid varchar(48), in c_supersedestxt varchar(2048) )
BEGIN

DECLARE supersedeselt VARCHAR(4096) default "";
DECLARE c_TITLE VARCHAR(4096) default "";
DECLARE c_supersedes VARCHAR(4096) default "";
select TRIM(c_supersedestxt) into c_supersedes;
-- faire tant que uuid dans c_supersedes
 WHILE ( (LENGTH(TRIM(c_supersedes)) >= 36) and (SELECT SUBSTR(TRIM(c_supersedes), 9 ,1 ) = "-") ) do
 -- select c_supersedes, LENGTH(TRIM(c_supersedes));
	select "" into supersedeselt;
    -- 1er element dans supersedeselt
	SELECT SUBSTRING_INDEX(c_supersedes , ',', 1 ) into supersedeselt;
    -- on retire cet element de la chaine
    SELECT SUBSTR(c_supersedes, LENGTH(supersedeselt)+2 ) into c_supersedes;
    if LENGTH(TRIM(supersedeselt)) = 36 then
       -- select TRIM(c_supersedes) into c_supersedes;
         -- if supersedeselt != "" and TRIM(uuid) != "" then
			SELECT title FROM base_wsusscn2.update_data WHERE updateid LIKE supersedeselt INTO c_TITLE;			
			if TRIM(c_TITLE) != "" then
					INSERT IGNORE INTO `base_wsusscn2`.`data_supersedes` (`updateid`, `title`) 	VALUES (uuid, c_TITLE);
			-- end if;
         end if;
    else
      select "" into c_supersedes ;
	end if;
	     END WHILE;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-10-20 17:14:25
