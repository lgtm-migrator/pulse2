<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("Client machine list", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$client_array = xmlrpc_get_clients();
$clients = $client_array["navitems"]["clients"];

echo '<br>';
echo '<br>';
echo "<table style:'border: 1px solid #333;'>";
echo '    <thead>';
echo '        <tr>';
echo '            <th colspan="3">'._T("Clients", 'urbackup').'</th>';
echo '        </tr>';
echo '    </thead>';
echo '    <tbody>';
echo '        <tr>';
echo "            <td style='padding:0px 500px 0px 0px;'>"._T("Clients name", 'urbackup')."</td>";
echo '            <td>'._T("Group", 'urbackup').'</td>';
echo '            <td>'._T("Online state", 'urbackup').'</td>';
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
?>
