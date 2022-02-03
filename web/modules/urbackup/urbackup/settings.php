<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("Settings", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$settings_global = xmlrpc_get_settings_global();

//OtherSettings sa=other
?>