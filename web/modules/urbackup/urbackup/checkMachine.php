<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("Check if machine exist", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$clientname = htmlspecialchars($_GET["cn"]);
$jidMachine = htmlspecialchars($_GET["jid"]);

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

print_r($exist);

if ($exist == "true")
{
    //$url = "main.php?module=urbackup&amp;submod=urbackup&amp;action=list_backups&amp;clientid=".$id;
    //header("Location: $url");
    echo "<a href='main.php?module=urbackup&amp;submod=urbackup&amp;action=list_backups&amp;clientid=".$id."'>OUAISS</a>";
}
else
{
    $create_client = xmlrpc_add_client($clientname, $jidMachine);
    print_r($create_client);
}
    
    

?>

<br>
<br>
<h1>CHECK MACHINE IF EXIST</h1>