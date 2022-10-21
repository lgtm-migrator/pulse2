<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/updates/includes/xmlrpc.php");

$p = new PageGenerator(_T("Updates test", 'pkgs'));
$p->setSideMenu($sidemenu);
$p->display();

$test = xmlrpc_tests();

echo '<pre>';
print_r($test);
echo '</pre>';
?>

