<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$clientname = htmlspecialchars($_GET["cn"]);
$jidMachine = htmlspecialchars($_GET["jid"]);

$p = new PageGenerator(_T("Check if ".$clientname." exist", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$clients = xmlrpc_get_backups_all_client();
$clients = $clients["clients"];

foreach ($clients as $client)
{
    if ($client["name"] == $clientname)
    {
        $exist = "true";
        $id = $client["id"];
    }
    else
        $exist = "false";
}
?>
<br>
<?php

$url = 'main.php?module=urbackup&submod=urbackup&action=list_backups&clientid='.$id;

if ($exist == "true")
{
    header("Location: ".$url);
    echo "<a href='main.php?module=urbackup&amp;submod=urbackup&amp;action=list_backups&amp;clientid=".$id."'>Go to user backups</a>";
}
else
{
    $create_client = xmlrpc_add_client($clientname);

    if ($create_client["already_exists"] == "1") 
    {
        print_r(_T("User already exists" ,"urbackup"));
        header("Location: ".$url);
    }
    else
    {
        print_r(_T("User created.", "urbackup"));
        $check_client = xmlrpc_check_client($jidMachine, $create_client["new_clientid"], $create_client["new_authkey"]);
    }
}
?>