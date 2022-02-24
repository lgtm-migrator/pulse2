<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$type_backup = htmlspecialchars($_GET["backuptype"]);
$client_id = htmlspecialchars($_GET["clientid"]);

$p = new PageGenerator(_T("Start ".$type_backup." backup", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

if ($type_backup == "incremental")
    $backup = xmlrpc_create_backup_incremental_file($client_id);
else
    $backup = xmlrpc_create_backup_full_file($client_id);

print_r($backup);
?>