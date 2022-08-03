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


$start_backup = $backup["result"];
?>
<br>
<?php
foreach($start_backup as $back)
{
    if ($back["start_ok"] == "1")
    {
        $url = 'main.php?module=urbackup&submod=urbackup&action=index&clientid='.$client_id;
        header("Location: ".$url);  
    }
    else
    {
        $backupstate = "false";
        $url = 'main.php?module=urbackup&submod=urbackup&action=list_backups&clientid='.$client_id."&backupstate=".$backupstate."&backuptype=".$type_backup;
        header("Location: ".$url);  
    }
}
?>