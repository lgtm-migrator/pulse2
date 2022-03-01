
<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$group_id = htmlspecialchars($_GET["groupid"]);

$p = new PageGenerator(_T("Delete group", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$group_deleted = xmlrpc_remove_group($group_id);
?>
<br>
<?php

$url = 'main.php?module=urbackup&submod=urbackup&action=usersgroups';

header("Location: ".$url);
?>