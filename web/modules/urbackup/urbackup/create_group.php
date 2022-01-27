<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("Group creation", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$groupname = isset($_POST['groupname']);
print_r($groupname);
$create_group = xmlrpc_add_group($groupname);

print_r($create_group);
?>