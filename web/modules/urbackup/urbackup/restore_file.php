<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("Restore file", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$client_id = htmlspecialchars($_GET["clientid"]);
$backup_id = htmlspecialchars($_GET["backupid"]);
$volume_name = htmlspecialchars($_GET["volumename"]);
$shahash = htmlspecialchars($_GET["shahash"]);
$path = htmlspecialchars($_GET["beforepath"]);

print_r($client_id);
print_r($backup_id);
print_r($volume_name);

if ($shahash == "")
{
    $client_restore_file = xmlrpc_client_download_backup_file($client_id, $backup_id, $volume_name);
}
else
{
    $client_restore_file_shahash = xmlrpc_client_download_backup_file_shahash($client_id, $backup_id, $path, $shahash);
}

?>