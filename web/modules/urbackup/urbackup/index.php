<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("Client machine list", 'pkgs'));
$p->setSideMenu($sidemenu);
$p->display();

$tableau = xmlrpc_get_clients();
$clients = $tableau["navitems"]["clients"];

echo '<br>';
echo '<br>';
echo "<table style:'border: 1px solid #333;'>";
echo '    <thead>';
echo '        <tr>';
echo '            <th colspan="3">Client list</th>';
echo '        </tr>';
echo '    </thead>';
echo '    <tbody>';
echo '        <tr>';
echo "            <td style='padding:0px 500px 0px 0px;'>Client name</td>";
echo '            <td>Group</td>';
echo '            <td>Online</td>';
echo '        </tr>';

foreach ($clients as $client) {
  echo '        <tr>';
  echo "            <td style='padding:0px 500px 0px 0px;'>".$client['name']."</td>";
  echo '            <td>'.$client['groupname'].'</td>';
  echo '            <td>-</td>';
  echo '        </tr>';
}

echo '    </tbody>';
echo '</table>';
echo '<br>';
echo '<br>';

echo '--------------------';
echo '<br>';
echo '<br>';

echo 'Debug - CLIENTS Array';
echo '<br>';

print_r($clients);
?>
