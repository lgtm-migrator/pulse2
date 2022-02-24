<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("List Backups by Client", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$type_backup = htmlspecialchars($_GET["backuptype"]);
$client_id = htmlspecialchars($_GET["clientid"]);

$client_id = htmlspecialchars($_GET["clientid"]);

?>