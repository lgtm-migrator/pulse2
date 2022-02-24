<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("List Backups by Client", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$type_backup = htmlspecialchars($_GET["backuptype"]);
$client_id = htmlspecialchars($_GET["clientid"]);

if ($type_backup == "incremental")
    $backup = xmlrpc_create_backup_incremental_file($client_id);
else
    $backup = xmlrpc_create_backup_full_file($client_id);

print_r($backup);
?>