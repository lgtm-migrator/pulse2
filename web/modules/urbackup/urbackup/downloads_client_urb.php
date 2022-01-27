<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("Télécharger le client Windows", 'pkgs'));
$p->setSideMenu($sidemenu);
$p->display();
$link_windows = "https://hndl.urbackup.org/Client/2.4.11/UrBackup%20Client%202.4.11.exe";

echo '<h1>User session :</h1>';
echo '<pre>';
print_r(xmlrpc_get_session());
echo '</pre>';
echo "Windows client : <button><a href='$link_windows' target='_blank'>Download</a></button>";
echo '</br>';
echo '<p>Linux Client : Run command :</p>';
echo '<p>TF=$(mktemp) && wget "https://hndl.urbackup.org/Client/2.4.11/UrBackup%20Client%20Linux%202.4.11.sh" -O $TF && sudo sh $TF; rm -f $TF</p>';
?>