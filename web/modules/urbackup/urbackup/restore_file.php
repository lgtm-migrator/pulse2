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
$filename = htmlspecialchars($_GET["filename"]);
?>
<br>
<?php
if ($shahash == "")
{
    $client_restore_file = xmlrpc_client_download_backup_file($client_id, $backup_id, $path, $filename);
    if ($client_restore_file["ok"] == "true")
        print_r(_T("Backup folder request successfully asked to client.", "urbackup"));
    else
        print_r(_T("Backup error, please try again, check if client exist or is online.","urbackup"));
}
else
{
    $client_restore_file_shahash = xmlrpc_client_download_backup_file_shahash($client_id, $backup_id, $path, $shahash);
    if ($client_restore_file["ok"] == "true")
        print_r(_T("Backup file(s) request successfully asked to client.", "urbackup"));
    else
        print_r(_T("Backup error, please try again, check if client exist or is online.","urbackup"));
}

?>