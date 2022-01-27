<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("UsersGroups", 'pkgs'));
$p->setSideMenu($sidemenu);
$p->display();

echo '<h1>Liste des utilisateurs et des groups : </h1>';
echo '<pre>';

echo '</pre>';

echo '<h2>Liste des utilisateurs et des groups : </h2>';
echo '<pre>';
$tableau = xmlrpc_get_clients();
echo '</pre>';

/*foreach($tableau as $key=>$value){
  echo $key."<br>";
  echo '<pre>';
  print_r($value);
  echo '</pre>';
}*/
?>
