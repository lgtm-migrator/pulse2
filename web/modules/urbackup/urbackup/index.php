<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("Clients machine list", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$client_array = xmlrpc_get_clients();
$clients = $client_array["navitems"]["clients"];
?>
<br>
<br>
<table style:'border: 1px solid #333;'>
    <thead>
        <tr style='text-align: left; text-decoration: underline;'>
          <th> <?php echo _T("Name", 'urbackup'); ?> </th>
          <th> <?php echo _T("Group", 'urbackup'); ?> </th>
          <th> <?php echo _T("Online state", 'urbackup'); ?> </th>
        </tr>
    </thead>
    <tbody>
<?php 
foreach ($clients as $client) {
?>
        <tr>
            <td style='padding:0px 500px 0px 0px;'> <?php echo $client['name']; ?></td>
            <td> <?php echo $client['groupname']; ?></td>
            <td>-</td>
        </tr>
<?php
}
?>
    </tbody>
</table>

<?php
print_r(xmlrpc_get_status());
?>
