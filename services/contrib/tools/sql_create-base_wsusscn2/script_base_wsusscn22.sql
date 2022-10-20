
CREATE DATABASE IF NOT EXISTS `` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;

USE `base_wsusscn2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `data_simple_update` (
  `updateid` varchar(38) NOT NULL COMMENT 'creationdate',
  `creationdate` datetime DEFAULT current_timestamp(),
  `updateclassification` text DEFAULT NULL,
  `category` text DEFAULT NULL,
  `title` text DEFAULT NULL,
  `description` text DEFAULT NULL,
  `kb` text DEFAULT NULL,
  `msrcseverity` text DEFAULT NULL,
  `msrcnumber` text DEFAULT NULL,
  PRIMARY KEY (`updateid`)
);
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `data_simple_update1` (
  `updateid` varchar(38) NOT NULL COMMENT 'creationdate',
  `creationdate` datetime DEFAULT current_timestamp(),
  `updateclassification` text DEFAULT NULL,
  `category` text DEFAULT NULL,
  `title` text DEFAULT NULL,
  `description` text DEFAULT NULL,
  `kb` text DEFAULT NULL,
  `msrcseverity` text DEFAULT NULL,
  `msrcnumber` text DEFAULT NULL,
  PRIMARY KEY (`updateid`)
);
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `data_supersedes` (
  `id` int(11) NOT NULL,
  `updateid` varchar(37) NOT NULL,
  `title` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniid` (`updateid`,`title`)
);
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `data_supersedes1` (
  `id` int(11) NOT NULL,
  `updateid` varchar(37) NOT NULL,
  `title` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniid` (`updateid`,`title`)
);
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `update_data` (
  `updateid` varchar(38) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `creationdate` timestamp NOT NULL DEFAULT current_timestamp(),
  `compagny` varchar(36) DEFAULT '',
  `product` varchar(512) DEFAULT '',
  `productfamily` varchar(100) DEFAULT '',
  `updateclassification` varchar(36) DEFAULT '',
  `prerequisite` varchar(2000) DEFAULT '',
  `title` varchar(500) DEFAULT '',
  `description` varchar(2048) DEFAULT '',
  `msrcseverity` varchar(16) DEFAULT '',
  `msrcnumber` varchar(16) DEFAULT '',
  `kb` varchar(16) DEFAULT '',
  `languages` varchar(16) DEFAULT '',
  `category` varchar(80) DEFAULT '',
  `supersededby` varchar(2048) DEFAULT '',
  `supersedes` text DEFAULT NULL,
  `payloadfiles` varchar(1024) DEFAULT '',
  `revisionnumber` varchar(30) DEFAULT '',
  `bundledby_revision` varchar(30) DEFAULT '',
  `isleaf` varchar(6) DEFAULT '',
  `issoftware` varchar(30) DEFAULT '',
  `deploymentaction` varchar(30) DEFAULT '',
  `title_short` varchar(500) DEFAULT '',
  PRIMARY KEY (`updateid`),
  UNIQUE KEY `id_UNIQUE` (`updateid`),
  UNIQUE KEY `id_UNIQUE1` (`revisionid`),
  KEY `indproduct` (`product`),
  KEY `indkb` (`kb`),
  KEY `indclassification` (`updateclassification`),
  KEY `ind_remplacerpar` (`supersededby`(768)),
  KEY `indcategory` (`category`)
);
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `update_data1` (
  `updateid` varchar(38) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `creationdate` timestamp NOT NULL DEFAULT current_timestamp(),
  `compagny` varchar(36) DEFAULT '',
  `product` varchar(1024) DEFAULT '',
  `productfamily` varchar(100) DEFAULT '',
  `updateclassification` varchar(36) DEFAULT '',
  `prerequisite` varchar(4096) DEFAULT '',
  `title` varchar(500) DEFAULT '',
  `description` varchar(4096) DEFAULT '',
  `msrcseverity` varchar(16) DEFAULT '',
  `msrcnumber` varchar(16) DEFAULT '',
  `kb` varchar(16) DEFAULT '',
  `languages` varchar(16) DEFAULT '',
  `category` varchar(128) DEFAULT '',
  `supersededby` varchar(3072) DEFAULT '',
  `supersedes` text DEFAULT NULL,
  `payloadfiles` varchar(2048) DEFAULT '',
  `revisionnumber` varchar(30) DEFAULT '',
  `bundledby_revision` varchar(30) DEFAULT '',
  `isleaf` varchar(6) DEFAULT '',
  `issoftware` varchar(30) DEFAULT '',
  `deploymentaction` varchar(30) DEFAULT '',
  `title_short` varchar(500) DEFAULT '',
  PRIMARY KEY (`updateid`),
  UNIQUE KEY `id_UNIQUE` (`updateid`),
  UNIQUE KEY `id_UNIQUE1` (`revisionid`),
  KEY `indproduct` (`product`(768)),
  KEY `indkb` (`kb`),
  KEY `indclassification` (`updateclassification`),
  KEY `ind_remplacerpar` (`supersededby`(768)),
  KEY `indcategory` (`category`)
);
/*!40101 SET character_set_client = @saved_cs_client */;
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
            title REGEXP ('^[0-9]{4}-[0-9]{2} .*\(kB[0-9]{7}\)$')));
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
