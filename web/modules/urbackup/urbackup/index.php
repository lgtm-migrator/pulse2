<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("Liste des clients machine", 'pkgs'));
$p->setSideMenu($sidemenu);
$p->display();

echo '<h1>ID de la session utilisateur en cours : </h1>';
echo '<pre>';
$tableau = xmlrpc_get_clients();
echo '</pre>';

foreach($tableau as $key=>$value){
  echo $key."<br>";
  echo '<pre>';
  print_r($value);
  echo '</pre>';
}
?>
