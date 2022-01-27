<?php
require("graph/navbar.inc.php");
require("localSidebar.php");
require_once("modules/urbackup/includes/xmlrpc.php");

$p = new PageGenerator(_T("Clients machine list", 'urbackup'));
$p->setSideMenu($sidemenu);
$p->display();

$client_array = xmlrpc_get_status();
$clients = $client_array["status"];
?>
<br>
<br>
<table style:'border: 1px solid #333;'>
    <thead>
        <tr style='text-align: left; text-decoration: underline;'>
          <th> <?php echo _T("Name", 'urbackup'); ?> </th>
          <th> <?php echo _T("Group", 'urbackup'); ?> </th>
          <th> <?php echo _T("OS", 'urbackup'); ?> </th>
          <th> <?php echo _T("IP", 'urbackup'); ?> </th>
          <th> <?php echo _T("Online state", 'urbackup'); ?> </th>
        </tr>
    </thead>
    <tbody>
<?php
foreach ($clients as $client) {
    if ($client['groupname'] != "")
    {
        $group = $client['groupname'];
    }
    else
    {
        $group = _T("No group", 'urbackup');
    }
?>
        <tr>
            <td style='padding:0px 500px 0px 0px;'> <?php echo $client['name']; ?></td>
            <td> <?php echo $group; ?></td>
            <td> <?php echo $client['os_simple']; ?></td>
            <td> <?php echo $client['ip']; ?></td>
            <td> <?php echo $client['online']; ?></td>
        </tr>
<?php
}
?>
    </tbody>
</table>
