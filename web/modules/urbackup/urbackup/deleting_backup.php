<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$clientid = htmlspecialchars($_GET["clientid"]);
$backupid = htmlspecialchars($_GET["backupid"]);

$p = new PageGenerator(_T("Delete backup", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$backup_deleted = xmlrpc_delete_backup($clientid, $backupid);
?>
<br>
<?php

$url = 'main.php?module=urbackup&submod=urbackup&action=list_backups&clientid='.$clientid;

header("Location: ".$url);
?>